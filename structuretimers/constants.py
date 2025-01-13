"""Global constants."""

# pylint: disable=missing-class-docstring

from enum import IntEnum


class EveCategoryId(IntEnum):
    STRUCTURE = 65


class EveGroupId(IntEnum):
    CONTROL_TOWER = 365
    MERCENARY_DEN = 4810
    MOBILE_DEPOT = 1246
    PIRATE_FORWARD_OPERATING_BASE = 4644
    REFINERY = 1406
    SKYHOOK = 4736


class EveTypeId(IntEnum):
    ASTRAHUS = 35832
    CUSTOMS_OFFICE = 2233
    IHUB = 32458
    ORBITAL_SKYHOOK = 81080
    TCU = 32226
