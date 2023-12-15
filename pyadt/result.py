# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of a Result type."""

from __future__ import annotations
from typing import *
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

__all__ = [
    'Result',
    'Error',
    'Success',
    'UnwrapError',
]


class UnwrapError(Exception):
    pass


class Result(Generic[T, E]):

    """Base Class for Option, do not directly instantiate"""

    @staticmethod
    def is_ok() -> bool:
        """Returns True if this is a Success otherwise False."""

    @staticmethod
    def is_err() -> bool:
        """Returns True if this is an Error otherwise False."""

    def unwrap(self, msg: str | None = None) -> T:
        """Get the held value or throw an Exception.

        :param msg: The error message, otherwise a default is used
        :raises UnwrapError: If this is an Err
        :return: The held value
        """
        raise NotImplementedError()

    def unwrap_or(self, fallback: T) -> T:
        """Return the held value or fallback if this is an Error.

        :param fallback: A value to use incase of Error
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        """Return the held value or the result of the fallback.

        :param fallback: A callable to generate a result if this in Error
        :return: Either the held value or the fallback value
        """
        raise NotImplementedError()

    def unwrap_err(self, msg: str | None = None) -> E:
        """Return the Error, or throw an UnwrapError

        :param msg: The message to add to the UnwrapError, otherwise a default is used
        :raises UnwrapError: Thrown if this is a Success
        :return: The held error
        """
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Error(Result[T, E]):

    _held: E

    def __bool__(self) -> bool:
        return False

    @staticmethod
    def is_ok() -> bool:
        return False

    @staticmethod
    def is_err() -> bool:
        return True

    def unwrap(self, msg: str | None = None) -> T:
        raise UnwrapError(msg or 'Attempted to unwrap an Error') from self._held

    def unwrap_or(self, fallback: T) -> T:
        return fallback

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return fallback()

    def unwrap_err(self, msg: str | None = None) -> E:
        return self._held


@dataclass(slots=True, frozen=True)
class Success(Result[T, E]):

    _held: T
    def __bool__(self) -> bool:
        return True

    @staticmethod
    def is_ok() -> bool:
        return True

    @staticmethod
    def is_err() -> bool:
        return False

    def unwrap(self, msg: str | None = None) -> T:
        return self._held

    def unwrap_or(self, fallback: T) -> T:
        return self._held

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return self._held

    def unwrap_err(self, msg: str | None = None) -> E:
        if msg is None:
            msg = 'Attempted to unwrap the error from a Success'
        raise UnwrapError(msg)
