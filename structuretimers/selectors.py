"""Selectors."""

from django.db.models import QuerySet
from eveuniverse.models import EveType

from structuretimers.constants import EveCategoryId, EveGroupId, EveTypeId


def supported_eve_types() -> QuerySet[EveType]:
    """Return query for all supported types."""
    structures = EveType.objects.filter(
        eve_group__eve_category_id=EveCategoryId.STRUCTURE,
        published=True,
    )
    groups_published = EveType.objects.filter(
        eve_group_id__in=[
            EveGroupId.CONTROL_TOWER,
            EveGroupId.MOBILE_DEPOT,
            EveGroupId.MERCENARY_DEN,
        ],
        published=True,
    )
    groups_unpublished = EveType.objects.filter(
        eve_group_id__in=[EveGroupId.PIRATE_FORWARD_OPERATING_BASE]
    )
    types = EveType.objects.filter(
        id__in=[
            EveTypeId.CUSTOMS_OFFICE,
            EveTypeId.ORBITAL_SKYHOOK,
            EveTypeId.IHUB,
            EveTypeId.TCU,
        ]
    )
    qs = (structures | groups_published | groups_unpublished | types).distinct()
    return qs
