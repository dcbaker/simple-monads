# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker


from __future__ import annotations

import pytest

from pyadt.result import *


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
            assert e.map(int) == e

        def test_success(self) -> None:
            assert Success('1').map(int) == Success(1)

    class TestMapErr:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_err(int) == Error(1)

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_err(int) == s

    class TestMapOr:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_or('foo', lambda _: 'bar') == 'foo'

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_or('foo', lambda _: 'bar') == 'bar'

    class TestMapOrElse:

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.map_or_else(lambda: 'foo', lambda _: 'bar') == 'foo'

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.map_or_else(lambda: 'foo', lambda _: 'bar') == 'bar'

    class TestAndThen:

        @staticmethod
        def _cb(res: str) -> Result[int, str]:
            return Success(int(res))

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.and_then(self._cb) == e

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.and_then(self._cb) == Success(1)

    class TestOrElse:

        @staticmethod
        def _cb(res: str) -> Result[int, str]:
            return Error(int(res))

        def test_error(self) -> None:
            e: Result[str, str] = Error('1')
            assert e.or_else(self._cb) == Error(1)

        def test_success(self) -> None:
            s: Success[str, str] = Success('1')
            assert s.or_else(self._cb) == s

    class TestErr:

        def test_error(self) -> None:
            e: Result[str, int] = Error(4)
            assert e.err().unwrap() == 4

        def test_success(self) -> None:
            s: Result[str, int] = Success(4)
            assert s.err().is_nothing()

    class TestOk:

        def test_error(self) -> None:
            e: Result[str, int] = Error(4)
            assert e.ok().is_nothing()

        def test_success(self) -> None:
            s: Result[str, int] = Success(4)
            assert s.ok().unwrap() == 4
