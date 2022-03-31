from dataclasses import dataclass, field
from typing import Callable


@dataclass(order=True)
class Cooldown:
    reset_val: int
    auto_reset: bool = field(kw_only=True, compare=False, default=False)
    func: Callable = field(kw_only=True, compare=False, default=None)
    args: tuple = field(kw_only=True, compare=False, default=())

    def __post_init__(self):
        self.value = 0

    def reset(self, reset_val=None, *, call_func=True):
        if reset_val is None:
            self.value = self.reset_val
        else:
            self.value = reset_val
        if self.func is not None and call_func:
            self.func(*self.args)

    def update(self):
        if self.value:
            self.value -= 1
        elif self.auto_reset:
            self.reset()

    def __int__(self):
        return int(self.value)

    def __bool__(self):
        return bool(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value}, reset_val={self.reset_val})"

