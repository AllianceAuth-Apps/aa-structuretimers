import json

from django.test import TestCase
from eve_sde.models import (
    Constellation,
    ItemCategory,
    ItemGroup,
    ItemType,
    Region,
    SolarSystem,
)

from structuretimers.constants import EveCategoryId, EveGroupId, EveTypeId

from . import test_data_filename


class CreateEveSdeTestData(TestCase):
    def test_create_testdata(self):
        solar_system_ids = [30004984, 30000142, 30001161, 31001303, 30045339]
        type_ids = [
            EveTypeId.CUSTOMS_OFFICE.value,
            EveTypeId.TCU.value,
            EveTypeId.IHUB.value,
        ]

        categories = list(
            ItemCategory.objects.filter(id=EveCategoryId.STRUCTURE.value).values(
                "id", "name", "published"
            )
        )
        groups = list(
            ItemGroup.objects.filter(
                id__in=[
                    EveGroupId.MERCENARY_DEN.value,
                    EveGroupId.PIRATE_FORWARD_OPERATING_BASE.value,
                    EveGroupId.SKYHOOK.value,
                ]
            ).values("id", "name", "published", "category_id")
        )
        regions = list(
            Region.objects.filter(
                id__in=Constellation.objects.filter(
                    id__in=SolarSystem.objects.filter(
                        id__in=solar_system_ids
                    ).values_list("constellation_id", flat=True)
                ).values_list("region_id", flat=True)
            ).values("id", "name", "description")
        )
        constellations = list(
            Constellation.objects.filter(
                id__in=SolarSystem.objects.filter(id__in=solar_system_ids).values_list(
                    "constellation_id", flat=True
                )
            ).values("id", "name", "region_id", "x", "y", "z")
        )
        solar_systems = list(
            SolarSystem.objects.filter(id__in=solar_system_ids).values(
                "id",
                "name",
                "constellation_id",
                "security_status",
                "x",
                "y",
                "z",
            )
        )
        types = list(
            ItemType.objects.filter(id__in=type_ids).values(
                "id",
                "name",
                "description",
                "group_id",
                "capacity",
                "mass",
                "radius",
                "volume",
                "packaged_volume",
                "portion_size",
                "published",
                "icon_id",
            )
        )

        payload = {
            "ItemCategory": [
                {"id": x["id"], "name": x["name"], "published": x["published"]}
                for x in categories
            ],
            "ItemGroup": [
                {
                    "id": x["id"],
                    "name": x["name"],
                    "published": x["published"],
                    "category_id": x["category_id"],
                }
                for x in groups
            ],
            "Region": [
                {
                    "id": x["id"],
                    "name": x["name"],
                    "description": x["description"] or "",
                }
                for x in regions
            ],
            "Constellation": [
                {
                    "id": x["id"],
                    "name": x["name"],
                    "region_id": x["region_id"],
                    "x": x["x"],
                    "y": x["y"],
                    "z": x["z"],
                }
                for x in constellations
            ],
            "SolarSystem": [
                {
                    "id": x["id"],
                    "name": x["name"],
                    "constellation_id": x["constellation_id"],
                    "security_status": x["security_status"],
                    "x": x["x"],
                    "y": x["y"],
                    "z": x["z"],
                }
                for x in solar_systems
            ],
            "ItemType": [
                {
                    "id": x["id"],
                    "name": x["name"],
                    "description": x["description"] or "",
                    "group_id": x["group_id"],
                    "capacity": x["capacity"],
                    "mass": x["mass"],
                    "radius": x["radius"],
                    "volume": x["volume"],
                    "packaged_volume": x["packaged_volume"],
                    "portion_size": x["portion_size"],
                    "published": x["published"],
                    "icon_id": x["icon_id"],
                }
                for x in types
            ],
        }

        with open(test_data_filename(), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)


__all__ = ["CreateEveSdeTestData"]
