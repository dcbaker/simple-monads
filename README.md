# simple-monads

Small, typed Python implementations of `Maybe` (optional values) and `Result`
(success or error values). The package supports Python 3.11 and newer and has
no required runtime dependencies beyond `typing-extensions`.

## Installation

```sh
python -m pip install simple-py-monads
```

## Maybe: represent an optional value

Use `maybe()` to convert a value that may be `None`. A non-`None` value becomes
`Something`; `None` becomes `Nothing`.

```python
from simple_monads.maybe import maybe

name = maybe('Ada')
missing_name = maybe(None)

name.map(str.upper).unwrap_or('UNKNOWN')  # 'ADA'
missing_name.unwrap_or('UNKNOWN')  # 'UNKNOWN'
```

Use `map()` to transform a present value, or `and_then()` when the callback
already returns a `Maybe`:

```python
from simple_monads.maybe import Maybe, maybe, wrap


@wrap
def find_user_name(user_id: int) -> str | None:
    users = {1: 'Ada'}
    return users.get(user_id)


def normalize_name(name: str) -> Maybe[str]:
    return maybe(name.strip() or None)


display_name = find_user_name(1).and_then(normalize_name).unwrap_or('Guest')
```

`unwrap()` returns the held value but raises `EmptyMaybeError` for `Nothing`.
Prefer `unwrap_or()`, `unwrap_or_else()`, or `get()` when an empty value is an
expected outcome. `maybe(None)` means absence, so use `Something(None)` if
`None` itself is a value you need to preserve.

## Result: represent success or failure

`Success(value)` and `Error(error)` make either outcome explicit. The
`@wrap(...)` decorator catches the specified exception type and returns it as
an `Error`.

```python
from simple_monads.result import Error, Result, wrap


@wrap(ValueError)
def parse_count(text: str) -> int:
    return int(text)


parsed: Result[int, ValueError] = parse_count('42')
count = parsed.map(lambda value: value * 2).unwrap_or(0)  # 84

failed = parse_count('not a number')
assert isinstance(failed, Error)
assert failed.unwrap_or(0) == 0
```

Use `and_then()` to chain a function that returns another `Result`,
`map_err()` to transform an error, and `or_else()` to recover from one.
`unwrap()` returns a `Success` value and raises `UnwrapError` for an `Error`;
use `unwrap_or()` or `unwrap_or_else()` for a fallback. `unwrap_err()` returns
the error value.

## Async functions

The mapping and wrapping helpers also support coroutines:

```python
from simple_monads.result import Result, wrap


@wrap(ValueError)
async def fetch_count(text: str) -> int:
    return int(text)


async def twice(value: int) -> int:
    return value * 2


async def doubled_count(text: str) -> Result[int, ValueError]:
    return await (await fetch_count(text)).map_async(twice)
```

`Maybe` also provides `map_async()` and `and_then_async()`. For fallbacks,
`unwrap_or_else_async()` accepts an async callable.

## Early propagation

For functions that need to return immediately when a `Maybe` is empty or a
`Result` is an error, call `propagate()` inside a function decorated with
`stop`:

```python
from simple_monads.result import Error, Result, Success, stop


@stop
def calculate(value: Result[int, str]) -> Result[int, str]:
    number = value.propagate()
    return Success(number // 2)


assert calculate(Success(20)) == Success(10)
assert calculate(Error('invalid input')) == Error('invalid input')
```

`stop` catches the internal propagation signal and returns the empty/error
value. It can also decorate async functions. Keep it on the inner function when
combining with `result.unwrap`; `stop` must be applied before `unwrap`.

## Pydantic

The Maybe and Result classes are supported for serialization and vaildation in pydantic.

## Development

Install the test and lint dependencies, then run the checks:

```sh
python -m pip install -e '.[test,lint]'
pytest
mypy
ruff check .
ruff format --check .
```

The project source is available on [GitHub](https://github.com/dcbaker/simple-monads).
