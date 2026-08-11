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

from copy import copy, deepcopy
from inspect import getmembers
from itertools import product

import pytest
from regs.alfa import AlfaGroup
from regs.bravo import BravoGroup
from regs.charlie import CharlieGroup
from regs.delta_x import DeltaXGroup
from regs.echo_x import EchoXGroup

import dral.model as dral


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
            assert instance[i].address == address, f"Address mismatch for {instance[i].name}: expected {address:#010x}, got {instance[i].address:#010x}"

    def test_indexed_group_reference_stays_sticky_across_repeated_access(self):
        # Regression: group[i] used to mutate a shared _index and reset it to 0
        # after the first attribute read, so a stored `sel = group[i]` silently
        # drifted back to index 0 on the second access.
        group = EchoXGroup()
        sel = group[1]
        first = sel.bearXGroup[0].address
        second = sel.bearXGroup[0].address
        assert first == second == 0x20041020
        assert sel.bearXGroup[1].address == 0x20041040
        # The un-indexed original must be unaffected and still default to index 0.
        assert group[0].bearXGroup[0].address == 0x20040020

    def test_indexed_group_register_value_is_isolated_per_slot(self):
        # Each array slot must own a real, independent Register instance -
        # writing through one indexed path must not leak into a sibling slot.
        sel = EchoXGroup()[1]
        sel.bearXGroup[0].bearRegister.value = 0xAA
        sel.bearXGroup[1].bearRegister.value = 0xBB
        assert sel.bearXGroup[0].bearRegister.value == 0xAA
        assert sel.bearXGroup[1].bearRegister.value == 0xBB
        assert EchoXGroup()[0].bearXGroup[0].bearRegister.value == 0x00

    def test_nested_group_address_calculation(self):
        echo_groups = (EchoXGroup(), EchoXGroup(), EchoXGroup())
        for i, group in enumerate(echo_groups):
            for echo_idx, bear_idx in product(range(len(group)), range(len(group.bearXGroup))):
                expected_address = 0x20040020 + (bear_idx * 0x20) + (echo_idx * 0x1000)
                actual_address = group[echo_idx].bearXGroup[bear_idx].address
                assert actual_address == expected_address, f"EchoGroup[{i}]: Expected address {expected_address:#010x}, got {actual_address:#010x}"

    @pytest.mark.parametrize("group", [AlfaGroup, BravoGroup, CharlieGroup, DeltaXGroup, EchoXGroup])
    def test_group_attributes_overwrite(self, group):
        instance = group()
        with pytest.raises(AttributeError):
            instance.name = "NewName"  # type: ignore
        with pytest.raises(AttributeError):
            instance.address = 0x1000000  # type: ignore
        with pytest.raises(AttributeError):
            instance.offset = [0x1000, 0x2000]  # type: ignore

    def test_nested_group_attributes_overwrite(self):
        echo_group = EchoXGroup()
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].name = "NewBearName"  # type: ignore
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].address = 0x1000000  # type: ignore
        with pytest.raises(AttributeError):
            echo_group.bearXGroup[0].offset = [0x1000, 0x2000]  # type: ignore

    @pytest.mark.parametrize("group", [AlfaGroup, BravoGroup, CharlieGroup, DeltaXGroup, EchoXGroup])
    def test_group_children_overwrite(self, group):
        instance = group()
        registers = getmembers(instance, lambda x: isinstance(x, dral.Register))
        for attr, value in registers:
            with pytest.raises(AttributeError):
                setattr(instance, attr, copy(value))
        groups = getmembers(instance, lambda x: isinstance(x, dral.Group))
        for attr, value in groups:
            with pytest.raises(AttributeError):
                setattr(instance, attr, copy(value))

    @pytest.mark.parametrize("group", [AlfaGroup, BravoGroup, CharlieGroup, DeltaXGroup, EchoXGroup])
    def test_group_deepcopy(self, group):
        instance = group()
        copied_instance = deepcopy(instance)
        assert instance.name == copied_instance.name, f"Name mismatch: {instance.name} != {copied_instance.name}"
        assert instance.address == copied_instance.address, f"Address mismatch: {instance.address:#010x} != {copied_instance.address:#010x}"
        assert instance.offset == copied_instance.offset, f"Offset mismatch: {instance.offset} != {copied_instance.offset}"

        for attr, value in getmembers(instance, lambda x: isinstance(x, dral.Register)):
            copied_value = getattr(copied_instance, attr)
            assert value != copied_value, f"Original and copied registers should not be the same object: {value} != {copied_value}"
            assert value.name == copied_value.name, f"Name mismatch: {value.name} != {copied_value.name}"
            assert value.address == copied_value.address, f"Address mismatch: {value.address:#010x} != {copied_value.address:#010x}"
            assert value.access == copied_value.access, f"Access type mismatch: {value.access} != {copied_value.access}"

        for attr, value in getmembers(instance, lambda x: isinstance(x, dral.Group)):
            copied_value = getattr(copied_instance, attr)
            assert value != copied_value, f"Original and copied groups should not be the same object: {value} != {copied_value}"
            assert value.name == copied_value.name, f"Name mismatch: {value.name} != {copied_value.name}"
            assert value.address == copied_value.address, f"Address mismatch: {value.address:#010x} != {copied_value.address:#010x}"
