from __future__ import annotations


class Field:
    def __init__(self, name: str, position: int, width: int) -> None:
        self._name = name
        self._position = position
        self._width = width
        self._mask = (1 << width) - 1
        self._value = 0

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> int:
        return self._position

    @property
    def mask(self) -> int:
        return self._mask

    @property
    def width(self) -> int:
        return self._width

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value & self._mask
