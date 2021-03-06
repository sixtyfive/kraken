# -*- coding: utf-8 -*-
#
# Copyright 2015 Benjamin Kiessling
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.
"""
Training loop interception helpers
"""
import abc

from torch.utils import data
from collections.abc import Iterable


class TrainStopper(Iterable):

    def __init__(self):
        self.best_loss = 0.0
        self.best_epoch = 0

    @abc.abstractmethod
    def update(self, val_loss: float) -> None:
        """
        Updates the internal state of the train stopper.
        """
        pass


class EarlyStopping(TrainStopper):
    """
    Early stopping to terminate training when validation loss doesn't improve
    over a certain time.
    """
    def __init__(self, it: data.DataLoader = None, min_delta: float = 0.002, lag: int = 5) -> None:
        """
        Args:
            it (torch.utils.data.DataLoader): training data loader
            min_delta (float): minimum change in validation loss to qualify as improvement.
            lag (int): Number of epochs to wait for improvement before
                       terminating.
        """
        super().__init__()
        self.min_delta = min_delta
        self.lag = lag
        self.it = it
        self.wait = 0
        self.epoch = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.wait >= self.lag:
            raise StopIteration
        self.epoch += 1
        return self.it

    def update(self, val_loss: float) -> None:
        """
        Updates the internal validation loss state
        """
        if (val_loss - self.best_loss) < self.min_delta:
            self.wait += 1
        else:
            self.wait = 0
            self.best_loss = val_loss
            self.best_epoch = self.epoch


class EpochStopping(TrainStopper):
    """
    Dumb stopping after a fixed number of epochs.
    """
    def __init__(self, it: data.DataLoader = None, epochs: int = 100) -> None:
        """
        Args:
            it (torch.utils.data.DataLoader): training data loader
            epochs (int): Number of epochs to train for
        """
        super().__init__()
        self.epochs = epochs
        self.epoch = 0
        self.it = it

    def __iter__(self):
        return self

    def __next__(self):
        if self.epoch< self.epochs:
            self.epoch += 1
            return self.it
        else:
            raise StopIteration

    def update(self, val_loss: float) -> None:
        """
        Only update internal best epoch
        """
        if val_loss > self.best_loss:
            self.best_loss = val_loss
            self.best_epoch = self.epoch - 1
