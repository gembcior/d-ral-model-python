from __future__ import annotations

from regs.alfa import AlfaGroup
from rich import inspect


def main():
    alfa = AlfaGroup()

    inspect(alfa, all=True)
    inspect(alfa[0].betaGroup[0], all=True)
    inspect(alfa[1].betaGroup[0], all=True)
    inspect(alfa[2].betaGroup[0], all=True)

    inspect(alfa[0].betaGroup[1], all=True)
    inspect(alfa[1].betaGroup[1], all=True)
    inspect(alfa[2].betaGroup[1], all=True)

    assert alfa.address == 0x40000000, f"Got {alfa.address:#x}"
    assert alfa[0].address == 0x40000000, f"Got {alfa[0].address:#x}"
    assert alfa[1].address == 0x40000100, f"Got {alfa[1].address:#x}"
    assert alfa[2].address == 0x40000200, f"Got {alfa[2].address:#x}"

    assert alfa[0].appleRegister.address == 0x40001000, f"Got {alfa[0].appleRegister.address:#x}"
    assert alfa[1].appleRegister.address == 0x40001100, f"Got {alfa[1].appleRegister.address:#x}"
    assert alfa[2].appleRegister.address == 0x40001200, f"Got {alfa[2].appleRegister.address:#x}"

    assert alfa[0].betaGroup[0].address == 0x70000000, f"Got {alfa[0].betaGroup.address:#x}"
    assert alfa[0].betaGroup[0].appleRegister.address == (0x40000000 + 0x30000000 + 0x1000), (
        f"Got {alfa[0].betaGroup[0].appleRegister.address:#x}"
    )


if __name__ == "__main__":
    main()
