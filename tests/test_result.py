# SPDX-License-Identifier: MIT
# Copyright © 2023-2026 Dylan Baker

from __future__ import annotations

from typing import assert_type, cast

import pytest

from simple_monads.result import (
    Error,
    Result,
    Success,
    UnwrapError,
    WrapError,
    stop,
    unwrap,
    wrap,
)


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


class TestPydantic:
    @pytest.mark.parametrize('value', [1, '1', Success(1), Success('1')])
    def test_success(self, value: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        adapter = pydantic.TypeAdapter(Result[int, str])
        assert adapter.validate_python(value) == Success(1)

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            ('invalid', Error('invalid')),
            (Error('invalid'), Error('invalid')),
            (Error('1'), Error('1')),
        ],
    )
    def test_error(self, value: object, expected: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        adapter = pydantic.TypeAdapter(Result[int, str])
        assert adapter.validate_python(value) == expected

    @pytest.mark.parametrize('value', ['1', Error('1')])
    def test_error_coercion(self, value: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        adapter = pydantic.TypeAdapter(Result[list[int], int])
        assert adapter.validate_python(value) == Error(1)

    @pytest.mark.parametrize('value', [None, [], Success('invalid'), Error(1)])
    def test_invalid(self, value: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        adapter = pydantic.TypeAdapter(Result[int, str])
        with pytest.raises(pydantic.ValidationError):
            adapter.validate_python(value)

    @pytest.mark.parametrize(
        ('annotation', 'value', 'expected'),
        [
            (Result, 'foo', Success('foo')),
            (Result, Error('foo'), Error('foo')),
            (Success, 'foo', Success('foo')),
            (Success, Success('foo'), Success('foo')),
            (Error, 'foo', Error('foo')),
            (Error, Error('foo'), Error('foo')),
        ],
    )
    def test_unparameterized(self, annotation: object, value: object, expected: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        assert pydantic.TypeAdapter(annotation).validate_python(value) == expected

    @pytest.mark.parametrize('annotation, value', [(Success, Error(1)), (Error, Success(1))])
    def test_wrong_variant(self, annotation: object, value: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        with pytest.raises(pydantic.ValidationError):
            pydantic.TypeAdapter(annotation).validate_python(value)

    def test_model(self) -> None:
        pytest.importorskip('pydantic', minversion='2')
        from pydantic import BaseModel

        class Model(BaseModel):
            value: Result[int, str]

        assert Model.model_validate({'value': '1'}).value == Success(1)
        assert Model.model_validate({'value': Success(1)}).value == Success(1)
        assert Model.model_validate({'value': 'invalid'}).value == Error('invalid')
        assert Model.model_validate({'value': Error('1')}).value == Error('1')

    def test_nested(self) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        adapter = pydantic.TypeAdapter(Result[list[int], str])
        assert adapter.validate_python(['1', 2]) == Success([1, 2])
        assert adapter.validate_python(Success(['1', 2])) == Success([1, 2])

    @pytest.mark.parametrize(
        ('annotation', 'value', 'expected'),
        [
            (Result[int | None, str], None, Success(None)),
            (Result[int | None, str], Success(None), Success(None)),
            (Result[int, str | None], None, Error(None)),
            (Result[int, str | None], Error(None), Error(None)),
        ],
    )
    def test_none(self, annotation: object, value: object, expected: object) -> None:
        pydantic = pytest.importorskip('pydantic', minversion='2')
        assert pydantic.TypeAdapter(annotation).validate_python(value) == expected


class TestWrapResult:
    def test_success(self) -> None:
        @wrap()
        def foo() -> str:
            return ''

        assert foo() == Success('')

    def test_error(self) -> None:
        @wrap(Exception)
        def foo() -> str:
            raise Exception('foo')

        assert isinstance(foo().unwrap_err(), Exception)

    def test_error_multi(self) -> None:
        @wrap((ValueError, RecursionError))
        def foo() -> str:
            raise ValueError('foo')

        assert isinstance(foo().unwrap_err(), ValueError)

    def test_error_uncaught(self) -> None:
        @wrap(ArithmeticError)
        def foo() -> str:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            foo()

    @pytest.mark.asyncio
    async def test_success_async(self) -> None:
        @wrap()
        async def foo() -> str:
            return ''

        assert await foo() == Success('')

    @pytest.mark.asyncio
    async def test_error_async(self) -> None:
        @wrap(Exception)
        async def foo() -> str:
            raise Exception('foo')

        err = await foo()
        assert isinstance(err.unwrap_err(), Exception)

    @pytest.mark.asyncio
    async def test_error_multi_async(self) -> None:
        @wrap((ValueError, RecursionError))
        async def foo() -> str:
            raise ValueError('foo')

        err = await foo()
        assert isinstance(err.unwrap_err(), ValueError)

    @pytest.mark.asyncio
    async def test_error_uncaught_async(self) -> None:
        @wrap(ArithmeticError)
        async def foo() -> str:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            await foo()


class TestUnwrapResult:
    def test_success(self) -> None:
        @unwrap
        def foo() -> Result[str, ValueError]:
            return Success('foo')

        assert foo() == 'foo'

    def test_error(self) -> None:
        @unwrap
        def foo() -> Result[str, ValueError]:
            return Error(ValueError('foo'))

        with pytest.raises(ValueError, match='foo'):
            foo()

    @pytest.mark.asyncio
    async def test_success_async(self) -> None:
        @unwrap
        async def foo() -> Result[str, ValueError]:
            return Success('foo')

        assert await foo() == 'foo'

    @pytest.mark.asyncio
    async def test_error_async(self) -> None:
        @unwrap
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

    def test_doesnt_catch_other_exceptions(self) -> None:
        @stop
        def inner() -> Result[str, int]:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            inner()

    def test_propogate_unwrap(self) -> None:
        @unwrap
        @stop
        def inner() -> Result[str, int]:
            r: Result[str, int] = Error(4)
            x = r.propagate()
            return Success(x + 'bar')

        with pytest.raises(WrapError, match='4'):
            inner()

    @pytest.mark.asyncio
    async def test_prop_async(self) -> None:
        @stop
        async def inner() -> Result[str, int]:
            r: Result[str, int] = Error(4)
            x = r.propagate()
            return Success(x + 'bar')

        assert await inner() == Error(4)

    @pytest.mark.asyncio
    async def test_no_prop_async(self) -> None:
        @stop
        async def inner() -> Result[str, int]:
            r: Result[str, int] = Success('foo')
            x = r.propagate()
            return Success(x + 'bar')

        assert await inner() == Success('foobar')

    @pytest.mark.asyncio
    async def test_doesnt_catch_other_exceptions_async(self) -> None:
        @stop
        async def inner() -> Result[str, int]:
            raise ValueError('foo')

        with pytest.raises(ValueError, match='foo'):
            await inner()


def test_returning_narrow_result() -> None:

    @stop
    def inner() -> Result[str | int, int]:
        def inner2() -> Result[str, int]:
            return Success('foo')

        r: Result[str, int] = inner2()
        return r

    assert inner() == Success('foo')


def test_returning_narrow_error_result() -> None:
    def inner() -> Result[str, int]:
        return Error(4)

    def outer() -> Result[str, int | str]:
        return inner()

    assert outer() == Error(4)


class TestResultCovariance:
    @pytest.mark.parametrize('is_error', [False, True])
    def test_fallbacks(self, is_error: bool) -> None:
        result: Result[str, int] = Error(4) if is_error else Success('foo')
        expected = 5 if is_error else 'foo'

        assert assert_type(result.unwrap_or(5), str | int) == expected
        assert assert_type(result.unwrap_or_else(lambda: 5), str | int) == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_error', [False, True])
    async def test_fallback_async(self, is_error: bool) -> None:
        async def fallback() -> int:
            return 5

        result: Result[str, int] = Error(4) if is_error else Success('foo')
        actual = await result.unwrap_or_else_async(fallback)
        assert assert_type(actual, str | int) == (5 if is_error else 'foo')

    @pytest.mark.parametrize('is_error', [False, True])
    def test_callbacks(self, is_error: bool) -> None:
        def and_callback(value: str) -> Result[int, str]:
            return Error(value)

        def or_callback(error: int) -> Result[int, str]:
            return Success(error)

        result: Result[str, int] = Error(4) if is_error else Success('foo')
        chained = result.and_then(and_callback)
        recovered = result.or_else(or_callback)
        expected_chained: Result[int, int | str] = Error(4) if is_error else Error('foo')
        expected_recovered: Result[str | int, str] = Success(4) if is_error else Success('foo')

        assert assert_type(chained, Result[int, int | str]) == expected_chained
        assert assert_type(recovered, Result[str | int, str]) == expected_recovered

    @pytest.mark.asyncio
    @pytest.mark.parametrize('is_error', [False, True])
    async def test_callbacks_async(self, is_error: bool) -> None:
        async def and_callback(value: str) -> Result[int, str]:
            return Error(value)

        async def or_callback(error: int) -> Result[int, str]:
            return Success(error)

        result: Result[str, int] = Error(4) if is_error else Success('foo')
        chained = await result.and_then_async(and_callback)
        recovered = await result.or_else_async(or_callback)
        expected_chained: Result[int, int | str] = Error(4) if is_error else Error('foo')
        expected_recovered: Result[str | int, str] = Success(4) if is_error else Success('foo')

        assert assert_type(chained, Result[int, int | str]) == expected_chained
        assert assert_type(recovered, Result[str | int, str]) == expected_recovered
