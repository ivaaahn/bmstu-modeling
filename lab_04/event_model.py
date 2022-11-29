from dataclasses import dataclass
from enum import Enum, auto
from random import randint

from distributions import IGenerator, IProcessor


class EventType(Enum):
    GEN = auto()
    PROC = auto()


@dataclass(slots=True, frozen=True)
class Event:
    time: float
    type: EventType


class EventsFlow:
    def __init__(self, init_data: list[Event] | None = None) -> None:
        self._items: list[Event] = []
        if init_data:
            self._items.extend(init_data)

    def add(self, event: Event) -> None:
        pos = 0

        while pos < len(self._items) and event.time > self._items[pos].time:
            pos += 1

        if pos < len(self._items):
            self._items.insert(pos - 1, event)
        else:
            self._items.append(event)

    def get(self) -> Event:
        return self._items.pop(0)


class EventModel:
    def __init__(
        self,
        generator: IGenerator,
        processor: IProcessor,
        total_tasks_qty: int = 0,
        repeat_percent: float = 0.0,
    ) -> None:
        self._processed_tasks_qty = 0
        self._curr_queue_len = 0
        self._max_queue_len = 0
        self._total_tasks_qty = total_tasks_qty
        self._repeat_percent = repeat_percent
        self._generator = generator
        self._processor = processor
        self._events_flow = EventsFlow(
            init_data=[Event(generator.generate(), EventType.GEN)]
        )
        self._is_free = True
        self._is_processing = False

    def _handle_gen_event(self, event: Event) -> None:
        self._curr_queue_len += 1
        self._max_queue_len = max(self._max_queue_len, self._curr_queue_len)
        self._events_flow.add(
            Event(event.time + self._generator.generate(), EventType.GEN)
        )

        if self._is_free:
            self._is_processing = True

    def _handle_proc_event(self) -> None:
        self._processed_tasks_qty += 1
        if randint(1, 100) <= self._repeat_percent:
            self._curr_queue_len += 1
        self._is_processing = True

    def run(self):
        while self._processed_tasks_qty < self._total_tasks_qty:
            event: Event = self._events_flow.get()
            match event.type:
                case EventType.GEN:
                    self._handle_gen_event(event)
                case EventType.PROC:
                    self._handle_proc_event()

            if self._is_processing:
                if self._curr_queue_len <= 0:
                    self._is_free = True
                else:
                    self._curr_queue_len -= 1
                    self._events_flow.add(
                        Event(
                            event.time + self._processor.process(),
                            EventType.PROC,
                        )
                    )
                    self._is_free = False
                self._is_processing = False
        return self._max_queue_len
