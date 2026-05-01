import datetime as dt
from unittest.mock import Mock, patch

from django.db import models
from django.utils.timezone import now
from eveuniverse.models import EveRegion, EveSolarSystem

from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo
from app_utils.testing import NoSocketsTestCase

from structuretimers.models import NotificationRule, ScheduledNotification, Timer
from structuretimers.tests.testdata.factory import (
    create_discord_webhook,
    create_notification_rule,
    create_scheduled_notification,
    create_timer,
)
from structuretimers.tests.testdata.fixtures import LoadTestDataMixin

MODULE_PATH = "structuretimers.models"


@patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleIsMatchingTimer(LoadTestDataMixin, NoSocketsTestCase):
    def test_should_match_when_no_rules_set(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule()
        # when/then
        self.assertTrue(rule.is_matching_timer(timer))

    def test_require_timer_types(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(require_timer_types=[Timer.Type.ARMOR])
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.timer_type = Timer.Type.ARMOR
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_timer_types(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(exclude_timer_types=[Timer.Type.ARMOR])
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.timer_type = Timer.Type.ARMOR
        self.assertFalse(rule.is_matching_timer(timer))

    def test_should_never_match_without_date(self):
        # given
        timer = create_timer(date=None)
        rule = create_notification_rule()
        # when/then
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_objectives(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(require_objectives=[Timer.Objective.HOSTILE])
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.objective = Timer.Objective.HOSTILE
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_objectives(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(exclude_objectives=[Timer.Objective.HOSTILE])
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))

        # do not process if it does not match
        timer.objective = Timer.Objective.HOSTILE
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_corporations(self):
        # given
        timer = create_timer()
        rule = create_notification_rule()
        rule.require_corporations.add(
            EveCorporationInfo.objects.get(corporation_id=2001)
        )
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))

        # process if it does match
        timer.eve_corporation = EveCorporationInfo.objects.get(corporation_id=2001)
        timer.save()
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_corporations(self):
        # given
        timer = create_timer()
        rule = create_notification_rule()
        # process if it does match
        rule.exclude_corporations.add(
            EveCorporationInfo.objects.get(corporation_id=2001)
        )
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.eve_corporation = EveCorporationInfo.objects.get(corporation_id=2001)
        timer.save()
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_alliances(self):
        # given
        timer = create_timer()
        rule = create_notification_rule()
        rule.require_alliances.add(EveAllianceInfo.objects.get(alliance_id=3001))
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.eve_alliance = EveAllianceInfo.objects.get(alliance_id=3001)
        timer.save()
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_alliances(self):
        # given
        timer = create_timer()
        rule = create_notification_rule()
        rule.exclude_alliances.add(EveAllianceInfo.objects.get(alliance_id=3001))
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.eve_alliance = EveAllianceInfo.objects.get(alliance_id=3001)
        timer.save()
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_visibility(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(
            require_visibility=[Timer.Visibility.CORPORATION]
        )
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.visibility = Timer.Visibility.CORPORATION
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_visibility(self):
        # given
        timer = create_timer()
        rule = create_notification_rule(
            exclude_visibility=[Timer.Visibility.CORPORATION]
        )
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.visibility = Timer.Visibility.CORPORATION
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_important(self):
        timer = create_timer()
        rule = create_notification_rule(is_important=NotificationRule.Clause.REQUIRED)
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.is_important = True
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_important(self):
        timer = create_timer()
        rule = create_notification_rule(is_important=NotificationRule.Clause.EXCLUDED)
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.is_important = True
        self.assertFalse(rule.is_matching_timer(timer))

    def test_require_opsec(self):
        timer = create_timer()
        rule = create_notification_rule(is_opsec=NotificationRule.Clause.REQUIRED)
        # do not process if it does not match
        self.assertFalse(rule.is_matching_timer(timer))
        # process if it does match
        timer.is_opsec = True
        self.assertTrue(rule.is_matching_timer(timer))

    def test_exclude_opsec(self):
        timer = create_timer()
        rule = create_notification_rule(is_opsec=NotificationRule.Clause.EXCLUDED)
        # process if it does match
        self.assertTrue(rule.is_matching_timer(timer))
        # do not process if it does not match
        timer.is_opsec = True
        self.assertFalse(rule.is_matching_timer(timer))

    def test_should_match_require_regions(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule()
        rule.require_regions.add(EveRegion.objects.get(name="Essence"))
        # when/then
        self.assertTrue(rule.is_matching_timer(timer))

    def test_should_not_match_require_regions(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule()
        rule.require_regions.add(EveRegion.objects.get(name="Black Rise"))
        # when/then
        self.assertFalse(rule.is_matching_timer(timer))

    def test_should_match_exclude_regions(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule()
        rule.exclude_regions.add(EveRegion.objects.get(name="Essence"))
        # when/then
        self.assertFalse(rule.is_matching_timer(timer))

    def test_should_not_match_exclude_regions(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule()
        rule.exclude_regions.add(EveRegion.objects.get(name="Black Rise"))
        # when/then
        self.assertTrue(rule.is_matching_timer(timer))

    def test_should_match_require_space_types(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule(require_space_types=[Timer.SpaceType.LOW_SEC])
        # when/then
        self.assertTrue(rule.is_matching_timer(timer))

    def test_should_not_match_require_space_types(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule(require_space_types=[Timer.SpaceType.NULL_SEC])
        # when/then
        self.assertFalse(rule.is_matching_timer(timer))

    def test_should_match_exclude_space_types(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule(exclude_space_types=[Timer.SpaceType.NULL_SEC])
        # when/then
        self.assertTrue(rule.is_matching_timer(timer))

    def test_should_not_match_exclude_space_types(self):
        # given
        timer = create_timer(eve_solar_system=EveSolarSystem.objects.get(name="Abune"))
        rule = create_notification_rule(exclude_space_types=[Timer.SpaceType.LOW_SEC])
        # when/then
        self.assertFalse(rule.is_matching_timer(timer))


@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleQuerySet(LoadTestDataMixin, NoSocketsTestCase):
    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.webhook = create_discord_webhook()
        self.rule_1 = create_notification_rule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=10,
            require_timer_types=[Timer.Type.ARMOR],
            webhook=self.webhook,
        )
        self.rule_2 = create_notification_rule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=15,
            require_objectives=[Timer.Objective.FRIENDLY],
            webhook=self.webhook,
        )
        self.rule_qs = NotificationRule.objects.all()

    def test_conforms_with_timer_1(self):
        """
        given two rules in qs
        when one rule conforms with timer
        then qs contains only conforming rule
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.ARMOR,
            objective=Timer.Objective.HOSTILE,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), {self.rule_1.pk})

    def test_conforms_with_timer_2(self):
        """
        given two rules in qs
        when no rule conforms with timer
        then qs is empty
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.HULL,
            objective=Timer.Objective.HOSTILE,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), set())

    def test_conforms_with_timer_3(self):
        """
        given two rules in qs
        when one rule conforms with timer
        then qs contains only conforming rule
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.ARMOR,
            objective=Timer.Objective.FRIENDLY,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(
            set(new_qs.values_list("pk", flat=True)), {self.rule_1.pk, self.rule_2.pk}
        )


@patch(MODULE_PATH + ".NotificationRule._import_schedule_notifications_for_rule")
class TestNotificationRuleSave(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = create_discord_webhook(name="dummy", url="dummy-url")

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", True)
    def test_scheduled_normal(self, mock_schedule_notifications):
        """
        given notifications are enabled
        when trigger is scheduled and enabled
        then schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.save()
        self.assertTrue(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def test_scheduled_disabled_1(self, mock_schedule_notifications):
        """
        given notifications are disabled
        when trigger is scheduled and enabled
        then do not schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.save()
        self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", True)
    def test_scheduled_disabled_2(self, mock_schedule_notifications):
        """
        given notifications are enabled
        when trigger is scheduled and disabled
        then do not schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
            is_enabled=False,
        )
        rule.save()
        self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def test_created_trigger(self, mock_schedule_notifications):
        """
        when trigger is created
        then delete all scheduled notifications based on same rule
        """
        rule = create_notification_rule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        timer = create_timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        obj = create_scheduled_notification(
            timer=timer,
            notification_rule=rule,
            timer_date=timer.date,
            notification_date=timer.date - dt.timedelta(minutes=10),
        )
        rule.trigger = NotificationRule.Trigger.NEW_TIMER_CREATED
        rule.scheduled_time = None
        rule.save()

        self.assertFalse(ScheduledNotification.objects.filter(pk=obj.pk).exists())
