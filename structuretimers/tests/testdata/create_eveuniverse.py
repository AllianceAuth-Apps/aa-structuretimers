from django.test import TestCase
from eveuniverse.tools.testdata import ModelSpec, create_testdata

from structuretimers.constants import EveCategoryId, EveGroupId, EveTypeId

from . import test_data_filename


class CreateEveUniverseTestData(TestCase):
    def test_create_testdata(self):
        testdata_spec = [
            ModelSpec(
                "EveCategory",
                ids=[EveCategoryId.STRUCTURE.value],
                include_children=True,
            ),
            ModelSpec(
                "EveGroup",
                ids=[
                    EveGroupId.MERCENARY_DEN.value,
                    EveGroupId.PIRATE_FORWARD_OPERATING_BASE.value,
                    EveGroupId.SKYHOOK.value,
                ],
                include_children=True,
            ),
            ModelSpec(
                "EveType",
                ids=[
                    EveTypeId.CUSTOMS_OFFICE.value,
                    EveTypeId.TCU.value,
                    EveTypeId.IHUB.value,
                ],
            ),
            ModelSpec(
                "EveSolarSystem", ids=[30004984, 30000142, 30001161, 31001303, 30045339]
            ),
        ]
        create_testdata(testdata_spec, test_data_filename())
