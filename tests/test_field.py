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

from regs.alfa import AlfaGroup
from regs.delta_x import DeltaXGroup
from regs.echo_x import EchoXGroup


class TestField:
    def test_field_value_set_get_1(self):
        alfa = AlfaGroup()

        alfa.appleRegister.dpField.value = 0x1
        alfa.appleRegister.hdmiField.value = 0x2
        alfa.bananaRegister.aesField.value = 0xF

        assert alfa.appleRegister.dpField.value == 0x1
        assert alfa.appleRegister.hdmiField.value == 0x2
        assert alfa.bananaRegister.aesField.value == 0xF

    def test_field_value_set_get_2(self):
        echo = EchoXGroup()

        echo[0].bearXGroup[0].bearRegister.tcpField.value = 0x3
        echo[1].bearXGroup[0].bearRegister.udpField.value = 0x4
        echo[0].bearXGroup[1].bearRegister.tcpField.value = 0x9F
        echo[1].bearXGroup[1].bearRegister.udpField.value = 0xA0

        assert echo[0].bearXGroup[0].bearRegister.tcpField.value == 0x3
        assert echo[1].bearXGroup[0].bearRegister.udpField.value == 0x4
        assert echo[0].bearXGroup[1].bearRegister.tcpField.value == 0x9F
        assert echo[1].bearXGroup[1].bearRegister.udpField.value == 0xA0

    def test_field_value_set_get_3(self):
        delta = DeltaXGroup()

        delta[0].appleRegister.dpField.value = 0x1
        delta[0].appleRegister.usbField.value = 0x6

        assert delta[0].appleRegister.value == 0x30001

        delta[0].bananaRegister.value = 0x20002
        assert delta[0].bananaRegister.aesField.value == 0x0
        assert delta[0].bananaRegister.hdcpField.value == 0x2
