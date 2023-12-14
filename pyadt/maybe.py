# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of an Option type."""

from __future__ import annotations
from os import stat
from typing import *
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

__all__ = [
    'EmptyMaybeError',
    'Maybe',
    'Something',
    'Nothing',
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

    def get(self, fallback: T | None = None) -> T:
        """Get the held value.

        Works like Python's standard get() interface, including throwing a
        ValueError if this is Nothing.

        :param fallback: A value to use if this is Nothing
        :raises ValueError: If this is nothing, and no fallback is provided
        :return: The value or fallback
        """
        raise NotImplementedError()

    def unwrap(self, msg: str | None = None) -> T:
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Something(Maybe[T]):

    _held: T

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

    def get(self, fallback: T | None = None) -> T:
        return self._held

    def unwrap(self, msg: str | None = None) -> T:
        return self._held


@dataclass(slots=True, frozen=True)
class Nothing(Maybe[T]):

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

    def get(self, fallback: T | None = None) -> T:
        if fallback is None:
            raise ValueError('Attempted to get the value from Nothing with no fallback')
        return fallback

    def unwrap(self, msg: str | None = None) -> T:
        if msg is None:
            msg = 'Attempted to unwrap Nothing'
        raise EmptyMaybeError(msg)
