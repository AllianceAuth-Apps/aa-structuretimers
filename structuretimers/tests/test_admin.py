from unittest import skip

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django_webtest import WebTest

from app_utils.testdata_factories import EveCorporationInfoFactory

from structuretimers.admin import _get_multiselect_display
from structuretimers.models import NotificationRule, StagingSystem, Timer

from .testdata.factory import (
    DiscordWebhookFactory,
    EveSolarSystemFactory,
    NotificationRuleFactory,
    StagingSystemFactory,
)


class TestNotificationRule_ChangeList(WebTest):
    def test_can_open_page_normally(self):
        # given
        webhook = DiscordWebhookFactory()
        NotificationRuleFactory(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=webhook,
        )
        NotificationRuleFactory(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            require_timer_types=[Timer.Type.ARMOR],
            webhook=webhook,
        )
        rule = NotificationRuleFactory(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=webhook,
        )
        rule.require_corporations.add(EveCorporationInfoFactory())
        NotificationRuleFactory(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            is_important=NotificationRule.Clause.EXCLUDED,
            webhook=webhook,
        )
        user = User.objects.create_superuser(
            "Bruce Wayne", "bruce@example.com", "password"
        )
        self.app.set_user(user)

        # user tries to add new notification rule
        add_page = self.app.get(
            reverse("admin:structuretimers_notificationrule_changelist")
        )
        self.assertEqual(add_page.status_code, 200)


class TestNotificationRule_Validations(WebTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webhook = DiscordWebhookFactory()
        cls.user = User.objects.create_superuser(
            "Bruce Wayne", "bruce@example.com", "password"
        )
        cls.url_add = reverse("admin:structuretimers_notificationrule_add")
        cls.url_changelist = reverse(
            "admin:structuretimers_notificationrule_changelist"
        )

    def _open_page(self) -> object:
        # login
        self.app.set_user(self.user)

        # user tries to add new notification rule
        add_page = self.app.get(self.url_add)
        self.assertEqual(add_page.status_code, 200)
        form = add_page.forms["notificationrule_form"]
        form["trigger"] = NotificationRule.Trigger.SCHEDULED_TIME_REACHED
        form["scheduled_time"] = NotificationRule.MINUTES_10
        form["webhook"] = self.webhook.pk
        return form

    # FIXME
    @skip("No longer works with sqlite")
    def test_no_errors(self):
        form = self._open_page()
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url_changelist)
        self.assertEqual(NotificationRule.objects.count(), 1)

    def test_can_not_have_same_options_timer_types(self):
        form = self._open_page()
        form["require_timer_types"] = [Timer.Type.ANCHORING, Timer.Type.HULL]
        form["exclude_timer_types"] = [Timer.Type.ANCHORING, Timer.Type.ARMOR]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_objectives(self):
        form = self._open_page()
        form["require_objectives"] = [Timer.Objective.FRIENDLY, Timer.Objective.HOSTILE]
        form["exclude_objectives"] = [Timer.Objective.FRIENDLY, Timer.Objective.NEUTRAL]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_visibility(self):
        form = self._open_page()
        form["require_visibility"] = [Timer.Visibility.CORPORATION]
        form["exclude_visibility"] = [Timer.Visibility.CORPORATION]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    # FIXME: Fix test
    # def test_can_not_have_same_options_corporations(self):
    #     form = self._open_page()
    #     corp_1 = EveCorporationInfoFactory()
    #     corp_2 = EveCorporationInfoFactory()
    #     form["require_corporations"] = [corp_1.pk, corp_2.pk]
    #     form["exclude_corporations"] = [corp_1.pk]
    #     response = form.submit()

    #     # assert results
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("Please correct the error below", response.text)
    #     self.assertEqual(NotificationRule.objects.count(), 0)

    # FIXME: Fix test
    # def test_can_not_have_same_options_alliances(self):
    #     form = self._open_page()
    #     all_1 = EveAllianceInfoFactory()
    #     all_2 = EveAllianceInfoFactory()
    #     form["require_alliances"] = [all_1.pk, all_2.pk]
    #     form["exclude_alliances"] = [all_1.pk]
    #     response = form.submit()

    #     # assert results
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("Please correct the error below", response.text)
    #     self.assertEqual(NotificationRule.objects.count(), 0)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestStagingSystemAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser("Bruce Wayne")
        cls.url_add = reverse("admin:structuretimers_stagingsystem_add")

    def test_should_create_new_staging_system(self):
        # given
        self.client.force_login(self.user)
        solar_system = EveSolarSystemFactory()

        # when
        res = self.client.post(self.url_add, data={"eve_solar_system": solar_system.pk})

        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(StagingSystem.objects.count(), 1)
        obj = StagingSystem.objects.first()
        self.assertEqual(obj.eve_solar_system, solar_system)
        self.assertFalse(obj.is_main)

    def test_should_ensure_only_one_obj_is_main(self):
        # given
        self.client.force_login(self.user)
        solar_system_1 = EveSolarSystemFactory()
        StagingSystemFactory(eve_solar_system=solar_system_1, is_main=True)
        solar_system_2 = EveSolarSystemFactory()

        # when
        res = self.client.post(
            self.url_add,
            data={"eve_solar_system": solar_system_2.pk, "is_main": True},
        )

        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            StagingSystem.objects.filter(is_main=True).get().eve_solar_system,
            solar_system_2,
        )


class TestGetMultiselectDisplay(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.choices = [
            (1, "alpha"),
            (2, "bravo"),
        ]

    def test_returns_value_if_found(self):
        self.assertEqual(_get_multiselect_display(1, self.choices), "alpha")
        self.assertEqual(_get_multiselect_display(2, self.choices), "bravo")

    def test_raises_exception_if_not_found(self):
        with self.assertRaises(ValueError):
            _get_multiselect_display(3, self.choices)
