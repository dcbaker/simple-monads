# SPDX-License-Identifier: MIT
# Copyright © 2023-2024 Dylan Baker

"""An implementation of an Option type."""

from __future__ import annotations
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, TypeVar, ParamSpec, Generic

if TYPE_CHECKING:
    from typing import Callable, Awaitable

    from .result import Result

P = ParamSpec('P')
R = TypeVar('R')
E = TypeVar('E')
T = TypeVar('T')
U = TypeVar('U')

__all__ = [
    'EmptyMaybeError',
    'Maybe',
    'Nothing',
    'Something',
    'maybe',
    'stop',
    'stop_async',
    'unwrap_maybe',
    'unwrap_maybe_async',
    'wrap_maybe',
    'wrap_maybe_async',
]


class Propagation(Exception):
    """Uses exception handling to propagate up."""

    def __init__(self) -> None:
        super().__init__('Uncaught Propagation, did you forget to decorate '
                         'function with @simple_monads.maybe.stop?')


class EmptyMaybeError(Exception):

    """Raised when calling :meth:`Maybe.unwrap` on an empty Maybe.

    It is advised to *not* catch this exception, as it is usually the result of
    an incorrect assumption in the code, or it truly is fatal.

    In the former case replacing :meth:`Maybe.unwrap` with
    :meth:`Maybe.unwrap_or` or :meth:`Maybe.get` may be mor appropriate.
    """


