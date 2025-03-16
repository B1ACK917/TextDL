import random


class BinaryRollBack:
    def __init__(self, n) -> None:
        self._time_slots = [2 ** i for i in range(1, n)]

    def select(self, n):
        return random.randint(1, self._time_slots[n] + 1)


class SequenceRollBack:
    def __init__(self, n) -> None:
        self._time_slots = list(range(1, n + 1))

    def select(self, n):
        return random.randint(1, self._time_slots[n] + 1)
