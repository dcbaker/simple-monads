# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of a Result type."""

from __future__ import annotations
from typing import *
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
F = TypeVar('F')

__all__ = [
    'Result',
    'Error',
    'Success',
    'UnwrapError',
    'ErrorWrapper',
]


class UnwrapError(Exception):
    """Error thrown when unwrapping is invalid."""


class ErrorWrapper(Exception):
    """wraps non Exception Errors"""


class Result(Generic[T, E]):

    """Base Class for Option, do not directly instantiate"""

    @staticmethod
    def is_ok() -> bool:
        """Returns True if this is a Success otherwise False."""
        raise NotImplementedError()

    @staticmethod
    def is_err() -> bool:
        """Returns True if this is an Error otherwise False."""
        raise NotImplementedError()

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

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        """Transform the held value or return the Error unchanged.

        :param cb: A callback taking the held success type and returning a new one
        :return: A result with the transformed Success or an unchanged Error
        """
        raise NotImplementedError()

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        """Transform the held error or return the success unchanged.

        :param cb: A callback taking the held error type and returning a new one
        :return: A result with the transformed Error or an unchanged Success
        """
        raise NotImplementedError()

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        """Transform the held value or return the default.

        :param default: A value to use of Error
        :param cb: A callback to transform the held value of a Success
        :return: The fallback value or the transformed held value
        """
        raise NotImplementedError()

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        """Transform the held value or return the calculated default

        :param default: A callable returning a value for Error
        :param cb: A callback to transform the held value of a Success
        :return: The fallback value or the transformed held value
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
        e: Exception
        if isinstance(self._held, Exception):
            e = self._held
        else:
            e = ErrorWrapper(self._held)
        raise UnwrapError(msg or 'Attempted to unwrap an Error') from e

    def unwrap_or(self, fallback: T) -> T:
        return fallback

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return fallback()

    def unwrap_err(self, msg: str | None = None) -> E:
        return self._held

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        return Error(self._held)

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        return Error(cb(self._held))

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        return default()


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

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        return Success(cb(self._held))

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        return Success(self._held)

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        return cb(self._held)

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        return cb(self._held)
