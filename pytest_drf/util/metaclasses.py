from typing import Type, Tuple, Union

__all__ = ['prioritize_bases']


class _PrioritizeBases(type):
    """Metaclass which ensures the specified bases are listed first in any subclasses
    """

    prioritized_bases: Tuple[Type] = ()

    @classmethod
    def sort_order(mcs, base) -> Union[int, float]:
        """Return priority of base in a subclass, or Infinity to retain original order
        """
        for i, prioritized_base in enumerate(mcs.prioritized_bases):
            if issubclass(base, prioritized_base):
                return i
        else:
            return float('Inf')

    def __new__(mcs, name, bases, attrs):
        bases = tuple(sorted(bases, key=mcs.sort_order))
        return super().__new__(mcs, name, bases, attrs)


def prioritize_bases(*bases) -> Type[_PrioritizeBases]:
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

    class PrioritizeBases(_PrioritizeBases):
        prioritized_bases = bases

    return PrioritizeBases
