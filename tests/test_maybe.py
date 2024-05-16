# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

from __future__ import annotations
from typing import cast

import pytest

from simple_monads.maybe import *


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

    class TestUnwrapOr:

        def test_something(self) -> None:
            assert Something('foo').unwrap_or('bar') == 'foo'

        def test_nothing(self) -> None:
            assert cast('Nothing[str]', Nothing()).unwrap_or('bar') == 'bar'

    class TestUnwrapOrElse:

        def test_something(self) -> None:
            assert Something('foo').unwrap_or_else(lambda: 'bar') == 'foo'

        def test_nothing(self) -> None:
            assert cast('Nothing[str]', Nothing()).unwrap_or_else(lambda: 'bar') == 'bar'

    class TestBool:

        def test_something(self) -> None:
            assert Something('foo')

        def test_nothing(self) -> None:
            assert not Nothing()

    class TestAndThen:

        @staticmethod
        @wrap_maybe
        def to_int(v: str) -> int | None:
            try:
                return int(v)
            except ValueError:
                return None

        def test_something_invalid(self) -> None:
            assert Something('foo').and_then(self.to_int) == Nothing()

        def test_something_valid(self) -> None:
            assert Something('1').and_then(self.to_int) == Something(1)

        def test_nothing(self) -> None:
            assert Nothing().and_then(self.to_int) == Nothing()

    class TestOrElse:

        def test_something(self) -> None:
            Something('foo').or_else(lambda: maybe('bar')) == Something('foo')

        def test_nothing(self) -> None:
            cast('Nothing[str]', Nothing()).or_else(lambda: maybe('bar')) == Something('bar')

    class TestOkOr:

        def test_something(self) -> None:
            Something('foo').ok_or('bar').unwrap() == 'foo'

        def test_nothing(self) -> None:
            cast('Nothing[str]', Nothing()).ok_or('bar').unwrap_err() == 'bar'

    class TestOkOrElse:

        def test_something(self) -> None:
            Something('foo').ok_or_else(lambda: 'bar').unwrap() == 'foo'

        def test_nothing(self) -> None:
            cast('Nothing[str]', Nothing()).ok_or_else(lambda: 'bar').unwrap_err() == 'bar'

    class TestMatch:

        def test_something(self) -> None:
            s = Something('foo')
            match s:
                case Something('bar'):
                    pytest.fail()
                case Something('foo'):
                    assert True
                case Nothing():
                    pytest.fail()
                case _:
                    pytest.fail()

        def test_nothing(self) -> None:
            s: Nothing[str] = Nothing()
            match s:
                case Something('bar'):
                    pytest.fail()
                case Something('foo'):
                    pytest.fail()
                case Nothing():
                    assert True
                case _:
                    pytest.fail()

class TestMaybeFunction:

    def test_something(self) -> None:
        assert maybe('foo') == Something('foo')

    def test_nothing(self) -> None:
        assert maybe(None) == Nothing()


class TestMaybeWrap:

    def test_something(self) -> None:
        @wrap_maybe
        def helper() -> str:
            return 'foo'

        assert helper() == Something('foo')

    def test_nothing(self) -> None:
        @wrap_maybe
        def helper() -> None:
            return None

        assert helper() == Nothing()


class TestMaybeUnwrap:

    def test_something(self) -> None:
        @unwrap_maybe
        def helper() -> Maybe[str]:
            return Something('foo')

        assert helper() == 'foo'

    def test_nothing(self) -> None:
        @unwrap_maybe
        def helper() -> Maybe[str]:
            return Nothing()

        assert helper() is None
