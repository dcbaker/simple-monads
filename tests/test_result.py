# SPDX-License-Identifier: MIT
# Copyright © 2023-2024 Dylan Baker

from __future__ import annotations
from typing import cast

import pytest

from simple_monads.result import *

class TestResult:

    class TestUnwrap:

        def test_error(self) -> None:
            with pytest.raises(UnwrapError, match='Attempted to unwrap an Error'):
                Error(Exception('foo')).unwrap()

        def test_error_msg(self) -> None:
            msg = 'test message'
            with pytest.raises(UnwrapError, match=msg):
                Error(Exception('foo')).unwrap(msg)

        def test_success(self) -> None:
            assert Success('foo').unwrap() == 'foo'

    class TestUnwrapOr:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert e.unwrap_or('bar') == 'bar'

        def test_success(self) -> None:
            assert Success('foo').unwrap_or('bar') == 'foo'

    class TestUnwrapOrElse:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert e.unwrap_or_else(lambda: 'bar') == 'bar'

        def test_success(self) -> None:
            assert Success('foo').unwrap_or_else(lambda: 'bar') == 'foo'

    class TestUnwrapOrElseAsync:

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            async def fb() -> str:
                return 'bar'

            e: Result[str, Exception] = Error(Exception('foo'))
            assert await e.unwrap_or_else_async(fb) == 'bar'

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            async def fb() -> str:
                return 'bar'
            assert await Success('foo').unwrap_or_else_async(fb) == 'foo'

    class TestBool:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert not e

        def test_success(self) -> None:
            assert Success('foo')

    class TestIsErr:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert e.is_err()

        def test_success(self) -> None:
            assert not Success('foo').is_err()

    class TestIsOk:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert not e.is_ok()

        def test_success(self) -> None:
            assert Success('foo').is_ok()

    class TestUnwrapErr:

        def test_error(self) -> None:
            err = Exception('foo')
            e: Result[str, Exception] = Error(err)
            assert e.unwrap_err() is err

        def test_success(self) -> None:
            with pytest.raises(UnwrapError, match='Attempted to unwrap the error from a Success'):
                Success('foo').unwrap_err()

        def test_success_with_msg(self) -> None:
            msg = 'test message'
            with pytest.raises(UnwrapError, match=msg):
                Success('foo').unwrap_err(msg)

    class TestMap:

        def test_error(self) -> None:
            e: Result[str, Exception] = Error(Exception('foo'))
            assert e.map(int) == cast(Result[int, Exception], e)

        def test_success(self) -> None:
            assert Success('1').map(int) == Success(1)

    class TestMapAsync:

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            async def cb(v: str) -> int:
                pytest.fail()

            e: Result[str, Exception] = Error(Exception('foo'))
            assert await e.map_async(cb) == cast(Result[int, Exception], e)

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            async def cb(v: str) -> int:
                return int(v)

            assert await Success('1').map_async(cb) == Success(1)

    class TestMapErr:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_err(int) == Error(1)

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_err(int) == cast(Success[str, int], s)

    class TestMapErrAsync:

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            async def cb(v: str) -> int:
                return int(v)
            e: Result[str, str] = Error('1')
            assert await e.map_err_async(cb) == Error(1)

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            async def cb(v: str) -> int:
                pytest.fail()
            s: Success[str, str] = Success('1')
            assert await s.map_err_async(cb) == cast(Success[str, int], s)

    class TestMapOr:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_or('foo', lambda _: 'bar') == 'foo'

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_or('foo', lambda _: 'bar') == 'bar'

    class TestMapOrAsync:

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            async def cb(v: str) -> str:
                pytest.fail()

            e: Result[str, str] = Error('1')
            assert await e.map_or_async('foo', cb) == 'foo'

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            async def cb(v: str) -> str:
                return 'bar'
            s: Success[str, str] = Success('1')
            assert await s.map_or_async('foo', cb) == 'bar'

    class TestMapOrElse:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_or_else(lambda: 'foo', lambda _: 'bar') == 'foo'

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_or_else(lambda: 'foo', lambda _: 'bar') == 'bar'

    class TestMapOrElseASync:

        @staticmethod
        async def _cb(v: int) -> int:
            return v + 5

        @staticmethod
        async def _fb() -> int:
            return 3

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            e: Result[int, int] = Error(1)
            assert await e.map_or_else_async(self._fb, self._cb) == 3

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            s: Success[int, str] = Success(1)
            assert await s.map_or_else_async(self._fb, self._cb) == 6

    class TestAndThen:

        @staticmethod
        def _cb(res: str) -> Result[int, str]:
            return Success(int(res))

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.and_then(self._cb) == cast(Result[int, str], e)

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.and_then(self._cb) == Success(1)

    class TestAndThenAsync:

        @staticmethod
        async def _cb(res: str) -> Result[int, str]:
            return Success(int(res))

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert await e.and_then_async(self._cb) == cast(Result[int, str], e)

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert await s.and_then_async(self._cb) == Success(1)

    class TestOrElse:

        @staticmethod
        def _cb(res: str) -> Result[str, int]:
            return Error(int(res))

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.or_else(self._cb) == Error(1)

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.or_else(self._cb) == cast(Result[str, int], s)

    class TestOrElseAsync:

        @staticmethod
        async def _cb(res: str) -> Result[str, int]:
            return Error(int(res))

        @pytest.mark.asyncio
        async def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert await e.or_else_async(self._cb) == Error(1)

        @pytest.mark.asyncio
        async def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert await s.or_else_async(self._cb) == cast(Result[str, int], s)

    class TestErr:

        def test_error(self) -> None:
            e: Result[str, int] = Error(4)
            assert e.err().unwrap() == 4

        def test_success(self) -> None:
            s: Result[int, int] = Success(4)
            assert s.err().is_nothing()

    class TestOk:

        def test_error(self) -> None:
            e: Result[str, int] = Error(4)
            assert e.ok().is_nothing()

        def test_success(self) -> None:
            s: Result[int, int] = Success(4)
            assert s.ok().unwrap() == 4

    class TestMatch:

        def test_error(self) -> None:
            e: Result[str, int] = Error(4)
            match e:
                case Success(4):
                    pytest.fail()
                case Error(4):
                    assert True
                case _:
                    pytest.fail()

        def test_success(self) -> None:
            s: Result[int, int] = Success(4)
            match s:
                case Error(4):
                    pytest.fail()
                case Success(4):
                    assert True
                case _:
                    pytest.fail()


