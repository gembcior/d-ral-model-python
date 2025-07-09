from __future__ import annotations

from regs.alfa import AlfaGroup
from rich import inspect


def main():
    alfa = AlfaGroup()

    assert alfa.address == 0x40000000, f"Got {alfa.address:#x}"
    assert alfa[0].address == 0x40000000, f"Got {alfa[0].address:#x}"
    assert alfa[1].address == 0x40000100, f"Got {alfa[1].address:#x}"
    assert alfa[2].address == 0x40000200, f"Got {alfa[2].address:#x}"

    assert alfa[0].appleRegister.address == 0x40001000, f"Got {alfa[0].appleRegister.address:#x}"
    assert alfa[1].appleRegister.address == 0x40001100, f"Got {alfa[1].appleRegister.address:#x}"
    assert alfa[2].appleRegister.address == 0x40001200, f"Got {alfa[2].appleRegister.address:#x}"

    assert alfa[0].betaGroup[0].address == 0x70000000, f"Got {alfa[0].betaGroup[0].address:#x}"
    assert alfa[1].betaGroup[0].address == 0x70000100, f"Got {alfa[1].betaGroup[0].address:#x}"
    assert alfa[2].betaGroup[0].address == 0x70000200, f"Got {alfa[2].betaGroup[0].address:#x}"
    assert alfa[0].betaGroup[1].address == 0x70000200, f"Got {alfa[0].betaGroup[1].address:#x}"
    assert alfa[1].betaGroup[1].address == 0x70000300, f"Got {alfa[1].betaGroup[1].address:#x}"
    assert alfa[2].betaGroup[1].address == 0x70000400, f"Got {alfa[2].betaGroup[1].address:#x}"

    assert alfa[0].betaGroup[0].appleRegister.address == (0x40000000 + 0x30000000 + 0x1000), (
        f"Got {alfa[0].betaGroup[0].appleRegister.address:#x}"
    )

    assert alfa[1].betaGroup[0].appleRegister.address == (0x40000100 + 0x30000000 + 0x1000), (
        f"Got {alfa[1].betaGroup[0].appleRegister.address:#x}"
    )

    assert alfa[2].betaGroup[1].appleRegister.address == (0x40000200 + 0x30000200 + 0x1000), (
        f"Got {alfa[2].betaGroup[1].appleRegister.address:#x}"
    )

    alfa[0].appleRegister.value = 0x12345678
    alfa[1].appleRegister.value = 0x23456789

    assert alfa[0].appleRegister.value == 0x12345678, f"Got {alfa[0].appleRegister.value:#x}"
    assert alfa[1].appleRegister.value == 0x23456789, f"Got {alfa[1].appleRegister.value:#x}"
    assert alfa[0].appleRegister.usbField.value == 0x2468, f"Got {alfa[0].appleRegister.usbField.value:#x}"
    assert alfa[1].appleRegister.usbField.value == 0x468a, f"Got {alfa[1].appleRegister.usbField.value:#x}"

    alfa[2].appleRegister.value = 0xFFFFFFFF
    alfa[2].appleRegister.usbField.value = 0x1234
    assert alfa[2].appleRegister.value == 0x891a7fff, f"Got {alfa[2].appleRegister.value:#x}"


if __name__ == "__main__":
    main()
