import random
from abc import ABC, abstractmethod

from numpy.random import exponential


class IGenerator(ABC):
    @abstractmethod
    def generate(self) -> float:
        raise NotImplementedError


class IProcessor(ABC):
    @abstractmethod
    def process(self) -> float:
        raise NotImplementedError


class UniformGenerator(IGenerator):
    def __init__(self, a: float, b: float) -> None:
        self._a = a
        self._b = b

    def generate(self) -> float:
        return self._a + (self._b - self._a) * random.random()


class ExponentialProcessor(IProcessor):
    def __init__(self, lambda_: float) -> None:
        self._lambda = lambda_

    def process(self) -> float:
        return exponential(1 / self._lambda)
