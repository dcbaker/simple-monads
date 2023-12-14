# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of an Option type."""

from __future__ import annotations
from functools import wraps
from typing import *
from dataclasses import dataclass

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')
U = TypeVar('U')

__all__ = [
    'EmptyMaybeError',
    'Maybe',
    'Something',
    'Nothing',
    'maybe',
    'maybe_wrap',
    'maybe_unwrap',
]


class EmptyMaybeError(Exception):

    """Raised when attempting to access an empty Option type."""


class Maybe(Generic[T]):

    """Base Class for Option, do not directly instantiate"""

    @staticmethod
    def is_something() -> bool:
        """Is this Something?

        :return: True if this is Something otherwise False
        """
        raise NotImplementedError()

    @staticmethod
    def is_nothing() -> bool:
        """Is this Nothing?

        :return: True if this is Nothing otherwise False
        """
        raise NotImplementedError()

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        """Transforms the held value using the callback

        If this Maybe is Nothing, then Nothing is returned

        :param cb: A callback transforming the held value from T to U
        :return: A new Maybe holding the transformed value
        """
        raise NotImplementedError()

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: A value to use for Nothing
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: callable returning a value U
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def get(self, fallback: T | None = None) -> T | None:
        """Get the held value.

        Works like Python's standard get() interface, including throwing a
        ValueError if this is Nothing.

        :param fallback: A value to use if this is Nothing
        :return: The value or fallback
        """
        raise NotImplementedError()

    def unwrap(self, msg: str | None = None) -> T:
        """Get the held value or throw an Exception.

        :param msg: The error message, otherwise a default is used
        :raises EmptyMaybeError: If this is Nothing
        :return: The held value
        """
        raise NotImplementedError()

    def unwrap_or(self, fallback: T) -> T:
        """Get the value or a fallback value.

        Unlike get() doesn't provide a fallback of None, which narrows type
        checking.

        :param fallback: The fallback to return
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        """Get the value or call the fallback to get a value

        :param fallback: A callable returning a type T
        :return: The held value or the fallback
        """
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Something(Maybe[T]):

    _held: T

    def __bool__(self) -> bool:
        return True

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


@dataclass(slots=True, frozen=True)
class Nothing(Maybe[T]):

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


def maybe(result: T | None) -> Maybe[T]:
    """Convenience function to convert T | None into Maybe[T].

    This can convert python code using the standard T | None Optional.
    This works correctly only when None is not a valid member of T

    :param result: A None or T type to wrap
    :return: Nothing if result is None, else Something[T](result)
    """
    if result is None:
        return Nothing()
    return Something(result)


def maybe_wrap(f: Callable[P, R]) -> Callable[P, Maybe[R]]:

    """Decorator (or wrapper) for common python code.

    Converts code returning T | None to return Maybe[T]
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        return maybe(f(*args, **kwargs))

    return inner


def maybe_unwrap(f: Callable[P, Maybe[R]]) -> Callable[P, R | None]:

    """Decorator (or wrapper) to convert back to common Python.

    Converts code returning Maybe[T] to T | None.

    This is meant to ease transitioning a codebase to using pyadt, but allowing
    code to internally use Maybe, but return common Python Optional
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
        return f(*args, **kwargs).get()

    return inner
