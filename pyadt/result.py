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
    'Nothing',
]


class Result(Generic[T, E]):

    """Base Class for Option, do not directly instantiate"""


@dataclass(slots=True, frozen=True)
class Error(Result[T, E]):

    _held: E


@dataclass(slots=True, frozen=True)
class Success(Result[T, E]):

    _held: T
