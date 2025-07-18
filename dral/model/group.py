from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from inspect import getmembers
from typing import Any, TypeVar

from .register import Register

GroupInstanceType = TypeVar("GroupInstanceType", bound="Group")
GroupType = TypeVar("GroupType", bound=type)


class Group:
    def __init__(self) -> None:
        self._name: str = ""
        self._address: int = 0
        self._offset: list[int] = []
        self._size: int = 1
        self._index: int = 0

    def __str__(self) -> str:
        return self._name

    def __len__(self) -> int:
        return self._size

    def __getitem__(self: GroupInstanceType, index: int) -> GroupInstanceType:
        if not isinstance(index, int):
            raise TypeError(f"Index must be an integer, got {type(index).__name__}")
        if index < 0:
            raise IndexError("Index must be a non-negative integer")
        if index >= len(self):
            raise IndexError(f"Index {index} out of range for group {self._name}")
        self._index = index
        return self

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> int:
        return self._address + self._offset[self._index]

    @property
    def offset(self) -> int:
        return self._offset[self._index]


def _setup_children(cls: GroupType, size: int, children_type: type) -> GroupType:
    children = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, children_type)}
    for attr, value in children.items():
        instances = tuple(deepcopy(value) for _ in range(size))
        setattr(cls, f"_{attr}", instances)

    for attr, _ in children.items():

        def getter(self: GroupType, attr: str = attr) -> Any:
            child = getattr(self, f"_{attr}")[self._index]  # type: ignore[attr-defined]
            self._index = 0  # type: ignore[attr-defined]
            return child

        def setter(self: GroupType, value: Any, attr: str = attr) -> None:
            raise AttributeError(f"Cannot set value directly on {attr}. Use {attr}.value = <value> instead.")

        setattr(cls, attr, property(getter, setter))

    return cls


def _setup_registers(cls: GroupType, size: int) -> GroupType:
    return _setup_children(cls, size, Register)


def _setup_groups(cls: GroupType, size: int) -> GroupType:
    return _setup_children(cls, size, Group)


def _setup_init(cls: GroupType, name: str, address: int, offset: list[int], size: int) -> GroupType:
    init = getattr(cls, "__init__", None)

    registers = getmembers(cls, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
    groups = getmembers(cls, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))

    def __init__(self: GroupType) -> None:
        if init is not None:
            init(self)
        self._name = name  # type: ignore[attr-defined]
        self._offset = offset  # type: ignore[attr-defined]
        self._size = size  # type: ignore[attr-defined]
        for attr, value in registers:
            setattr(self, attr, tuple(deepcopy(x) for x in value))
        for attr, value in groups:
            setattr(self, attr, tuple(deepcopy(x) for x in value))
        self._update_address(address, offset)  # type: ignore[attr-defined]

    cls.__init__ = __init__  # type: ignore[misc]
    return cls


def _deepcopy(self: GroupInstanceType, memo: dict[int, Any]) -> GroupInstanceType:
    instance = copy(self)
    memo[id(self)] = instance
    registers = getmembers(instance, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
    for reg in registers:
        new = tuple(deepcopy(x, memo) for x in reg[1])
        setattr(instance, reg[0], new)
    groups = getmembers(instance, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))
    for group in groups:
        new = tuple(deepcopy(x, memo) for x in group[1])
        setattr(instance, group[0], new)
    return instance


def _update_address(self: GroupInstanceType, address: int, offset: list[int] | None = None) -> GroupInstanceType:
    self._address = address + self._address
    registers = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
    for i, reg in enumerate(registers):
        for j, instance in enumerate(reg[1]):
            offset2add = offset[j] if offset is not None else 0
            registers[i][1][j]._address = address + instance._address + offset2add

    groups = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))
    for i, group in enumerate(groups):
        for j, _ in enumerate(group[1]):
            offset2add = offset[j] if offset is not None else 0
            groups[i][1][j]._update_address(address + offset2add)

    return self


def _setup_methods(cls: GroupType) -> GroupType:
    cls.__deepcopy__ = _deepcopy  # type: ignore[attr-defined]
    cls._update_address = _update_address  # type: ignore[attr-defined]
    return cls


def group(name: str, address: int, offset: list[int] | int, size: int = 1) -> Callable[[GroupType], GroupType]:
    if isinstance(offset, list):
        size = len(offset)
    else:
        offset = [0] + [offset + (i * offset) for i in range(size - 1)]

    if offset[0] != 0:
        raise ValueError("The first offset must be 0")

    def decorator(cls: GroupType) -> GroupType:
        cls = _setup_methods(cls)
        cls = _setup_registers(cls, size)
        cls = _setup_groups(cls, size)
        cls = _setup_init(cls, name, address, offset, size)

        return cls

    return decorator
