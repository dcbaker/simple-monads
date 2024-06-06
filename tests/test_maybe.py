# SPDX-License-Identifier: MIT
# Copyright © 2023-2024 Dylan Baker

from __future__ import annotations
from typing import TYPE_CHECKING, cast

import pytest

from simple_monads.maybe import *

if TYPE_CHECKING:
    from typing import Awaitable, Callable


class TestMaybe:

    class TestMap:

        def test_something(self) -> None:
            s = Something(1).map(str)
            assert s == Something('1')

        def test_nothing(self) -> None:
            s = Nothing().map(str)
            assert s == Nothing()

    class TestMapAsync:

        @staticmethod
        async def _helper(v: int) -> str:
            return str(v)

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            s = await Something(1).map_async(self._helper)
            assert s == Something('1')

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            s = await Nothing().map_async(self._helper)
            assert s == Nothing()

    class TestMapOr:

        def test_something(self) -> None:
            assert Something(1).map_or(str, '2') == Something('1')

        def test_nothing(self) -> None:
            assert Nothing().map_or(str, '2') == Something('2')

    class TestMapOrAsync:

        @staticmethod
        async def _helper(v: int) -> str:
            return str(v)

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            s = await Something(1).map_or_async(self._helper, '5')
            assert s == Something('1')

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            s = await Nothing().map_or_async(self._helper, '5')
            assert s == Something('5')

    class TestMapOrElse:

        def test_something(self) -> None:
            assert Something(1).map_or_else(str, lambda: '2') == Something('1')

        def test_nothing(self) -> None:
            assert Nothing().map_or_else(str, lambda: '2') == Something('2')

    class TestMapOrElseAsync:

        @staticmethod
        async def _cb(v: int) -> str:
            return str(v)

        @staticmethod
        async def _fb() -> str:
            return '2'

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            assert await Something(1).map_or_else_async(self._cb, self._fb) == Something('1')

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            assert await Nothing().map_or_else_async(self._cb, self._fb) == Something('2')

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

    class TestUnwrapOrElseAsync:

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            async def cb() -> str:
                return 'bar'

            v = await Something('foo').unwrap_or_else_async(cb)
            assert v == 'foo'

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            async def cb() -> str:
                return 'bar'

            v = await cast('Nothing[str]', Nothing()).unwrap_or_else_async(cb)
            assert v == 'bar'

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

    class TestAndThenAsync:

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            async def f(v: int) -> Maybe[str]:
                return Something(str(v))

            v = await Something(1).and_then_async(f)
            assert v.unwrap() == '1'

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            async def f(v: int) -> Maybe[str]:
                pytest.fail()

            v = await Nothing().and_then_async(f)
            assert v == Nothing()

    class TestOrElse:

        def test_something(self) -> None:
            Something('foo').or_else(lambda: maybe('bar')) == Something('foo')

        def test_nothing(self) -> None:
            cast('Nothing[str]', Nothing()).or_else(lambda: maybe('bar')) == Something('bar')

    class TestOrElseAsync:

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            async def cb() -> Maybe[str]:
                return maybe('bar')

            v = await Something('foo').or_else_async(cb)
            assert v == Something('foo')

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            async def cb() -> Maybe[str]:
                return maybe('bar')

            v = await cast('Nothing[str]', Nothing()).or_else_async(cb)
            assert v == Something('bar')

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

    class TestOkOrElseAsync:

        @pytest.mark.asyncio
        async def test_something(self) -> None:
            async def cb() -> str:
                return 'bar'

            v = await Something('foo').ok_or_else_async(cb)
            assert v.unwrap() == 'foo'

        @pytest.mark.asyncio
        async def test_nothing(self) -> None:
            async def cb() -> str:
                return 'bar'

            v = await cast('Nothing[str]', Nothing()).ok_or_else_async(cb)
            assert v.unwrap_err() == 'bar'

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


class TestMaybeWrapAsync:

    @pytest.mark.asyncio
    async def test_something(self) -> None:
        @wrap_maybe_async
        async def helper() -> str:
            return 'foo'

        assert await helper() == Something('foo')

    @pytest.mark.asyncio
    async def test_nothing(self) -> None:
        @wrap_maybe_async
        async def helper() -> None:
            return None

        assert await helper() == Nothing()


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


class TestMaybeUnwrapASync:

    @pytest.mark.asyncio
    async def test_something(self) -> None:
        @unwrap_maybe_async
        async def helper() -> Maybe[str]:
            return Something('foo')

        assert await helper() == 'foo'

    @pytest.mark.asyncio
    async def test_nothing(self) -> None:
        @unwrap_maybe_async
        async def helper() -> Maybe[str]:
            return Nothing()

        assert await helper() is None


class TestPropagate:

    def test_prop(self) -> None:

        @stop
        def inner() -> Maybe[str]:
            r: Maybe[str] = Nothing()
            x = r.propagate()
            return Something(x + 'bar')

        assert inner() == Nothing()

    def test_no_prop(self) -> None:

        @stop
        def inner() -> Maybe[str]:
            r: Maybe[str] = Something('foo')
            x = r.propagate()
            return Something(x + 'bar')

        assert inner() == Something('foobar')


class TestPropagateAsync:

    @pytest.mark.asyncio
    async def test_prop(self) -> None:
        @stop_async
        async def inner() -> Maybe[str]:
            r: Maybe[str] = Nothing()
            x = r.propagate()
            return Something(x + 'bar')

        assert await inner() == Nothing()

    @pytest.mark.asyncio
    async def test_no_prop(self) -> None:
        @stop_async
        async def inner() -> Maybe[str]:
            r: Maybe[str] = Something('foo')
            x = r.propagate()
            return Something(x + 'bar')

        assert await inner() == Something('foobar')