class TestWrapResult:

    def test_success(self) -> None:
        @wrap_result()
        def foo() -> str:
            return ''

        assert foo() == Success('')

    def test_error(self) -> None:
        @wrap_result(Exception)
        def foo() -> str:
            raise Exception('foo')

        assert isinstance(foo().unwrap_err(), Exception)

    def test_error_multi(self) -> None:
        @wrap_result((ValueError, RecursionError))
        def foo() -> str:
            raise ValueError('foo')

        assert isinstance(foo().unwrap_err(), ValueError)

    def test_error_uncaught(self) -> None:
        @wrap_result(ArithmeticError)
        def foo() -> str:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            foo()


class TestWrapResultASync:

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        @wrap_result_async()
        async def foo() -> str:
            return ''

        assert await foo() == Success('')

    @pytest.mark.asyncio
    async def test_error(self) -> None:
        @wrap_result_async(Exception)
        async def foo() -> str:
            raise Exception('foo')

        err = await foo()
        assert isinstance(err.unwrap_err(), Exception)

    @pytest.mark.asyncio
    async def test_error_multi(self) -> None:
        @wrap_result_async((ValueError, RecursionError))
        async def foo() -> str:
            raise ValueError('foo')

        err = await foo()
        assert isinstance(err.unwrap_err(), ValueError)

    @pytest.mark.asyncio
    async def test_error_uncaught(self) -> None:
        @wrap_result_async(ArithmeticError)
        async def foo() -> str:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            await foo()


class TestUnwrapResult:

    def test_success(self) -> None:
        @unwrap_result
        def foo() -> Result[str, ValueError]:
            return Success('foo')

        assert foo() == 'foo'

    def test_error(self) -> None:
        @unwrap_result
        def foo() -> Result[str, ValueError]:
            return Error(ValueError('foo'))

        with pytest.raises(ValueError, match='foo'):
            foo()


class TestUnwrapResultAsync:

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        @unwrap_result_async
        async def foo() -> Result[str, ValueError]:
            return Success('foo')

        assert await foo() == 'foo'

    @pytest.mark.asyncio
    async def test_error(self) -> None:
        @unwrap_result_async
        async def foo() -> Result[str, ValueError]:
            return Error(ValueError('foo'))

        with pytest.raises(ValueError, match='foo'):
            await foo()


class TestPropagate:

    def test_prop(self) -> None:

        @stop
        def inner() -> Result[str, int]:
            r: Result[str, int] = Error(4)
            x = r.propagate()
            return Success(x + 'bar')

        assert inner() == Error(4)

    def test_no_prop(self) -> None:

        @stop
        def inner() -> Result[str, int]:
            r: Result[str, int] = Success('foo')
            x = r.propagate()
            return Success(x + 'bar')

        assert inner() == Success('foobar')


class TestPropagateAsync:

    @pytest.mark.asyncio
    async def test_prop(self) -> None:
        @stop_async
        async def inner() -> Result[str, int]:
            r: Result[str, int] = Error(4)
            x = r.propagate()
            return Success(x + 'bar')

        assert await inner() == Error(4)

    @pytest.mark.asyncio
    async def test_no_prop(self) -> None:
        @stop_async
        async def inner() -> Result[str, int]:
            r: Result[str, int] = Success('foo')
            x = r.propagate()
            return Success(x + 'bar')

        assert await inner() == Success('foobar')
