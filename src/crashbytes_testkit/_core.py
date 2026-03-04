"""Test data builders — auto-generate dataclass instances from type hints."""

from __future__ import annotations

import dataclasses
import random
import string
import uuid
from datetime import date, datetime
from typing import Any, TypeVar, get_type_hints

T = TypeVar("T")

_counter = 0


def _next_id() -> int:
    global _counter  # noqa: PLW0603
    _counter += 1
    return _counter


def _random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _generate_value(type_hint: Any, field_name: str = "") -> Any:
    """Generate a plausible value for a given type hint."""
    origin = getattr(type_hint, "__origin__", None)
    args = getattr(type_hint, "__args__", ())

    # Handle Union types (Optional[X], X | Y, etc.)
    import types
    import typing
    if origin is typing.Union or isinstance(type_hint, types.UnionType):
        type_args = args if args else getattr(type_hint, "__args__", ())
        non_none = [a for a in type_args if a is not type(None)]
        if non_none:
            return _generate_value(non_none[0], field_name)
        return None

    if type_hint is str:
        return f"{field_name}_{_random_string()}" if field_name else _random_string()
    if type_hint is int:
        return _next_id()
    if type_hint is float:
        return round(random.uniform(0.0, 100.0), 2)
    if type_hint is bool:
        return random.choice([True, False])
    if type_hint is bytes:
        return _random_string().encode()
    if type_hint is datetime:
        return datetime(2024, 1, 1, 12, 0, 0)
    if type_hint is date:
        return date(2024, 1, 1)

    # list[X]
    if origin is list:
        inner = args[0] if args else str
        return [_generate_value(inner, field_name) for _ in range(2)]

    # dict[K, V]
    if origin is dict:
        k_type = args[0] if args else str
        v_type = args[1] if len(args) > 1 else str  # type: ignore[misc]
        return {_generate_value(k_type): _generate_value(v_type) for _ in range(2)}

    # set[X]
    if origin is set:
        inner = args[0] if args else str
        return {_generate_value(inner, field_name) for _ in range(2)}

    # tuple[X, ...]
    if origin is tuple:
        if args:
            return tuple(_generate_value(a, field_name) for a in args if a is not Ellipsis)
        return ()

    # UUID
    if type_hint is uuid.UUID:
        return uuid.uuid4()

    # Nested dataclass
    if dataclasses.is_dataclass(type_hint) and isinstance(type_hint, type):
        return _create_instance(type_hint)

    # Fallback
    return None


def _create_instance(cls: type[T], overrides: dict[str, Any] | None = None) -> T:
    """Create an instance of *cls* with auto-generated values."""
    hints = get_type_hints(cls)
    kwargs: dict[str, Any] = {}

    for field in dataclasses.fields(cls):  # type: ignore[arg-type]
        if overrides and field.name in overrides:
            kwargs[field.name] = overrides[field.name]
        elif field.default is not dataclasses.MISSING:
            kwargs[field.name] = field.default
        elif field.default_factory is not dataclasses.MISSING:
            kwargs[field.name] = field.default_factory()
        else:
            type_hint = hints.get(field.name, str)
            kwargs[field.name] = _generate_value(type_hint, field.name)

    return cls(**kwargs)


class Fixture:
    """Auto-generate test data from dataclass type hints."""

    @staticmethod
    def create(cls: type[T], **overrides: Any) -> T:
        """Create a single instance of *cls*."""
        if not dataclasses.is_dataclass(cls):
            raise TypeError(f"{cls.__name__} is not a dataclass")
        return _create_instance(cls, overrides or None)

    @staticmethod
    def create_many(cls: type[T], count: int = 3, **overrides: Any) -> list[T]:
        """Create *count* instances of *cls*."""
        return [Fixture.create(cls, **overrides) for _ in range(count)]


class Builder:
    """Fluent builder for constructing test data."""

    def __init__(self, cls: type[Any]) -> None:
        if not dataclasses.is_dataclass(cls):
            raise TypeError(f"{cls.__name__} is not a dataclass")
        self._cls = cls
        self._overrides: dict[str, Any] = {}

    def with_field(self, name: str, value: Any) -> Builder:
        """Set a specific field value."""
        self._overrides[name] = value
        return self

    def build(self) -> Any:
        """Build the instance."""
        return _create_instance(self._cls, self._overrides)

    def build_many(self, count: int = 3) -> list[Any]:
        """Build *count* instances."""
        return [self.build() for _ in range(count)]
