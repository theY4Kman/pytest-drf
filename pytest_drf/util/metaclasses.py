from typing import Optional, Type, Tuple, Union

__all__ = ['prioritize_bases', 'prioritize_base', 'deprioritize_base']


class _PrioritizeBases(type):
    """Metaclass which ensures the specified bases are listed first in any subclasses
    """

    base_class_priorities: Tuple[Tuple[Type, Optional[Union[int, float]]]] = ()

    @classmethod
    def sort_order(mcs, base) -> Union[int, float]:
        """Return priority of base in a subclass, or Infinity to retain original order
        """
        highest_priority = len(mcs.base_class_priorities)

        for i, (prioritized_base, priority) in enumerate(mcs.base_class_priorities):
            if issubclass(base, prioritized_base):
                return priority if priority is not None else i
        else:
            return highest_priority

    def __new__(mcs, name, bases, attrs):
        bases = tuple(sorted(bases, key=mcs.sort_order))
        return super().__new__(mcs, name, bases, attrs)


def prioritize_bases(*bases, reverse=False) -> Type[_PrioritizeBases]:
    """Return a metaclass that prioritizes the specified bases in any declared subclasses

    By reordering base classes at subclass construction time, we allow the base
    classes to be declared with respect to readability — and without being forced
    to declare bases to appease the method resolution order (whereby the attributes
    from the first-listed base class win out against later-listed bases).

    This is used for Great Good with AsUser et al, because it reads better to
    declare AsUser *after* APIViewTest, but we don't want APIViewTest's default
    client fixture to overrule AsUser's.

    Example usage:

        class APIViewTest:
            # Set a default value for client
            client = static_fixture('unauthed_client')

        class AsUser:
            client = static_fixture('user_client')

        class PrioritizedAsUser(AsUser, metaclass=prioritize_bases(AsUser)):
            pass

        class DescribeMyUnprioritizedView(
            APIViewTest,
            AsUser,
        ):
            pass

        class DescribeMyPrioritizedView(
            APIViewTest,
            PrioritizedAsUser,
        ):
            pass


        assert APIViewTest().client() == 'unauthed_client'
        assert DescribeMyUnprioritizedView().client() == 'unauthed_client'
        assert DescribeMyPrioritizedView().client() == 'user_client'

    """
    if reverse:
        priorities = [
            (base, float('Inf'))
            for base in bases
        ]
    else:
        priorities = [
            (base, i)
            for i, base in enumerate(bases)
        ]

    class PrioritizeBases(_PrioritizeBases):
        base_class_priorities = priorities

    return PrioritizeBases


def prioritize_base(cls: Type) -> Type:
    """Class decorator to place decorated class first in subclasses' MRO"""
    return prioritize_bases(cls)(cls.__name__, (cls,), {})


def deprioritize_base(cls: Type) -> Type:
    """Class decorator to place decorated class last in subclasses' MRO"""
    return prioritize_bases(cls, reverse=True)(cls.__name__, (cls,), {})
