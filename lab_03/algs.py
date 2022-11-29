from collections.abc import Sequence
from random import randint


def generate_tabular(count, low=0, high=100):
    seq = []
    with open("table.txt") as file:
        for line in file:
            for curr in line.split(" ")[1:]:
                if len(seq) < count and curr != "":
                    seq.append(low + int(curr) % (high - low))
            if len(seq) >= count:
                break
    return seq


def __setup_linear_congruent():
    m = randint(100000, 1000000)
    a = randint(10000, 100000)
    c = randint(10000, 100000)
    x0 = randint(10000, 100000)
    return 312500, 36261, 66037, 60000


def generate_linear_congruent(
    count: int, low: int = 0, high: int = 100
) -> Sequence[int]:
    m, a, c, x0 = __setup_linear_congruent()

    seq: list[int] = [x0]
    for i in range(1, count + 1):
        curr = (seq[i - 1] * a + c) % m
        seq.append(low + curr % (high - low))

    return seq[1:]


def __slice(seq: Sequence[int], step: int) -> Sequence[int]:
    return [abs(seq[i] - seq[i + step]) for i in range(0, len(seq) - step, 1)]


def __unique_qty(seq: Sequence[int]) -> float:
    return (len(set(seq)) - 1) / len(seq)


def approve_sequence(seq: Sequence[int]) -> float:
    res = [__unique_qty(__slice(seq, step)) for step in range(1, len(seq) - 1)]
    return sum(res) / len(res)
