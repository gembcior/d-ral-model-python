from __future__ import annotations

from enum import IntEnum


class AccessType(IntEnum):
    ReadOnly = 0
    WriteOnly = 1
    ReadWrite = 2
