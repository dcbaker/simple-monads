# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of an Option type."""

from __future__ import annotations
from functools import wraps
from typing import TYPE_CHECKING, TypeVar, ParamSpec, Generic, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from .result import Result

P = ParamSpec('P')
R = TypeVar('R')
E = TypeVar('E')
T = TypeVar('T')
U = TypeVar('U')

__all__ = [
    'EmptyMaybeError',
    'Maybe',
    'Nothing',
    'Something',
    'maybe',
    'unwrap_maybe',
    'wrap_maybe',
]


class EmptyMaybeError(Exception):

    """Raised when calling :meth:`Maybe.unwrap` on an empty Maybe.

    It is advised to *not* catch this exception, as it is usually the result of
    an incorrect assumption in the code, or it truly is fatal.

    In the former case replacing :meth:`Maybe.unwrap` with
    :meth:`Maybe.unwrap_or` or :meth:`Maybe.get` may be mor appropriate.
    """


class Maybe(Generic[T]):

    """Base Class for Option, do not directly instantiate.

    This class is not useful for instantiation, instead use either
    :class:`Something` or :class:`Nothing`. This class is useful for isinstance
    """

    @staticmethod
    def is_something() -> bool:
        """Is this Something?

        It is *strongly* recommended to use this method an not
        :func:`isinstance`.

        >>> maybe('foo').is_something()
        True

        >>> maybe(None).is_something()
        False

        :return: True if this is Something otherwise False
        """
        raise NotImplementedError()

    @staticmethod
    def is_nothing() -> bool:
        """Is this Nothing?

        It is *strongly* recommended to use this method an not
        :func:`isinstance`.

        >>> maybe('foo').is_nothing()
        False

        >>> maybe(None).is_nothing()
        True

        :return: True if this is Nothing otherwise False
        """
        raise NotImplementedError()

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        """Transforms the held value using the callback

        If this Maybe is Nothing, then Nothing is returned

        >>> maybe(500).map(str).unwrap()
        '500'

        >>> maybe(None).map(str).is_nothing()
        True

        :param cb: A callback transforming the held value from T to U
        :return: A new Maybe holding the transformed value
        """
        raise NotImplementedError()

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        >>> maybe(500).map_or(str, '0').unwrap()
        '500'

        >>> maybe(None).map_or(str, '0').unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: A value to use for Nothing
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        >>> maybe(500).map_or_else(str, lambda: '0').unwrap()
        '500'

        >>> maybe(None).map_or_else(str, lambda: '0').unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: callable returning a value U
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def get(self, fallback: T | None = None) -> T | None:
        """Get the held value.

        Works much like Python's normal `.get()` methods, but never throws.

        >>> maybe('500').get()
        '500'

        >>> maybe(None).get('a')
        'a'

        :param fallback: A value to use if this is Nothing
        :return: The value or fallback
        """
        raise NotImplementedError()

    def unwrap(self, msg: str | None = None) -> T:
        """Get the held value or throw an Exception.

        >>> maybe('foo').unwrap()
        'foo'

        >>> maybe(None).unwrap()
        Traceback (most recent call last):
          ...
        simple_monads.maybe.EmptyMaybeError: Attempted to unwrap Nothing

        >>> maybe(None).unwrap("Expected a result")
        Traceback (most recent call last):
          ...
        simple_monads.maybe.EmptyMaybeError: Expected a result

        :param msg: The error message, otherwise a default is used
        :raises EmptyMaybeError: If this is Nothing
        :return: The held value
        """
        raise NotImplementedError()

    def unwrap_or(self, fallback: T) -> T:
        """Get the value or a fallback value.

        Unlike get() doesn't provide a fallback of None, which narrows type
        checking.

        >>> maybe(500).unwrap_or(0)
        500

        >>> maybe(None).unwrap_or(0)
        0

        :param fallback: The fallback to return
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        """Get the value or call the fallback to get a value

        >>> maybe(500).unwrap_or_else(lambda: 0)
        500

        >>> maybe(None).unwrap_or_else(lambda: 0)
        0

        :param fallback: A callable returning a type T
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Run a callback on the value if it is Something

        >>> maybe(500).and_then(lambda x: maybe(0)).unwrap()
        0

        :param cb: A callback to run on the held value or Something()
        :return: A Maybe[U] with the result of the callback or nothing
        """
        raise NotImplementedError()

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        """Run a callback to get a value if this is Nothing or return self.

        >>> maybe(500).or_else(lambda: maybe(100)).unwrap()
        500

        >>> maybe(None).or_else(lambda: maybe(100)).unwrap()
        100

        :param fallback: A callback to run if this is Nothing returning a
            Maybe[T]
        :return: A Maybe[T], which is self unchanged if this Something,
            otherwise the result of fallback
        """
        raise NotImplementedError()

    def ok_or(self, err: E) -> Result[T, E]:
        """Convert this Option to a Result.

        If the Option is Something, that will be placed in the Success value,
        otherwise the Error value of E will be used.

        >>> maybe(0).ok_or("WHAT!").unwrap()
        0

        >>> maybe(None).ok_or("WHAT!").unwrap_err()
        'WHAT!'

        :param err: An error if this is Nothing
        :return: A result with the held value as a Success or an Error
        """
        raise NotImplementedError()

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        """Convert this Option to a Result.

        If the Option is Something, that will be placed in the Success value,
        otherwise the Error value of E will be used.

        >>> maybe(0).ok_or_else(lambda: "WHAT!").unwrap()
        0

        >>> maybe(None).ok_or_else(lambda: "WHAT!").unwrap_err()
        'WHAT!'

        :param err: An callable returning a type E
        :return: A result with the held value as a Success or an Error
        """
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Something(Maybe[T]):

    """A Maybe that holds a value."""

    _held: T

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Something({self._held!r})"

    @staticmethod
    def is_something() -> bool:
        return True

    @staticmethod
    def is_nothing() -> bool:
        return False

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        return Something(cb(self._held))

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        return Something(cb(self._held))

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        return Something(cb(self._held))

    def get(self, fallback: T | None = None) -> T | None:
        return self._held

    def unwrap(self, msg: str | None = None) -> T:
        return self._held

    def unwrap_or(self, fallback: T) -> T:
        return self._held

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return self._held

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return cb(self._held)

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        return self

    def ok_or(self, err: E) -> Result[T, E]:
        from .result import Success  # pylint: disable=import-outside-toplevel
        return Success(self._held)

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        from .result import Success  # pylint: disable=import-outside-toplevel
        return Success(self._held)


@dataclass(slots=True, frozen=True)
class Nothing(Maybe[T]):

    """A Maybe that does not hold a value."""

    def __bool__(self) -> bool:
        return False

    @staticmethod
    def is_something() -> bool:
        return False

    @staticmethod
    def is_nothing() -> bool:
        return True

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        return Nothing()

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        return Something(fallback)

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        return Something(fallback())

    def get(self, fallback: T | None = None) -> T | None:
        return fallback

    def unwrap(self, msg: str | None = None) -> T:
        if msg is None:
            msg = 'Attempted to unwrap Nothing'
        raise EmptyMaybeError(msg)

    def unwrap_or(self, fallback: T) -> T:
        return fallback

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return fallback()

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing()

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        return fallback()

    def ok_or(self, err: E) -> Result[T, E]:
        from .result import Error  # pylint: disable=import-outside-toplevel
        return  Error(err)

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        from .result import Error  # pylint: disable=import-outside-toplevel
        return  Error(err())


def maybe(result: T | None) -> Maybe[T]:
    """Convenience function to convert T | None into Maybe[T].

    This can convert python code using the standard T | None Optional.
    This works correctly only when None is not a valid member of T

    >>> maybe(0)
    Something(0)

    >>> maybe(None)
    Nothing()

    :param result: A None or T type to wrap
    :return: Nothing if result is None, else Something[T](result)
    """
    if result is None:
        return Nothing()
    return Something(result)


def wrap_maybe(f: Callable[P, R | None]) -> Callable[P, Maybe[R]]:

    """Decorator (or wrapper) for common python code.

    Converts code returning T | None to return Maybe[T]

    >>> @wrap_maybe
    ... def func(arg: bool) -> str | None:
    ...     if arg:
    ...         return "yes!"
    ...     return None
    ...
    >>> func(True)
    Something('yes!')

    >>> func(False)
    Nothing()

    >>> import os
    >>> f = wrap_maybe(os.environ.get)
    >>> f("Totally not there")
    Nothing()

    :param f: A callable returning a type R or None
    :return: A new callable return :class:`Maybe[R]`, where a non-null are
        :class:`Success`, and None is :class:`Nothing`
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        return maybe(f(*args, **kwargs))

    return inner


def unwrap_maybe(f: Callable[P, Maybe[R]]) -> Callable[P, R | None]:

    """Decorator (or wrapper) to convert back to common Python.

    Converts code returning Maybe[T] to T | None.

    This is meant to ease transitioning a codebase to using simple_monads, but
    allowing code to internally use Maybe, but return common Python Optional

    >>> def raw(arg: str) -> Maybe[str]:
    ...     if arg:
    ...         return Something(arg)
    ...     return Nothing()

    >>> f = unwrap_maybe(raw)
    >>> f("foo")
    'foo'

    >>> @unwrap_maybe
    ... def g(arg: str) -> str | None:
    ...     return raw(arg)

    >>> g("foo")
    'foo'

    :param f: A callable returning a :class:`Maybe[T]`
    :return: A new callable returning a `T | None`
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
        return f(*args, **kwargs).get()

    return inner
