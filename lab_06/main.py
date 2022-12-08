import itertools
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum, auto
from random import choices, uniform
from time import time
from queue import Queue

import click
from numpy.random import normal

TIME_UNIT = 0.01  # minutes
CURRENT_TIME = 0.0
DELTA = 1e-5


class ProcessResult(Enum):
    FINISHED = auto()
    ACCEPTED = auto()
    PASSED = auto()


class OrderKind(Enum):
    ECONOMY = auto()
    COMFORT = auto()


class Order:
    _idx_generator = itertools.count(start=0)

    def __init__(self, kind: OrderKind):
        self.id = next(self._idx_generator)
        self.kind = kind
        self.created_at = CURRENT_TIME
        self.process_started_at: float | None = None

    def __repr__(self) -> str:
        return f"<{self.id}: {round(CURRENT_TIME - self.created_at, 2)}>"


class TimeGenerator:
    _distribution: Callable[..., float]

    def __init__(self, value: float, *, delta: float = 0.0):
        self._value = value
        self._delta = delta

    def generate(self) -> float:
        return self._distribution(
            self._value - self._delta, self._value + self._delta
        )


class NormalTimeGenerator(TimeGenerator):
    _distribution = normal


class UniformTimeGenerator(TimeGenerator):
    _distribution = uniform


class Car:
    GEN_VALUE: int
    GEN_DELTA: int

    def __init__(self, requests_queue: Queue[Order]):
        self._time_generator = NormalTimeGenerator(
            self.GEN_VALUE, delta=self.GEN_DELTA
        )
        self._is_busy = False
        self._requests_queue = requests_queue
        self._curr_order: Order | None = None
        self._time_left: float | None = None

        self._last_order: Order | None = None

    @property
    def last_order(self) -> Order | None:
        return self._last_order

    def _finish_processing(self) -> None:
        self._is_busy = False
        self._last_order = self._curr_order
        self._curr_order = None

    def _get_accept_order(self) -> None:
        self._curr_order = self._requests_queue.get()
        self._curr_order.process_started_at = CURRENT_TIME
        self._time_left = self._time_generator.generate()
        self._is_busy = True

    def process(self) -> ProcessResult:
        if not self._is_busy and not self._requests_queue.empty():
            self._get_accept_order()
            return ProcessResult.ACCEPTED

        if not self._is_busy:
            return ProcessResult.PASSED

        if self._time_left > DELTA:
            self._time_left -= TIME_UNIT
            return ProcessResult.PASSED

        self._finish_processing()
        return ProcessResult.FINISHED


class EcoCar(Car):
    GEN_VALUE = 25
    GEN_DELTA = 10


class ComfortCar(Car):
    GEN_VALUE = 30
    GEN_DELTA = 5


class Operator:
    GEN_VALUE = 1

    def __init__(
        self,
        input_queue: Queue[Order],
        eco_queue: Queue[Order],
        comfort_queue: Queue[Order],
    ) -> None:
        self._input_queue = input_queue

        self._order_map = {
            OrderKind.COMFORT: comfort_queue,
            OrderKind.ECONOMY: eco_queue,
        }

        self._time_generator = NormalTimeGenerator(self.GEN_VALUE)
        self._is_busy: bool = False
        self._curr_order: Order | None = None
        self._time_left_to_route = 0.0

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @property
    def is_free(self) -> bool:
        return not self._is_busy

    def accept(self):
        self._is_busy = True
        self._curr_order = self._input_queue.get()
        self._time_left_to_route = self._time_generator.generate()

    def _finish(self):
        self._order_map[self._curr_order.kind].put(self._curr_order)
        self._is_busy = False
        self._curr_order = None

    def process(self) -> ProcessResult:
        if not self._is_busy and not self._input_queue.empty():
            self.accept()
            return ProcessResult.ACCEPTED

        if not self._is_busy:
            return ProcessResult.PASSED

        if self._time_left_to_route < DELTA:
            self._finish()
            return ProcessResult.FINISHED

        self._time_left_to_route -= TIME_UNIT
        return ProcessResult.PASSED


class OrderFactory:
    ORDER_KINDS = (OrderKind.ECONOMY, OrderKind.COMFORT)

    def __init__(
        self,
        queue: Queue[Order],
        avg_time: float,
        delta: float,
        eco_ratio: int,
        comfort_ratio: int,
    ) -> None:
        self._orders_created = 0
        self._queue = queue
        self._order_kinds_weights = (eco_ratio, comfort_ratio)
        self._time_generator = UniformTimeGenerator(avg_time, delta=delta)
        self._time_left_to_create: float = self._time_generator.generate()

    @property
    def created_qty(self) -> int:
        return self._orders_created

    @property
    def time_is_up(self) -> bool:
        return self._time_left_to_create < DELTA

    def _decrement_time(self) -> None:
        self._time_left_to_create -= TIME_UNIT

    def _make_order(self) -> Order:
        return Order(
            kind=choices(
                self.ORDER_KINDS, weights=self._order_kinds_weights, k=1
            )[0]
        )

    def create(self) -> None:
        if self.time_is_up:
            self._queue.put(self._make_order())
            self._orders_created += 1

        self._decrement_time()


