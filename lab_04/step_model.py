import random

from distributions import IProcessor, IGenerator


class StepModel:
    def __init__(
        self,
        generator: IGenerator,
        processor: IProcessor,
        total_tasks_qty: int = 0,
        repeat_percent: float = 0.0,
        step=0.001,
    ) -> None:
        self._generator = generator
        self._processor = processor
        self._total_tasks_qty = total_tasks_qty
        self._repeat_qty = repeat_percent
        self._step = step
        self._curr_queue_len = 0
        self._max_queue_len = 0
        self._processed_tasks = 0

        self._t_curr = self._step

        self._t_gen = self._generator.generate()
        self._t_gen_prev = 0

        self._t_proc = 0

        self._is_free = True

    def _handle_generator(self) -> None:
        self._curr_queue_len += 1

        self._max_queue_len = max(self._max_queue_len, self._curr_queue_len)

        self._t_gen_prev = self._t_gen
        self._t_gen += self._generator.generate()

    def _handle_processing(self) -> None:
        if self._curr_queue_len <= 0:
            self._is_free = True
            return

        was_free = self._is_free

        if self._is_free:
            self._is_free = False
        else:
            self._processed_tasks += 1
            if random.randint(1, 100) <= self._repeat_qty:
                self._curr_queue_len += 1

        self._curr_queue_len -= 1

        if was_free:
            self._t_proc = self._t_gen_prev + self._processor.process()
        else:
            self._t_proc += self._processor.process()

    def run(self) -> int:
        while self._processed_tasks < self._total_tasks_qty:
            if self._t_curr > self._t_gen:
                self._handle_generator()

            if self._t_curr > self._t_proc:
                self._handle_processing()

            self._t_curr += self._step

        return self._max_queue_len
