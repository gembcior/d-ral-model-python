from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, cast

from .access import AccessType
from .field import Field


class Register:
    def __init__(self):
        print(f"Initializing register {self.__class__.__name__}")
        self._name = ""
        self._address = 0
        self._access = AccessType.ReadWrite
        self._value = 0
        self._fields = self._get_all_fields()
        self._index = 0

    def _get_all_fields(self) -> tuple[Field, ...]:
        fields = list(filter(lambda x: isinstance(x, Field), self.__dict__.values()))
        sorted_fields = sorted(fields, key=lambda x: x.position)
        return tuple(sorted_fields)

    def __copy__(self):
        return type(self)()

    def __setitem__(self, key: int, value: int) -> None:
        self._fields[key].value = value

    def __getitem__(self, key: int) -> Field:
        return self._fields[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._fields):
            item = self._fields[self._index]
            self._index += 1
            return item
        else:
            self._index = 0
            raise StopIteration

    def __str__(self) -> str:
        return self._name

    def __len__(self) -> int:
        return len(self._fields)

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> int:
        return self._address

    @property
    def access(self) -> AccessType:
        return self._access

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        for _, field in self.__dict__.items():
            if isinstance(field, Field):
                field.value = (value >> field.position) & field.mask
        self._value = value


RegisterType = TypeVar("RegisterType", bound=type)


def register(name: str, address: int, access: AccessType = AccessType.ReadWrite) -> Callable[[RegisterType], RegisterType]:
    def decorator(cls: RegisterType) -> RegisterType:
        init = getattr(cls, "__init__", None)

        def __init__(self):
            if init is not None:
                init(self)
            self._name = name
            self._address = address
            self._access = access

        cls.__init__ = __init__  # type: ignore[method-assign]
        return cast(RegisterType, cls)

    return decorator
