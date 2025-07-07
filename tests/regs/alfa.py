from dataclasses import dataclass

import dral


@dral.register("Apple", 0x1000, dral.AccessType.ReadWrite)
class AppleRegister(dral.Register):
    dpField = dral.Field("DP", 0, 1)
    hdmiField = dral.Field("HDMI", 2, 4)
    usbField = dral.Field("USB", 15, 16)


@dral.register("Banana", 0x2000, dral.AccessType.ReadOnly)
class BananaRegister(dral.Register):
    dpField = dral.Field("DP", 0, 1)
    hdmiField = dral.Field("HDMI", 2, 4)
    usbField = dral.Field("USB", 15, 16)


@dral.group("Beta", 0x30000000, 0x200, 2)
class BetaGroup(dral.Group):
    bananaRegister = BananaRegister()
    appleRegister = AppleRegister()


@dral.group("Alfa", 0x40000000, 0x100, 3)
class AlfaGroup(dral.Group):
    appleRegister = AppleRegister()
    betaGroup = BetaGroup()
