# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from inspect import getmembers
from typing import Any, TypeVar

from .access import AccessType
from .field import Field


class Register:
    def __init__(self) -> None:
        self._name: str = ""
        self._address: int = 0
        self._access: AccessType = AccessType.ReadWrite
        self._description: str = ""
        self._value: int = 0
        self._fields: tuple[Field, ...] = self._get_all_fields()

    def _get_all_fields(self) -> tuple[Field, ...]:
        field_members = getmembers(self, lambda x: isinstance(x, Field))
        fields = [x[1] for x in field_members if x[0].startswith("_")]
        return tuple(sorted(fields, key=lambda x: x.position))

    def __str__(self) -> str:
        return self._name

    def _clear_value(self) -> None:
        for field in self._fields:
            self._value &= ~(field.mask << field.position)

    def _set_value(self) -> None:
        self._clear_value()
        for field in self._fields:
            self._value |= (field.value & field.mask) << field.position

    def _update_fields(self) -> None:
        for field in self._fields:
            field.value = (self._value >> field.position) & field.mask

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
    def description(self) -> str:
        return self._description

    @property
    def value(self) -> int:
        self._set_value()
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value
        self._update_fields()


RegisterInstanceType = TypeVar("RegisterInstanceType", bound="Register")
RegisterType = TypeVar("RegisterType", bound=type)


def _setup_fields(cls: RegisterType) -> RegisterType:
    fields = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, Field)}
    for attr, field in fields.items():
        setattr(cls, f"_{attr}", field)

    for attr, _ in fields.items():

        def getter(self: RegisterType, attr: str = attr) -> Any:  # noqa: ANN401
            return getattr(self, f"_{attr}")

        def setter(self: RegisterType, value: Any, attr: str = attr) -> None:  # noqa: ANN401
            raise AttributeError(f"Cannot set value directly on {attr}. Use {attr}.value = <value> instead.")

        setattr(cls, attr, property(getter, setter))

    return cls


def _deepcopy(self: RegisterInstanceType, memo: dict[int, Any]) -> RegisterInstanceType:
    instance = copy(self)
    memo[id(self)] = instance
    fields = getmembers(instance, lambda x: isinstance(x, Field))
    fields = [x for x in fields if x[0].startswith("_")]
    for field in fields:
        new = deepcopy(field[1], memo)
        setattr(instance, field[0], new)
    instance._fields = instance._get_all_fields()
    return instance


def _setup_init(cls: RegisterType, name: str, address: int, access: AccessType, description: str) -> RegisterType:
    init = getattr(cls, "__init__", None)
    fields = getmembers(cls, lambda x: isinstance(x, Field))

    def __init__(self: RegisterType) -> None:  # noqa: N807
        if init is not None:
            init(self)
        self._name = name  # type: ignore[attr-defined]
        self._address = address  # type: ignore[attr-defined]
        self._access = access  # type: ignore[attr-defined]
        self._description = description  # type: ignore[attr-defined]
        for attr, value in fields:
            setattr(self, attr, deepcopy(value))

    cls.__init__ = __init__  # type: ignore[misc]
    return cls


def _setup_methods(cls: RegisterType) -> RegisterType:
    cls.__deepcopy__ = _deepcopy  # type: ignore[attr-defined]
    return cls


def register(name: str, address: int, access: AccessType = AccessType.ReadWrite, description: str = "") -> Callable[[RegisterType], RegisterType]:
    def decorator(cls: RegisterType) -> RegisterType:
        cls = _setup_methods(cls)
        cls = _setup_fields(cls)
        cls = _setup_init(cls, name, address, access, description)

        return cls

    return decorator
