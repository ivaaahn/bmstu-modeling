import itertools
from enum import Enum, auto
from random import uniform
from time import time
from queue import Queue

import click

SYS_TIME_UNIT = 0.01  # minutes
DELTA = 1e-5


class ProcessResult(Enum):
    FINISHED = auto()
    RECEIVED = auto()
    PASSED = auto()


class Request:
    _idx_generator = itertools.count(start=0)

    def __init__(self):
        self.id = next(self._idx_generator)


class Distribution:
    def __init__(self, value: float, *, delta: float = 0.0):
        self._value = value
        self._delta = delta

    def get_time(self) -> float:
        if self._delta == 0.0:
            return self._value

        return uniform(self._value - self._delta, self._value + self._delta)


class Computer:
    def __init__(
        self, requests_queue: Queue[Request], distribution: Distribution
    ):
        self._work_time_distribution = distribution
        self._is_busy = False
        self._requests_queue = requests_queue
        self._current_request: Request | None = None
        self._time_left: float | None = None

    def _finish_processing(self) -> None:
        self._is_busy = False
        self._current_request = None

    def _get_request(self) -> None:
        self._current_request = self._requests_queue.get()
        self._time_left = self._work_time_distribution.get_time()
        self._is_busy = True

    def continue_processing(self) -> ProcessResult:
        if not self._is_busy and not self._requests_queue.empty():
            self._get_request()
            return ProcessResult.RECEIVED

        if not self._is_busy:
            return ProcessResult.PASSED

        if self._time_left > DELTA:
            self._time_left -= SYS_TIME_UNIT
            return ProcessResult.PASSED

        self._finish_processing()
        return ProcessResult.FINISHED


class Operator:
    def __init__(
        self, queue_send_to: Queue[Request], distribution: "Distribution"
    ):
        self._work_time_distribution = distribution
        self._is_busy: bool = False
        self._queue_send_to = queue_send_to
        self._current_request: Request | None = None
        self._time_left: float | None = None

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @property
    def is_free(self) -> bool:
        return not self._is_busy

    def accept(self, request: "Request"):
        self._is_busy = True
        self._current_request = request
        self._time_left = self._work_time_distribution.get_time()

    def _finish(self):
        self._queue_send_to.put(self._current_request)
        self._is_busy = False
        self._current_request = None

    def continue_processing(self) -> ProcessResult:
        if not self._is_busy:
            return ProcessResult.PASSED

        if self._time_left > DELTA:
            self._time_left -= SYS_TIME_UNIT
            return ProcessResult.PASSED

        self._finish()
        return ProcessResult.FINISHED


class RequestGenerator:
    def __init__(self, distribution: Distribution):
        self._work_time_distribution = distribution
        self._time_left: float | None = None

    def generate(self) -> Request | None:
        if self._time_left and self._time_left > DELTA:
            self._time_left -= SYS_TIME_UNIT
            return None

        self._time_left = self._work_time_distribution.get_time()
        return Request()


class Model:
    def __init__(
        self,
        requests_generator: RequestGenerator,
        operators: tuple[Operator, Operator, Operator],
        computers: tuple[Computer, Computer],
        total_incoming_requests: int,
    ) -> None:
        self._request_generator = requests_generator
        self._operators = operators
        self._computers = computers
        self._total_incoming_requests = total_incoming_requests

        self._requests_generated = 0
        self._requests_processed = 0
        self._requests_lost = 0

        self._wasted_time = 0

    @property
    def requests_lost(self) -> int:
        return self._requests_lost

    @property
    def wasted_time(self) -> float:
        return self._wasted_time

    def run(self) -> None:
        time_start = time()
        while not self._is_all_requests_processed():
            if self._requests_generated < self._total_incoming_requests:
                self._generate_and_route_request()
            self._handle_one_tick()

        time_end = time()
        self._wasted_time = time_end - time_start

    def _is_all_requests_processed(self):
        return (
            self._requests_lost + self._requests_processed
            >= self._total_incoming_requests
        )

    def _generate_and_route_request(self):
        request = self._request_generator.generate()
        if request:
            self._requests_generated += 1
            self._route_request(request)

    def _route_request(self, request: Request) -> None:
        if operator := self._find_free_operator(self._operators):
            operator.accept(request)
        else:
            self._requests_lost += 1

    def _find_free_operator(
        self, operators: tuple[Operator, Operator, Operator]
    ) -> Operator | None:
        for operator in operators:
            if operator.is_free:
                return operator
        return None

    def _handle_one_tick(self) -> None:
        self._update_operators()
        self._update_processors()

    def _update_operators(self) -> None:
        for operator in self._operators:
            operator.continue_processing()

    def _update_processors(self) -> None:
        for computer in self._computers:
            process_result = computer.continue_processing()
            if process_result is ProcessResult.FINISHED:
                self._requests_processed += 1


@click.command()
@click.option(
    "-requests",
    required=False,
    default=300,
    help="Общее количество заявок",
)
def main(requests: int) -> None:
    queues: tuple[Queue[Request], Queue[Request]] = Queue(), Queue()
    operators: tuple[Operator, Operator, Operator] = (
        Operator(queues[0], Distribution(20, delta=5)),
        Operator(queues[0], Distribution(40, delta=10)),
        Operator(queues[1], Distribution(40, delta=20)),
    )
    computers: tuple[Computer, Computer] = (
        Computer(queues[0], Distribution(15)),
        Computer(queues[1], Distribution(30)),
    )

    model = Model(
        requests_generator=RequestGenerator(Distribution(10, delta=2)),
        operators=operators,
        computers=computers,
        total_incoming_requests=requests,
    )
    model.run()

    print()
    click.secho(
        f"Вероятность потери: {round(model.requests_lost / requests, 2)}",
        bg="red",
        bold=True,
    )


if __name__ == "__main__":
    main()
