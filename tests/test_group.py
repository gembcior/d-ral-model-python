from __future__ import annotations

from itertools import product

import pytest
from regs.alfa import AlfaGroup
from regs.bravo import BravoGroup
from regs.charlie import CharlieGroup
from regs.delta_x import DeltaXGroup
from regs.echo_x import EchoXGroup


class TestGroup:
    @pytest.mark.parametrize(
        "group, expected_address",
        [
            (AlfaGroup, [0x20000000]),
            (BravoGroup, [0x20010000]),
            (CharlieGroup, [0x20020000]),
            (DeltaXGroup, [0x20030000, 0x20031000]),
            (EchoXGroup, [0x20040000, 0x20041000]),
        ],
    )
    def test_group_address_calculation(self, group, expected_address):
        instance = group()
        for i, address in enumerate(expected_address):
            assert instance[i].address == address, (
                f"Address mismatch for {instance[i].name}: expected {address:#010x}, got {instance[i].address:#010x}"
            )

    def test_nested_group_address_calculation(self):
        echo_groups = (EchoXGroup(), EchoXGroup(), EchoXGroup())
        for i, group in enumerate(echo_groups):
            for echo_idx, bear_idx in product(range(len(group)), range(len(group.bearXGroup))):
                expected_address = 0x20040020 + (bear_idx * 0x20) + (echo_idx * 0x1000)
                actual_address = group[echo_idx].bearXGroup[bear_idx].address
                assert actual_address == expected_address, (
                    f"EchoGroup[{i}]: Expected address {expected_address:#010x}, got {actual_address:#010x}"
                )

    @pytest.mark.parametrize("group", [AlfaGroup, BravoGroup, CharlieGroup, DeltaXGroup, EchoXGroup])
    def test_group_attributes_access(self, group):
        instance = group()
        with pytest.raises(AttributeError):
            instance.name = "NewName"  # type: ignore
        with pytest.raises(AttributeError):
            instance.address = 0x1000000  # type: ignore
        with pytest.raises(AttributeError):
            instance.offset = [0x1000, 0x2000]  # type: ignore

    def test_nested_group_attributes_access(self):
        echo_group = EchoXGroup()
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].name = "NewBearName"  # type: ignore
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].address = 0x1000000  # type: ignore
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].offset = [0x1000, 0x2000]  # type: ignore
