# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

from __future__ import annotations
from typing import cast

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

    class TestMapOr:

        def test_something(self) -> None:
            assert Something(1).map_or(str, '2') == Something('1')

        def test_nothing(self) -> None:
            assert Nothing().map_or(str, '2') == Something('2')

    class TestMapOrElse:

        def test_something(self) -> None:
            assert Something(1).map_or_else(str, lambda: '2') == Something('1')

        def test_nothing(self) -> None:
            assert Nothing().map_or_else(str, lambda: '2') == Something('2')

    class TestGet:

        def test_something(self) -> None:
            assert Something(1).get() == 1

        def test_empty(self) -> None:
            assert Nothing().get() is None

        def test_empty_with_fallback(self) -> None:
            assert cast(Nothing[str], Nothing()).get('foo') == 'foo'

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

    class TestMaybe:

        def test_something(self) -> None:
            assert maybe('foo') == Something('foo')

        def test_nothing(self) -> None:
            assert maybe(None) == Nothing()

class TestMaybeWrap:

    def test_something(self) -> None:
        @maybe_wrap
        def helper() -> str:
            return 'foo'

        assert helper() == Something('foo')

    def test_nothing(self) -> None:
        @maybe_wrap
        def helper() -> None:
            return None

        assert helper() == Nothing()


class TestMaybeUnwrap:

    def test_something(self) -> None:
        @maybe_unwrap
        def helper() -> Maybe[str]:
            return Something('foo')

        assert helper() == 'foo'

    def test_nothing(self) -> None:
        @maybe_unwrap
        def helper() -> Maybe[str]:
            return Nothing()

        assert helper() is None
