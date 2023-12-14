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
