# crashbytes-testkit

Test data builders for Python — auto-generate dataclass instances from type hints.

## Install

```bash
pip install crashbytes-testkit
```

## Usage

```python
from dataclasses import dataclass
from crashbytes_testkit import Fixture, Builder

@dataclass
class User:
    name: str
    age: int
    email: str

# Auto-generate from type hints
user = Fixture.create(User)
users = Fixture.create_many(User, 5)

# Override specific fields
admin = Fixture.create(User, name="Admin", age=30)

# Fluent builder
user = (
    Builder(User)
    .with_field("name", "Alice")
    .with_field("age", 25)
    .build()
)
```

Supports: `str`, `int`, `float`, `bool`, `bytes`, `datetime`, `date`, `UUID`, `list[T]`, `dict[K,V]`, `set[T]`, `tuple`, `Optional[T]`, nested dataclasses.

## License

MIT