class Maybe(Generic[T]):

    """Base Class for Option, do not directly instantiate.

    This class is not useful for instantiation, instead use either
    :class:`Something` or :class:`Nothing`. This class is useful for isinstance
    """

    @staticmethod
    def is_something() -> bool:
        """Is this Something?

        It is *strongly* recommended to use this method an not
        :func:`isinstance`.

        >>> maybe('foo').is_something()
        True

        >>> maybe(None).is_something()
        False

        :return: True if this is Something otherwise False
        """
        raise NotImplementedError()

    @staticmethod
    def is_nothing() -> bool:
        """Is this Nothing?

        It is *strongly* recommended to use this method an not
        :func:`isinstance`.

        >>> maybe('foo').is_nothing()
        False

        >>> maybe(None).is_nothing()
        True

        :return: True if this is Nothing otherwise False
        """
        raise NotImplementedError()

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        """Transforms the held value using the callback

        If this Maybe is Nothing, then Nothing is returned

        >>> maybe(500).map(str).unwrap()
        '500'

        >>> maybe(None).map(str).is_nothing()
        True

        :param cb: A callback transforming the held value from T to U
        :return: A new Maybe holding the transformed value
        """
        raise NotImplementedError()

    async def map_async(self, cb: Callable[[T], Awaitable[U]]) -> Maybe[U]:
        """Transforms the held value using the callback asynchronously.

        If this Maybe is Nothing, then Nothing is returned

        >>> import asyncio
        >>> async def foo(a: int) -> str:
        ...     return str(a)
        >>> asyncio.run(maybe(500).map_async(foo)).unwrap()
        '500'
        >>> asyncio.run(maybe(None).map_async(foo)).is_nothing()
        True

        :param cb: A callback transforming the held value from T to awaitable U
        :return: A new Maybe holding the transformed value
        """
        raise NotImplementedError()


    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        >>> maybe(500).map_or(str, '0').unwrap()
        '500'

        >>> maybe(None).map_or(str, '0').unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: A value to use for Nothing
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    async def map_or_async(self, cb: Callable[[T], Awaitable[U]], fallback: U) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value asynchronously.

        >>> import asyncio
        >>> async def foo(a: int) -> str:
        ...     return str(a)

        >>> asyncio.run(maybe(500).map_or_async(foo, '0')).unwrap()
        '500'

        >>> asyncio.run(maybe(None).map_or_async(foo, '0')).unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: A value to use for Nothing
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        """Transform the held value using the callback, or use the fallback
        value.

        >>> maybe(500).map_or_else(str, lambda: '0').unwrap()
        '500'

        >>> maybe(None).map_or_else(str, lambda: '0').unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: callable returning a value U
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    async def map_or_else_async(
            self, cb: Callable[[T], Awaitable[U]], fallback: Callable[[], Awaitable[U]]) -> Maybe[U]:  # pylint: disable=line-too-long
        """Transform the held value using the callback, or use the fallback
        value asynchronously.

        >>> import asyncio
        >>> async def fb() -> str:
        ...     return '0'

        >>> async def cb(v: int) -> str:
        ...     return str(v)

        >>> asyncio.run(maybe(500).map_or_else_async(cb, fb)).unwrap()
        '500'

        >>> asyncio.run(maybe(None).map_or_else_async(cb, fb)).unwrap()
        '0'

        :param cb: A callback which will transform Something[T] into Something[U]
        :param fallback: callable returning a value U
        :return: A Something containing the transformation or the fallback value
        """
        raise NotImplementedError()

    def get(self, fallback: T | None = None) -> T | None:
        """Get the held value.

        Works much like Python's normal `.get()` methods, but never throws.

        >>> maybe('500').get()
        '500'

        >>> maybe(None).get('a')
        'a'

        :param fallback: A value to use if this is Nothing
        :return: The value or fallback
        """
        raise NotImplementedError()

    def unwrap(self, msg: str | None = None) -> T:
        """Get the held value or throw an Exception.

        >>> maybe('foo').unwrap()
        'foo'

        >>> maybe(None).unwrap()
        Traceback (most recent call last):
          ...
        simple_monads.maybe.EmptyMaybeError: Attempted to unwrap Nothing

        >>> maybe(None).unwrap("Expected a result")
        Traceback (most recent call last):
          ...
        simple_monads.maybe.EmptyMaybeError: Expected a result

        :param msg: The error message, otherwise a default is used
        :raises EmptyMaybeError: If this is Nothing
        :return: The held value
        """
        raise NotImplementedError()

    def unwrap_or(self, fallback: T) -> T:
        """Get the value or a fallback value.

        Unlike get() doesn't provide a fallback of None, which narrows type
        checking.

        >>> maybe(500).unwrap_or(0)
        500

        >>> maybe(None).unwrap_or(0)
        0

        :param fallback: The fallback to return
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        """Get the value or call the fallback to get a value

        >>> maybe(500).unwrap_or_else(lambda: 0)
        500

        >>> maybe(None).unwrap_or_else(lambda: 0)
        0

        :param fallback: A callable returning a type T
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    async def unwrap_or_else_async(self, fallback: Callable[[], Awaitable[T]]) -> T:
        """Get the value or call the fallback to get a value

        >>> import asyncio
        >>> async def fb():
        ...     return 0

        >>> asyncio.run(maybe(500).unwrap_or_else_async(fb))
        500

        >>> asyncio.run(maybe(None).unwrap_or_else_async(fb))
        0

        :param fallback: An async callable returning a type T
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Run a callback on the value if it is Something

        >>> maybe(500).and_then(lambda x: maybe(0)).unwrap()
        0

        :param cb: A callback to run on the held value or Something()
        :return: A Maybe[U] with the result of the callback or nothing
        """
        raise NotImplementedError()

    async def and_then_async(self, cb: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        """Run a callback on the value if it is Something

        >>> import asyncio
        >>> async def cb(v: int):
        ...     return Something(str(v))
        >>> asyncio.run(maybe(500).and_then_async(cb)).unwrap()
        '500'

        :param cb: A callback to run on the held value or Something()
        :return: A Maybe[U] with the result of the callback or nothing
        """
        raise NotImplementedError()

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        """Run a callback to get a value if this is Nothing or return self.

        >>> maybe(500).or_else(lambda: maybe(100)).unwrap()
        500

        >>> maybe(None).or_else(lambda: maybe(100)).unwrap()
        100

        :param fallback: A callback to run if this is Nothing returning a
            Maybe[T]
        :return: A Maybe[T], which is self unchanged if this Something,
            otherwise the result of fallback
        """
        raise NotImplementedError()

    async def or_else_async(self, fallback: Callable[[], Awaitable[Maybe[T]]]) -> Maybe[T]:
        """Run a callback to get a value if this is Nothing or return self.

        >>> import asyncio
        >>> async def cb():
        ...     return maybe(100)
        >>> asyncio.run(maybe(500).or_else_async(cb)).unwrap()
        500

        >>> asyncio.run(maybe(None).or_else_async(cb)).unwrap()
        100

        :param fallback: An async callback to run if this is Nothing returning a
            Maybe[T]
        :return: A Maybe[T], which is self unchanged if this Something,
            otherwise the result of fallback
        """
        raise NotImplementedError()

    def ok_or(self, err: E) -> Result[T, E]:
        """Convert this Option to a Result.

        If the Option is Something, that will be placed in the Success value,
        otherwise the Error value of E will be used.

        >>> maybe(0).ok_or("WHAT!").unwrap()
        0

        >>> maybe(None).ok_or("WHAT!").unwrap_err()
        'WHAT!'

        :param err: An error if this is Nothing
        :return: A result with the held value as a Success or an Error
        """
        raise NotImplementedError()

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        """Convert this Option to a Result.

        If the Option is Something, that will be placed in the Success value,
        otherwise the Error value of E will be used.

        >>> maybe(0).ok_or_else(lambda: "WHAT!").unwrap()
        0

        >>> maybe(None).ok_or_else(lambda: "WHAT!").unwrap_err()
        'WHAT!'

        :param err: An callable returning a type E
        :return: A result with the held value as a Success or an Error
        """
        raise NotImplementedError()

    async def ok_or_else_async(self, err: Callable[[], Awaitable[E]]) -> Result[T, E]:
        """Convert this Option to a Result asynchronously.

        If the Option is Something, that will be placed in the Success value,
        otherwise the Error value of E will be used.

        >>> import asyncio
        >>> async def cb():
        ...     return "WHAT!"
        >>> asyncio.run(maybe(0).ok_or_else_async(cb)).unwrap()
        0

        >>> asyncio.run(maybe(None).ok_or_else_async(cb)).unwrap_err()
        'WHAT!'

        :param err: An async callable returning a type E
        :return: A result with the held value as a Success or an Error
        """
        raise NotImplementedError()

    def propagate(self) -> T:
        """Get the value, or propagate an error up the stack.

        This is achieved by throwing a special Exception, which is caught using
        the :func:`stop` decorator. This is ugly and an abuse of Exceptions,
        (control flow through Exceptions, which is bad, m'kay?). However, this
        is the only obvious portable way to implement this in Python.

        :return: The held value of a Success

        >>> @stop
        ... def func() -> Maybe[str]:
        ...     r: Maybe[str] = Nothing()
        ...     x = r.propagate()  # is now str, or thrown
        ...     return x == 'foo'

        >>> func()
        Nothing()
        """
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Something(Maybe[T]):

    """A Maybe that holds a value."""

    _held: T

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Something({self._held!r})"

    @staticmethod
    def is_something() -> bool:
        return True

    @staticmethod
    def is_nothing() -> bool:
        return False

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        return Something(cb(self._held))

    async def map_async(self, cb: Callable[[T], Awaitable[U]]) -> Maybe[U]:
        return Something(await cb(self._held))

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        return Something(cb(self._held))

    async def map_or_async(self, cb: Callable[[T], Awaitable[U]], fallback: U) -> Maybe[U]:
        return Something(await cb(self._held))

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        return Something(cb(self._held))

    async def map_or_else_async(
            self, cb: Callable[[T], Awaitable[U]], fallback: Callable[[], Awaitable[U]]) -> Maybe[U]:  # pylint: disable=line-too-long
        return Something(await cb(self._held))

    def get(self, fallback: T | None = None) -> T | None:
        return self._held

    def unwrap(self, msg: str | None = None) -> T:
        return self._held

    def unwrap_or(self, fallback: T) -> T:
        return self._held

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return self._held

    async def unwrap_or_else_async(self, fallback: Callable[[], Awaitable[T]]) -> T:
        return self._held

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return cb(self._held)

    async def and_then_async(self, cb: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        return await cb(self._held)

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        return self

    async def or_else_async(self, fallback: Callable[[], Awaitable[Maybe[T]]]) -> Maybe[T]:
        return self

    def ok_or(self, err: E) -> Result[T, E]:
        from .result import Success  # pylint: disable=import-outside-toplevel
        return Success(self._held)

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        from .result import Success  # pylint: disable=import-outside-toplevel
        return Success(self._held)

    async def ok_or_else_async(self, err: Callable[[], Awaitable[E]]) -> Result[T, E]:
        from .result import Success  # pylint: disable=import-outside-toplevel
        return Success(self._held)

    def propagate(self) -> T:
        return self._held


@dataclass(slots=True, frozen=True)
class Nothing(Maybe[T]):

    """A Maybe that does not hold a value."""

    def __bool__(self) -> bool:
        return False

    @staticmethod
    def is_something() -> bool:
        return False

    @staticmethod
    def is_nothing() -> bool:
        return True

    def map(self, cb: Callable[[T], U]) -> Maybe[U]:
        return Nothing()

    async def map_async(self, cb: Callable[[T], Awaitable[U]]) -> Maybe[U]:
        return Nothing()

    def map_or(self, cb: Callable[[T], U], fallback: U) -> Maybe[U]:
        return Something(fallback)

    async def map_or_async(self, cb: Callable[[T], Awaitable[U]], fallback: U) -> Maybe[U]:
        return Something(fallback)

    def map_or_else(self, cb: Callable[[T], U], fallback: Callable[[], U]) -> Maybe[U]:
        return Something(fallback())

    async def map_or_else_async(
            self, cb: Callable[[T], Awaitable[U]], fallback: Callable[[], Awaitable[U]]) -> Maybe[U]:  # pylint: disable=line-too-long
        return Something(await fallback())

    def get(self, fallback: T | None = None) -> T | None:
        return fallback

    def unwrap(self, msg: str | None = None) -> T:
        if msg is None:
            msg = 'Attempted to unwrap Nothing'
        raise EmptyMaybeError(msg)

    def unwrap_or(self, fallback: T) -> T:
        return fallback

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return fallback()

    async def unwrap_or_else_async(self, fallback: Callable[[], Awaitable[T]]) -> T:
        return await fallback()

    def and_then(self, cb: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing()

    async def and_then_async(self, cb: Callable[[T], Awaitable[Maybe[U]]]) -> Maybe[U]:
        return Nothing()

    def or_else(self, fallback: Callable[[], Maybe[T]]) -> Maybe[T]:
        return fallback()

    async def or_else_async(self, fallback: Callable[[], Awaitable[Maybe[T]]]) -> Maybe[T]:
        return await fallback()

    def ok_or(self, err: E) -> Result[T, E]:
        from .result import Error  # pylint: disable=import-outside-toplevel
        return Error(err)

    def ok_or_else(self, err: Callable[[], E]) -> Result[T, E]:
        from .result import Error  # pylint: disable=import-outside-toplevel
        return Error(err())

    async def ok_or_else_async(self, err: Callable[[], Awaitable[E]]) -> Result[T, E]:
        from .result import Error  # pylint: disable=import-outside-toplevel
        return Error(await err())

    def propagate(self) -> T:
        raise Propagation()


def maybe(result: T | None) -> Maybe[T]:
    """Convenience function to convert T | None into Maybe[T].

    This can convert python code using the standard T | None Optional.
    This works correctly only when None is not a valid member of T

    >>> maybe(0)
    Something(0)

    >>> maybe(None)
    Nothing()

    :param result: A None or T type to wrap
    :return: Nothing if result is None, else Something[T](result)
    """
    if result is None:
        return Nothing()
    return Something(result)


def wrap_maybe_async(f: Callable[P, Awaitable[R | None]]) -> Callable[P, Awaitable[Maybe[R]]]:
    """Decorator (or wrapper) for asynchronous python code.

    Converts code returning Awaitable[T | None] to return Awaitable[Maybe[T]]

    >>> import asyncio

    >>> @wrap_maybe_async
    ... async def func(arg: bool) -> str | None:
    ...     if arg:
    ...         return "yes!"
    ...     return None
    ...
    >>> asyncio.run(func(True))
    Something('yes!')

    >>> asyncio.run(func(False))
    Nothing()

    :param f: An async callable returning a type R or None
    :return: A new async callable return :class:`Maybe[R]`, where a non-null are
        :class:`Success`, and None is :class:`Nothing`
    """

    @wraps(f)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        return maybe(await f(*args, **kwargs))

    return inner


def wrap_maybe(f: Callable[P, R | None]) -> Callable[P, Maybe[R]]:
    """Decorator (or wrapper) for common python code.

    Converts code returning T | None to return Maybe[T]

    >>> @wrap_maybe
    ... def func(arg: bool) -> str | None:
    ...     if arg:
    ...         return "yes!"
    ...     return None
    ...
    >>> func(True)
    Something('yes!')

    >>> func(False)
    Nothing()

    >>> import os
    >>> f = wrap_maybe(os.environ.get)
    >>> f("Totally not there")
    Nothing()

    :param f: A callable returning a type R or None
    :return: A new callable return :class:`Maybe[R]`, where a non-null are
        :class:`Success`, and None is :class:`Nothing`
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        return maybe(f(*args, **kwargs))

    return inner


def unwrap_maybe_async(f: Callable[P, Awaitable[Maybe[R]]]) -> Callable[P, Awaitable[R | None]]:
    """Decorator (or wrapper) to convert back to common asynchronous Python.

    Converts code returning Awaitable[Maybe[T]] to Awaitable[T | None].

    This is meant to ease transitioning a codebase to using simple_monads, but
    allowing code to internally use Maybe, but return common Python Optional

    >>> import asyncio
    >>> async def raw(arg: str) -> Maybe[str]:
    ...     if arg:
    ...         return Something(arg)
    ...     return Nothing()

    >>> f = unwrap_maybe_async(raw)
    >>> asyncio.run(f("foo"))
    'foo'

    >>> @unwrap_maybe_async
    ... async def g(arg: str) -> str | None:
    ...     return await raw(arg)

    >>> asyncio.run(g("foo"))
    'foo'

    :param f: An async callable returning a :class:`Maybe[T]`
    :return: A new async callable returning a `T | None`
    """

    @wraps(f)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
        return (await f(*args, **kwargs)).get()

    return inner


def unwrap_maybe(f: Callable[P, Maybe[R]]) -> Callable[P, R | None]:

    """Decorator (or wrapper) to convert back to common Python.

    Converts code returning Maybe[T] to T | None.

    This is meant to ease transitioning a codebase to using simple_monads, but
    allowing code to internally use Maybe, but return common Python Optional

    >>> def raw(arg: str) -> Maybe[str]:
    ...     if arg:
    ...         return Something(arg)
    ...     return Nothing()

    >>> f = unwrap_maybe(raw)
    >>> f("foo")
    'foo'

    >>> @unwrap_maybe
    ... def g(arg: str) -> str | None:
    ...     return raw(arg)

    >>> g("foo")
    'foo'

    :param f: A callable returning a :class:`Maybe[T]`
    :return: A new callable returning a `T | None`
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
        return f(*args, **kwargs).get()

    return inner


def stop(f: Callable[P, Maybe[R]]) -> Callable[P, Maybe[R]]:
    """Decorator for functions that use :meth:`Maybe.propagate`.

    This is required to catch the propagated Error, and ensure that it is
    returned instead of continuing to go up the stack.

    >>> def g() -> Maybe[str]:
    ...     return Nothing()

    >>> @stop
    ... def f() -> Maybe[int]:
    ...     v = g()
    ...     v.propagate()
    ...     return v.map(int)

    >>> f()
    Nothing()

    :param f: The function to wrap
    :return: The original function wrapped to handle Propagation Exceptions
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        try:
            return f(*args, **kwargs)
        except Propagation:
            return Nothing()

    return inner


def stop_async(f: Callable[P, Awaitable[Maybe[R]]]) -> Callable[P, Awaitable[Maybe[R]]]:
    """Decorator for async functions that use :meth:`Result.propagate`.

    This is required to catch the propagated Error, and ensure that it is
    returned instead of continuing to go up the stack.

    >>> async def g() -> Maybe[str]:
    ...     return Nothing()

    >>> @stop_async
    ... async def f() -> Result[int, str]:
    ...     v = await g()
    ...     v.propagate()
    ...     x = v.map(int)
    ...     return x

    >>> import asyncio
    >>> asyncio.run(f())
    Nothing()

    :param f: The async function to wrap
    :return: The original function wrapped to handle Propagation Exceptions
    """

    @wraps(f)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> Maybe[R]:
        try:
            return await f(*args, **kwargs)
        except Propagation:
            return Nothing()

    return inner
