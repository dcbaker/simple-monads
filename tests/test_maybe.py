# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

from __future__ import annotations

import pytest

from pyadt.maybe import *


class TestMaybe:

    class TestMap:

        def test_something(self) -> None:
            s = Something(1).map(str)
            assert s == Something('1')

        def test_nothing(self) -> None:
            s = Nothing().map(str)
            assert s == Nothing()

    class TestGet:

        def test_something(self) -> None:
            assert Something(1).get() == 1

        def test_empty(self) -> None:
            with pytest.raises(ValueError):
                Nothing().get()

        def test_empty_with_fallback(self) -> None:
            assert Nothing().get('foo') == 'foo'

    class TestIsSomething:

        def test_something(self) -> None:
            assert Something(1).is_something()

        def test_nothing(self) -> None:
            assert not Nothing().is_something()

    class TestIsNothing:

        def test_something(self) -> None:
            assert not Something(1).is_nothing()

        def test_nothing(self) -> None:
            assert Nothing().is_nothing()

    class TestUnwrap:

        def test_something(self) -> None:
            assert Something('foo').unwrap() == 'foo'

        def test_nothing(self) -> None:
            with pytest.raises(EmptyMaybeError, match='Attempted to unwrap Nothing'):
                assert Nothing().unwrap()

        def test_nothing_msg(self) -> None:
            msg = 'test message'
            with pytest.raises(EmptyMaybeError, match=msg):
                assert Nothing().unwrap(msg)