class Model:
    CRITICAL_TIME = 15

    def __init__(
        self,
        order_factory: OrderFactory,
        operators: Iterable[Operator],
        eco_queue: Queue[Order],
        eco_cars: Iterable[EcoCar],
        comfort_queue: Queue[Order],
        comfort_cars: Iterable[ComfortCar],
        total_incoming_requests: int,
    ) -> None:
        self._order_factory = order_factory
        self._operators = operators

        self._eco_queue = eco_queue
        self._comfort_queue = comfort_queue

        self._eco_cars = eco_cars
        self._comfort_cars = comfort_cars

        self.orders_expected_qty = total_incoming_requests

        self._orders_finished = 0
        self._orders_lost = 0

        self._max_size_input = 0
        self._max_size_eco = 0
        self._max_size_comfort = 0
        self._wasted_time = 0
        self._summary_waiting_time = 0
        self._min_waiting_time = 1e3
        self._max_waiting_time = 0

    @property
    def min_waiting_time(self) -> float:
        return self._min_waiting_time

    @property
    def max_waiting_time(self) -> float:
        return self._max_waiting_time

    @property
    def summary_waiting_time(self) -> float:
        return self._summary_waiting_time

    @property
    def orders_lost(self) -> int:
        return self._orders_lost

    @property
    def wasted_time(self) -> float:
        return self._wasted_time

    @property
    def cars(self) -> Iterable[Car]:
        return itertools.chain(self._eco_cars, self._comfort_cars)

    def run(self) -> None:
        global CURRENT_TIME
        time_start = time()

        factory = self._order_factory
        while self._orders_finished < self.orders_expected_qty:
            self._max_size_eco = max(
                self._max_size_eco, self._eco_queue.qsize()
            )
            self._max_size_comfort = max(
                self._max_size_comfort, self._comfort_queue.qsize()
            )
            self._max_size_input = max(
                self._max_size_eco, self._order_factory._queue.qsize()
            )

            CURRENT_TIME += TIME_UNIT

            if factory.created_qty < self.orders_expected_qty:
                self._order_factory.create()

            self._update_operators()
            self._update_processors()

        print(
            f"""
    =============================
    Created: {factory.created_qty}
    Finished: {self._orders_finished}
    Time: {round(CURRENT_TIME, 2)}

    input: {self._max_size_input}
    eco: {self._max_size_eco}
    comfort: {self._max_size_comfort}

    """
        )

        self._wasted_time = time() - time_start

    def _update_operators(self) -> None:
        for operator in self._operators:
            operator.process()

    def _update_processors(self) -> None:
        for car in self.cars:
            process_result = car.process()
            if process_result is ProcessResult.FINISHED:
                self._orders_finished += 1

                order = car.last_order

                waiting_time = order.process_started_at - order.created_at
                self._summary_waiting_time += waiting_time

                self._min_waiting_time = min(self.min_waiting_time, waiting_time)
                self._max_waiting_time = max(self.max_waiting_time, waiting_time)

                if waiting_time > self.CRITICAL_TIME:
                    self._orders_lost += 1


@dataclass(slots=True, frozen=True)
class Config:
    requests_qty: int
    eco_cars_qty: int
    comfort_cars_qty: int
    eco_ratio: int
    comfort_ratio: int
    operators_qty: int


def main() -> None:
    config = Config(
        int(os.environ.get("REQUESTS", default=200)),
        int(os.environ.get("ECO_CARS", default=100)),
        int(os.environ.get("COMFORT_CARS", default=50)),
        int(os.environ.get("ECO_RATIO", default=80)),
        int(os.environ.get("COMFORT_RATIO", default=20)),
        int(os.environ.get("OPERATORS_QTY", default=10)),
    )

    eco_queue: Queue[Order] = Queue()
    comfort_queue: Queue[Order] = Queue()
    orders_queue: Queue[Order] = Queue()

    eco_cars = tuple(EcoCar(eco_queue) for _ in range(config.eco_cars_qty))
    comfort_cars = tuple(
        ComfortCar(comfort_queue) for _ in range(config.comfort_cars_qty)
    )

    operators = tuple(
        Operator(
            input_queue=orders_queue,
            eco_queue=eco_queue,
            comfort_queue=comfort_queue,
        )
        for _ in range(config.operators_qty)
    )

    order_factory = OrderFactory(
        avg_time=30,
        delta=20,
        eco_ratio=config.eco_ratio,
        comfort_ratio=config.comfort_ratio,
        queue=orders_queue,
    )

    model = Model(
        order_factory=order_factory,
        operators=operators,
        eco_queue=eco_queue,
        eco_cars=eco_cars,
        comfort_queue=comfort_queue,
        comfort_cars=comfort_cars,
        total_incoming_requests=config.requests_qty,
    )
    model.run()

    print()
    click.secho(
        f"Процент превышений нормы ожидания подачи: {round(model.orders_lost / config.requests_qty *100, 2)}\n"
        f"Максимальное время подачи: {round(model.max_waiting_time,2)}\n"
        f"Среднее время подачи {round(model.summary_waiting_time / config.requests_qty, 2)}",
        bg="red",
        bold=True,
    )


if __name__ == "__main__":
    main()
