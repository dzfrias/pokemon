from functools import total_ordering


@total_ordering
class Cooldown:
    cooldowns = []

    def __init__(self, reset_val: int, *, auto_reset=False, zero_start=True,
                 func=None, auto_update=True):
        if auto_update:
            Cooldown.cooldowns.append(self)
        self.value = reset_val if not zero_start else 0
        self.auto_reset = auto_reset
        self.reset_val = reset_val
        self.func = func

    def reset(self, reset_val=None, *, call_func=True):
        if reset_val is None:
            self.value = self.reset_val
        else:
            self.value = reset_val
        if self.func is not None and call_func:
            self.func()

    def update(self):
        if self.value:
            self.value -= 1
        elif self.auto_reset:
            self.reset()

    def __int__(self):
        return int(self.value)

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

