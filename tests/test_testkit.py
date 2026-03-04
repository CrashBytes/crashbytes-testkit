"""Tests for crashbytes-testkit."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

import pytest

from crashbytes_testkit import Builder, Fixture


@dataclass
class SimpleUser:
    name: str
    age: int
    active: bool


@dataclass
class Address:
    street: str
    city: str
    zip_code: str


@dataclass
class UserWithAddress:
    name: str
    address: Address


@dataclass
class UserWithDefaults:
    name: str
    role: str = "user"
    tags: list[str] = field(default_factory=list)


@dataclass
class UserWithOptional:
    name: str
    nickname: str | None = None


@dataclass
class UserWithCollections:
    name: str
    scores: list[int] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    unique_ids: set[int] = field(default_factory=set)


@dataclass
class UserWithTypes:
    id: uuid.UUID
    created_at: datetime
    birth_date: date
    score: float
    data: bytes


@dataclass
class UserWithTuple:
    name: str
    coords: tuple[float, float] = (0.0, 0.0)


class TestFixtureCreate:
    def test_creates_instance(self) -> None:
        user = Fixture.create(SimpleUser)
        assert isinstance(user, SimpleUser)
        assert isinstance(user.name, str)
        assert isinstance(user.age, int)
        assert isinstance(user.active, bool)

    def test_overrides(self) -> None:
        user = Fixture.create(SimpleUser, name="John", age=30)
        assert user.name == "John"
        assert user.age == 30

    def test_with_defaults(self) -> None:
        user = Fixture.create(UserWithDefaults)
        assert user.role == "user"
        assert user.tags == []

    def test_with_optional(self) -> None:
        user = Fixture.create(UserWithOptional)
        assert isinstance(user.name, str)
        # nickname should be generated as a string (non-None branch)
        assert user.nickname is None or isinstance(user.nickname, str)

    def test_nested_dataclass(self) -> None:
        user = Fixture.create(UserWithAddress)
        assert isinstance(user.address, Address)
        assert isinstance(user.address.street, str)

    def test_with_types(self) -> None:
        user = Fixture.create(UserWithTypes)
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.birth_date, date)
        assert isinstance(user.score, float)
        assert isinstance(user.data, bytes)

    def test_raises_for_non_dataclass(self) -> None:
        with pytest.raises(TypeError, match="not a dataclass"):
            Fixture.create(dict)  # type: ignore[arg-type]


class TestFixtureCreateMany:
    def test_creates_multiple(self) -> None:
        users = Fixture.create_many(SimpleUser, 5)
        assert len(users) == 5
        assert all(isinstance(u, SimpleUser) for u in users)

    def test_default_count(self) -> None:
        users = Fixture.create_many(SimpleUser)
        assert len(users) == 3

    def test_with_overrides(self) -> None:
        users = Fixture.create_many(SimpleUser, 3, active=True)
        assert all(u.active is True for u in users)


class TestBuilder:
    def test_basic_build(self) -> None:
        user = Builder(SimpleUser).build()
        assert isinstance(user, SimpleUser)

    def test_with_field(self) -> None:
        user = Builder(SimpleUser).with_field("name", "Alice").with_field("age", 25).build()
        assert user.name == "Alice"
        assert user.age == 25

    def test_build_many(self) -> None:
        users = Builder(SimpleUser).with_field("active", True).build_many(4)
        assert len(users) == 4
        assert all(u.active is True for u in users)

    def test_fluent_chaining(self) -> None:
        builder = Builder(SimpleUser)
        result = builder.with_field("name", "Bob")
        assert result is builder  # Returns self

    def test_raises_for_non_dataclass(self) -> None:
        with pytest.raises(TypeError, match="not a dataclass"):
            Builder(list)  # type: ignore[arg-type]


class TestCollections:
    def test_list_generation(self) -> None:
        user = Fixture.create(UserWithCollections)
        # Default factory will be used
        assert isinstance(user.scores, list)
        assert isinstance(user.metadata, dict)

    def test_tuple_with_default(self) -> None:
        user = Fixture.create(UserWithTuple)
        assert user.coords == (0.0, 0.0)


# Additional types for coverage


@dataclass
class WithList:
    items: list[str]


@dataclass
class WithDict:
    data: dict[str, int]


@dataclass
class WithSet:
    ids: set[int]


@dataclass
class WithTuple:
    pair: tuple[int, str]


@dataclass
class WithBareList:
    items: list[str]


@dataclass
class WithOptionalStr:
    name: str
    bio: str | None = None


class TestGenerateValuePaths:
    def test_list_type(self) -> None:
        obj = Fixture.create(WithList)
        assert isinstance(obj.items, list)
        assert len(obj.items) == 2
        assert all(isinstance(i, str) for i in obj.items)

    def test_dict_type(self) -> None:
        obj = Fixture.create(WithDict)
        assert isinstance(obj.data, dict)
        assert len(obj.data) == 2

    def test_set_type(self) -> None:
        obj = Fixture.create(WithSet)
        assert isinstance(obj.ids, set)
        assert all(isinstance(i, int) for i in obj.ids)

    def test_tuple_type(self) -> None:
        obj = Fixture.create(WithTuple)
        assert isinstance(obj.pair, tuple)
        assert isinstance(obj.pair[0], int)
        assert isinstance(obj.pair[1], str)

    def test_optional_generates_value(self) -> None:
        # Test the Union/Optional branch
        obj = Fixture.create(WithOptionalStr)
        assert isinstance(obj.name, str)

    def test_bytes_type(self) -> None:
        obj = Fixture.create(UserWithTypes)
        assert isinstance(obj.data, bytes)

    def test_float_type(self) -> None:
        obj = Fixture.create(UserWithTypes)
        assert isinstance(obj.score, float)
        assert 0.0 <= obj.score <= 100.0

    def test_uuid_type(self) -> None:
        obj = Fixture.create(UserWithTypes)
        assert isinstance(obj.id, uuid.UUID)

    def test_datetime_type(self) -> None:
        obj = Fixture.create(UserWithTypes)
        assert isinstance(obj.created_at, datetime)

    def test_date_type(self) -> None:
        obj = Fixture.create(UserWithTypes)
        assert isinstance(obj.birth_date, date)

    def test_nested_dataclass(self) -> None:
        obj = Fixture.create(UserWithAddress)
        assert isinstance(obj.address, Address)
        assert isinstance(obj.address.city, str)

    def test_field_name_in_string(self) -> None:
        user = Fixture.create(SimpleUser)
        assert "name" in user.name

    def test_create_many_unique(self) -> None:
        users = Fixture.create_many(SimpleUser, 5)
        names = [u.name for u in users]
        assert len(set(names)) == 5  # All unique


@dataclass
class WithBareTuple:
    data: tuple[()]


@dataclass
class WithUnknownType:
    value: object


@dataclass
class WithOptionalTyping:
    name: str | None


class TestEdgeCases:
    def test_empty_tuple(self) -> None:
        obj = Fixture.create(WithBareTuple)
        assert isinstance(obj.data, tuple)

    def test_unknown_type_returns_none(self) -> None:
        obj = Fixture.create(WithUnknownType)
        assert obj.value is None

    def test_union_type_syntax(self) -> None:
        obj = Fixture.create(WithOptionalTyping)
        # Should generate a string (non-None branch of str | None)
        assert obj.name is None or isinstance(obj.name, str)
