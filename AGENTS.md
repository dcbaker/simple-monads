# Repository Guidelines

## Project

`simple_monads` is a typed Python library implementing `Maybe` and `Result` types. Supported Python versions start at 3.11. Keep public APIs and runtime dependencies small.

## Development

- Install development dependencies with `python -m pip install -e '.[test,lint]'`.
- Run tests and doctests with `pytest`.
- Run strict type checking with `mypy`.
- Check lint and formatting with `ruff check .` and `ruff format --check .`.

## Code and Tests

- Follow `.editorconfig`: use 4-space indentation by default and 2 spaces for YAML, TOML, and JSON; use UTF-8 with LF line endings, trim trailing whitespace, and end files with a newline.
- Follow Ruff's configured style: single-quoted strings and a 100-character line limit.
- Keep type annotations compatible with the configured strict mypy checks. The package includes `py.typed`.
- Put behavioral tests in the matching module under `tests/` (`test_maybe.py` or `test_result.py`). Use pytest and follow the existing nested test-class organization.
- Mark coroutine tests with `pytest.mark.asyncio`; the pytest configuration also runs doctests in package modules.
- Add or update tests for behavior changes, including both success and error/empty cases where relevant.
