from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from inspect import getmembers
from typing import TypeVar, cast

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
        return cast(GroupInstanceType, self)

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

        def getter(self, attr=attr):
            child = getattr(self, f"_{attr}")[self._index]
            self._index = 0
            return child

        def setter(self, value, attr=attr):
            raise AttributeError(f"Cannot set value directly on {attr}. Use {attr}.value = <value> instead.")

        setattr(cls, attr, property(getter, setter))

    return cast(GroupType, cls)


def _setup_registers(cls: GroupType, size: int) -> GroupType:
    return _setup_children(cls, size, Register)


def _setup_groups(cls: GroupType, size: int) -> GroupType:
    return _setup_children(cls, size, Group)


def _setup_init(cls: GroupType, name: str, address: int, offset: list[int], size: int) -> GroupType:
    init = getattr(cls, "__init__", None)

    def __init__(self):
        if init is not None:
            init(self)
        self._name = name
        self._offset = offset
        self._size = size
        self._update_address(address, offset)

    cls.__init__ = __init__  # type: ignore[method-assign]
    return cast(GroupType, cls)


def _deepcopy(self: GroupInstanceType, memo) -> GroupInstanceType:
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
    return cast(GroupInstanceType, instance)


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

    return cast(GroupInstanceType, self)


def _setup_methods(cls: GroupType) -> GroupType:
    cls.__deepcopy__ = _deepcopy  # type: ignore[method-assign]
    cls._update_address = _update_address  # type: ignore[method-assign]
    return cast(GroupType, cls)


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

        return cast(GroupType, cls)

    return decorator
