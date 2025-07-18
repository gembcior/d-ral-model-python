"""
D-RAL - Device Register Access Layer
https://github.com/gembcior/d-ral

MIT License

Copyright (c) 2025 Gembcior

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is an auto generated file. Do not modify!
"""

import dral.model as dral


@dral.group("DeltaX", 0x20030000, 0x00001000, 2)
class DeltaXGroup(dral.Group):
    @dral.register("Apple", 0x00000000, dral.AccessType.ReadWrite)
    class AppleRegister(dral.Register):
        dpField = dral.Field("Dp", 0, 1)
        hdmiField = dral.Field("Hdmi", 2, 4)
        usbField = dral.Field("Usb", 15, 16)

    @dral.register("Banana", 0x00000020, dral.AccessType.ReadWrite)
    class BananaRegister(dral.Register):
        hdcpField = dral.Field("Hdcp", 0, 10)
        aesField = dral.Field("Aes", 20, 5)

    appleRegister = AppleRegister()
    bananaRegister = BananaRegister()
