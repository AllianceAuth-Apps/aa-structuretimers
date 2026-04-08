import json

from eve_sde.models import (
    Constellation,
    ItemCategory,
    ItemGroup,
    ItemType,
    Region,
    SolarSystem,
)

from . import test_data_filename


def _load_eve_sde_from_file():
    with open(test_data_filename(), "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


eve_sde_testdata = _load_eve_sde_from_file()


def load_eve_sde():
    for row in eve_sde_testdata.get("ItemCategory", []):
        ItemCategory.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "published": row.get("published", False),
            },
        )

    for row in eve_sde_testdata.get("ItemGroup", []):
        ItemGroup.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "category_id": row.get("category_id"),
                "published": row.get("published", False),
            },
        )

    for row in eve_sde_testdata.get("Region", []):
        Region.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "description": row.get("description") or None,
            },
        )

    for row in eve_sde_testdata.get("Constellation", []):
        Constellation.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "region_id": row.get("region_id"),
                "x": row.get("x"),
                "y": row.get("y"),
                "z": row.get("z"),
            },
        )

    for row in eve_sde_testdata.get("SolarSystem", []):
        SolarSystem.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "constellation_id": row.get("constellation_id"),
                "security_status": row.get("security_status"),
                "x": row.get("x"),
                "y": row.get("y"),
                "z": row.get("z"),
            },
        )

    for row in eve_sde_testdata.get("ItemType", []):
        ItemType.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "description": row.get("description") or None,
                "group_id": row.get("group_id"),
                "published": row.get("published", False),
                "capacity": row.get("capacity"),
                "mass": row.get("mass"),
                "radius": row.get("radius"),
                "volume": row.get("volume"),
                "packaged_volume": row.get("packaged_volume"),
                "portion_size": row.get("portion_size"),
            },
        )
