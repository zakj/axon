from collections.abc import Callable, Iterable
from itertools import filterfalse, tee


def partition[T](
    predicate: Callable[[T], bool], iterable: Iterable[T]
) -> tuple[Iterable[T], Iterable[T]]:
    """Partition iterable into two lists, where predicate is False or True."""
    t1, t2 = tee(iterable)
    return filterfalse(predicate, t1), filter(predicate, t2)
