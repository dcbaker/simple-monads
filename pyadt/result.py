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


@dataclass(slots=True, frozen=True)
class Error(Result[T, E]):

    _held: E

    def unwrap(self, msg: str | None = None) -> T:
        raise UnwrapError(msg or 'Attempted to unwrap an Error') from self._held

    def unwrap_or(self, fallback: T) -> T:
        return fallback


@dataclass(slots=True, frozen=True)
class Success(Result[T, E]):

    _held: T

    def unwrap(self, msg: str | None = None) -> T:
        return self._held

    def unwrap_or(self, fallback: T) -> T:
        return self._held
