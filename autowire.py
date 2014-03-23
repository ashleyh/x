from functools import partial
import inspect


def partition(pred, xs):
    left = []
    right = []
    for x in xs:
        if pred(x):
            left.append(x)
        else:
            right.append(x)
    return left, right


def is_runnable(state, f):
    args = inspect.getargspec(f).args
    for arg in args:
        if arg not in state:
            return False
    return True


def run_bit(state, f):
    args = inspect.getargspec(f).args
    kwargs = {}
    for arg in args:
        kwargs[arg] = state[arg]
    return f(**kwargs)


def autowire(state, bits):
    while len(bits) > 0:
        is_runnable_now = partial(is_runnable, state)
        runnable, not_runnable = partition(is_runnable_now, bits)
        assert len(runnable) > 0
        for bit in runnable:
            result = run_bit(state, bit)
            state.update(result)
        bits = not_runnable
