from typing import Any, Callable, Iterable, List, Protocol, TypeVar, Union

__all__ = ['pluralized']

T = TypeVar('T')
V = TypeVar('V')


class ExpressionMethodWithKwargs(Protocol):
    def __call__(self, obj: T, **kwargs) -> V: ...


class ExpressionMethodWithoutKwargs(Protocol):
    def __call__(self, obj: T) -> V: ...


ExpressionMethod = Union[ExpressionMethodWithKwargs, ExpressionMethodWithoutKwargs]


def pluralized(fn: ExpressionMethod) -> Callable[[Iterable[T]], List[V]]:
    """Return a method which maps a set of args onto fn()

    >>> fn = lambda d: d
    >>> fn({'id': 1})
    {'id': 1}
    >>> fn_pluralized = pluralized(fn)
    >>> fn_pluralized([{'id': 1}, {'id': 2}])
    [{'id': 1}, {'id': 2}]

    """

    def bulk_fn(args: Iterable[T], **kwargs) -> List[V]:
        mapped = map(lambda arg: fn(arg, **kwargs), args)
        return list(mapped)

    bulk_fn.__name__ = f'bulk_{fn.__name__}'
    return bulk_fn
