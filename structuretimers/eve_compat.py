"""Compatibility layer for EVE SDE models used by this app."""

from __future__ import annotations

from collections import deque
from math import sqrt
from typing import Optional

from eve_sde.models import ItemType, SolarSystem, Stargate


def meters_to_ly(value_meters: Optional[float]) -> Optional[float]:
    """Convert meters to light years."""
    if value_meters is None:
        return None
    return value_meters / 9.4607304725808e15


def _icon_url(self: ItemType, size: int = 64) -> str:
    """Return EVE image URL for an item type."""
    return f"https://images.evetech.net/types/{self.id}/icon?size={size}"


def _distance_to(self: SolarSystem, other: Optional[SolarSystem]) -> Optional[float]:
    """Return euclidean distance in meters between two solar systems."""
    if not other:
        return None
    if None in (self.x, self.y, self.z, other.x, other.y, other.z):
        return None
    return sqrt(
        (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
    )


def _jumps_to(self: SolarSystem, other: Optional[SolarSystem]) -> Optional[int]:
    """Return shortest jump count between two systems using stargate graph."""
    if not other:
        return None
    if self.pk == other.pk:
        return 0

    visited = {self.pk}
    queue = deque([(self.pk, 0)])

    while queue:
        system_id, jumps = queue.popleft()
        neighbors = Stargate.objects.filter(solar_system_id=system_id).values_list(
            "destination_id", flat=True
        )
        for neighbor_id in neighbors:
            if neighbor_id == other.pk:
                return jumps + 1
            if neighbor_id in visited:
                continue
            visited.add(neighbor_id)
            queue.append((neighbor_id, jumps + 1))

    return None


def _is_w_space(self: SolarSystem) -> bool:
    """Compatibility alias for wormhole-space check."""
    return self.is_wh_space


SolarSystem.distance_to = _distance_to
SolarSystem.jumps_to = _jumps_to
SolarSystem.is_w_space = property(_is_w_space)

ItemType.icon_url = _icon_url
