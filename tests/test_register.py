from __future__ import annotations

from copy import copy, deepcopy
from inspect import getmembers

import pytest
from regs.alfa import AlfaGroup
from regs.bravo import BravoGroup
from regs.charlie import CharlieGroup
from regs.delta_x import DeltaXGroup
from regs.echo_x import EchoXGroup

import dral.model as dral


class TestRegister:
    def test_register_address_calculation(self):
        alfa = AlfaGroup()
        bravo = BravoGroup()
        charlie = CharlieGroup()
        delta = DeltaXGroup()
        echo = EchoXGroup()

        test_cases = [
            (alfa.appleRegister.address, 0x20000000),
            (alfa.bananaRegister.address, 0x20000020),
            (bravo.albatrossRegister.address, 0x20010000),
            (bravo.bearXGroup[0].bearRegister.address, 0x20010020),
            (bravo.bearXGroup[1].bearRegister.address, 0x20010040),
            (charlie.albatrossRegister.address, 0x20020000),
            (charlie.fruitsGroup[0].appleRegister.address, 0x20020020),
            (charlie.fruitsGroup[0].bananaRegister.address, 0x20020040),
            (delta[0].appleRegister.address, 0x20030000),
            (delta[1].appleRegister.address, 0x20031000),
            (delta[0].bananaRegister.address, 0x20030020),
            (delta[1].bananaRegister.address, 0x20031020),
            (echo[0].bearXGroup[0].bearRegister.address, 0x20040020),
            (echo[0].bearXGroup[1].bearRegister.address, 0x20040040),
            (echo[0].bearXGroup[2].bearRegister.address, 0x20040060),
            (echo[1].bearXGroup[0].bearRegister.address, 0x20041020),
            (echo[1].bearXGroup[1].bearRegister.address, 0x20041040),
            (echo[1].bearXGroup[2].bearRegister.address, 0x20041060),
        ]

        for address, expected in test_cases:
            assert address == expected, f"Expected {expected:#010x}, got {address:#010x}"

    def test_register_attributes_overwrite(self):
        alfa = AlfaGroup()
        bravo = BravoGroup()
        charlie = CharlieGroup()
        delta = DeltaXGroup()
        echo = EchoXGroup()

        test_cases = [
            (alfa.appleRegister, "name", "NewAppleName"),
            (bravo.albatrossRegister, "address", 0x1000000),
            (charlie.fruitsGroup[0].appleRegister, "access", dral.AccessType.ReadOnly),
            (delta[0].appleRegister, "address", 0x1000000),
            (echo[0].bearXGroup[0].bearRegister, "name", "NewBearName"),
            (echo[1].bearXGroup[0].bearRegister, "access", dral.AccessType.WriteOnly),
        ]

        for register, attr, value in test_cases:
            with pytest.raises(AttributeError):
                setattr(register, attr, value)

    def test_register_deepcopy(self):
        alfa = AlfaGroup()
        bravo = BravoGroup()
        charlie = CharlieGroup()
        delta = DeltaXGroup()
        echo = EchoXGroup()

        test_cases = [
            (alfa.appleRegister, deepcopy(alfa.appleRegister)),
            (bravo.albatrossRegister, deepcopy(bravo.albatrossRegister)),
            (charlie.fruitsGroup[0].appleRegister, deepcopy(charlie.fruitsGroup[0].appleRegister)),
            (delta[0].appleRegister, deepcopy(delta[0].appleRegister)),
            (echo[0].bearXGroup[0].bearRegister, deepcopy(echo[0].bearXGroup[0].bearRegister)),
            (echo[1].bearXGroup[0].bearRegister, deepcopy(echo[1].bearXGroup[0].bearRegister)),
        ]
        for original, copied in test_cases:
            assert original != copied, f"Original and copied registers should not be the same object: {original} != {copied}"
            assert original.name == copied.name, f"Name mismatch: {original.name} != {copied.name}"
            assert original.address == copied.address, f"Address mismatch: {original.address:#010x} != {copied.address:#010x}"
            assert original.access == copied.access, f"Access type mismatch: {original.access} != {copied.access}"

    def test_register_children_overwrite(self):
        alfa = AlfaGroup()
        fields = getmembers(alfa.appleRegister, lambda x: isinstance(x, dral.Field))
        fields = [x for x in fields if not x[0].startswith("_")]
        for attr, value in fields:
            with pytest.raises(AttributeError):
                setattr(alfa.appleRegister, attr, copy(value))

    def test_register_value_set_get(self):
        alfa = AlfaGroup()
        bravo = BravoGroup()
        charlie = CharlieGroup()
        delta = DeltaXGroup()
        echo = EchoXGroup()

        test_cases = [
            (alfa.appleRegister, 0x12345678),
            (bravo.albatrossRegister, 0x87654321),
            (charlie.fruitsGroup[0].appleRegister, 0xAABBCCDD),
            (delta[0].appleRegister, 0x11223344),
            (echo[0].bearXGroup[0].bearRegister, 0x55667788),
            (echo[1].bearXGroup[0].bearRegister, 0x99AABBCC),
        ]

        for register, new_value in test_cases:
            register.value = new_value
            actual_value = register.value
            assert actual_value == new_value, f"Expected value {new_value:#010x}, got {actual_value:#010x}"
