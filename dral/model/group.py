from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import dataclass
from inspect import getmembers
from typing import TypeVar, cast

from rich import inspect as richInspect
from rich import print

from .register import Register

GroupInstanceType = TypeVar("GroupInstanceType", bound="Group")


class Group:
    def __init__(self) -> None:
        print(f"Initializing group {self.__class__.__name__}")
        self._name = ""
        self._address = 0
        self._offset = []
        self._size = 1
        self._index = 0

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

    def __deepcopy__(self: GroupInstanceType, memo) -> GroupInstanceType:
        instance = copy(self)
        memo[id(self)] = instance
        registers = getmembers(instance, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
        for reg in registers:
            new = tuple(deepcopy(x, memo) for x in reg[1])
            setattr(instance, f"{reg[0]}", new)
        groups = getmembers(instance, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))
        for group in groups:
            new = tuple(deepcopy(x, memo) for x in group[1])
            setattr(instance, f"{group[0]}", new)
        return cast(GroupInstanceType, instance)

    @classmethod
    def _update_address(cls, address: int):
        cls._address = cls._address + address
        print(f"Updating address for group {cls.__name__} to {cls._address:#x}")
        for item in cls.__dict__.values():
            if isinstance(item, tuple) and all(isinstance(x, Register) for x in item):
                print(f"Updating registers in group {cls.__name__}")
                for i, reg in enumerate(item):
                    item[i]._address = address + reg.address
                    print(f"Register {reg.name} address updated to {item[i]._address:#x}")
            elif isinstance(item, list) and all(isinstance(x, Group) for x in item):
                print(f"Updating groups in group {cls.__name__}")
                for i, group in enumerate(item):
                    print(f"Updating group {group.name} address to {address + group.address:#x}")
                    item[i] = copy(group._update_address(address)())
        for item in cls.__dict__.values():
            if isinstance(item, tuple | list) and all(isinstance(x, Group) for x in item):
                for group in item:
                    print(f"Group {group.name} address is now {group.address:#x}")
        return cls

    def _update_address_2(self: GroupInstanceType, address: int) -> GroupInstanceType:
        print(f"Updating address for group {self._name} to {address:#x}")
        self._address = address + self._address
        registers = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
        print(f"Found {len(registers)} registers in group {self._name}")
        for i, reg in enumerate(registers):
            for j, instance in enumerate(reg[1]):
                registers[i][1][j]._address = address + instance._address

        groups = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))
        print(f"Found {len(groups)} groups in group {self._name}")
        for i, group in enumerate(groups):
            for j, instance in enumerate(group[1]):
                groups[i][1][j]._update_address_2(address)

        groups = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Group) for y in x))
        for group in groups:
            for instance in group[1]:
                print(f"Group {instance.name} address is now {instance.address:#x}")
        registers = getmembers(self, lambda x: isinstance(x, list | tuple) and all(isinstance(y, Register) for y in x))
        for reg in registers:
            for instance in reg[1]:
                print(f"Register {instance.name} address is now {instance.address:#x}")

        return cast(GroupInstanceType, self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> int:
        return self._address + self._offset[self._index]

    @property
    def offset(self) -> list[int] | int:
        return self._offset


GroupType = TypeVar("GroupType", bound=type)


def _setup_registers(cls: GroupType, offset: list[int], size: int) -> GroupType:
    registers = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, Register)}
    print(f"Creating registers for group {cls.__name__}")
    for attr, value in registers.items():
        instances = tuple(deepcopy(value) for _ in range(size))
        for i, instance in enumerate(instances):
            instance._address = value.address + offset[i]

        setattr(cls, f"_{attr}", instances)

    for attr, value in registers.items():

        def getter(self, attr=attr):
            register = getattr(self, f"_{attr}")[self._index]
            self._index = 0
            return register

        def setter(self, value, attr=attr):
            register = getattr(self, f"_{attr}")[self._index]
            register.value = value
            self._index = 0

        setattr(cls, attr, property(getter, setter))

    return cls


def _setup_groups(cls: GroupType, offset: list[int], size: int) -> GroupType:
    groups = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, Group)}
    print(f"Creating groups for group {cls.__name__}")
    for attr, value in groups.items():
        instances = tuple(deepcopy(value) for _ in range(size))
        for i, instance in enumerate(instances):
            instance._address = value.address + offset[i]
        print(f"Creating {len(instances)} instances of group {attr} for group {cls.__name__}")
        for i, instance in enumerate(instances):
            richInspect(instance, all=True)

        setattr(cls, f"_{attr}", instances)

    for attr, value in groups.items():

        def getter(self, attr=attr):
            register = getattr(self, f"_{attr}")[self._index]
            self._index = 0
            return register

        def setter(self, value, attr=attr):
            register = getattr(self, f"_{attr}")[self._index]
            register.value = value
            self._index = 0

        setattr(cls, attr, property(getter, setter))

    return cls


def _update_address(cls: GroupType, address: int, offset: list[int]) -> GroupType:
    print(f"Updating address for group {cls.__name__}")
    return cls._update_address(address)


def _setup_init(cls: GroupType, name: str, address: int, offset: list[int], size: int) -> GroupType:
    init = getattr(cls, "__init__", None)
    print(f"Setting up init for group {name}")

    def __init__(self):
        print(f"Decorator init for group {name}")
        if init is not None:
            init(self)
        self._name = name
        # self._address = address + getattr(self, "_address", 0)
        self._offset = offset
        self._size = size
        self._update_address_2(address)

    cls.__init__ = __init__  # type: ignore[method-assign]
    return cls


def group(name: str, address: int, offset: list[int] | int, size: int = 1) -> Callable[[GroupType], GroupType]:
    if isinstance(offset, list):
        size = len(offset)
    else:
        offset = [0] + [offset + (i * offset) for i in range(size - 1)]

    print(f"Creating group {name} at address {address:#x} with offsets {offset} and size {size}")

    def decorator(cls: GroupType) -> GroupType:
        cls = _setup_registers(cls, offset, size)
        cls = _setup_groups(cls, offset, size)
        # cls = _update_address(cls, address, offset)
        cls = _setup_init(cls, name, address, offset, size)

        return cast(GroupType, cls)

    return decorator
