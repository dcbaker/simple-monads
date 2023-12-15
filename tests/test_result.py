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
