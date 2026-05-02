from datetime import timedelta
from http import HTTPStatus
from unittest.mock import Mock, patch

from webtest.app import AppError

from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now
from django_webtest import WebTest

from app_utils.testing import NoSocketsTestCase

from structuretimers.models import ScheduledNotification, Timer
from structuretimers.tasks import send_test_message_to_webhook
from structuretimers.tests.testdata.factory import (
    CitadelTypeFactory,
    DiscordWebhookFactory,
    EveSolarSystemLowSecFactory,
    NotificationRuleFactory,
    TimerFactory,
    UserNoAccessFactory,
    UserWithAccessFactory,
    UserWithCreateFactory,
    UserWithManageFactory,
)

MODELS_PATH = "structuretimers.models"
FORMS_PATH = "structuretimers.forms"
TASKS_PATH = "structuretimers.tasks"

# TODO: Rewrite tests to work also with AA4


@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestUI(WebTest):
    # @classmethod
    # def setUp(self) -> None:
    #     timer = TimerFactory(
    #         structure_name="Timer 1",
    #         date=now() + timedelta(hours=4),
    #         eve_character=self.character_2,
    #         eve_corporation=self.corporation_1,
    #         user=self.user_create,
    #         eve_solar_system=self.system_abune,
    #         structure_type=self.type_astrahus,
    #     )
    #     timer = TimerFactory(
    #         structure_name="Timer 2",
    #         date=now() - timedelta(hours=8),
    #         eve_character=self.character_2,
    #         eve_corporation=self.corporation_1,
    #         user=self.user_create,
    #         eve_solar_system=self.system_abune,
    #         structure_type=self.type_raitaru,
    #     )
    #     self.timer_3 = TimerFactory(
    #         structure_name="Timer 3",
    #         date=now() - timedelta(hours=8),
    #         eve_character=self.character_2,
    #         eve_corporation=self.corporation_1,
    #         user=self.user_create,
    #         eve_solar_system=self.system_enaluri,
    #         structure_type=self.type_astrahus,
    #     )

    def test_user_with_permission_can_add_timer(self):
        # setup
        solar_system = EveSolarSystemLowSecFactory()
        structure_type = CitadelTypeFactory()

        # login
        self.app.set_user(UserWithCreateFactory())

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, HTTPStatus.OK)

        # user clicks on "Add Timer"
        add_timer = timerboard.click(href=reverse("structuretimers:add"))
        self.assertEqual(add_timer.status_code, HTTPStatus.OK)

        # user enters data and clicks create
        form = add_timer.forms["add-timer-form"]
        form["structure_name"] = "Timer 4"
        form["eve_solar_system_2"].force_value([str(solar_system.id)])
        form["structure_type_2"].force_value([str(structure_type.id)])
        form["timer_type"] = Timer.Type.ANCHORING
        form["days_left"] = 1
        form["hours_left"] = 2
        form["minutes_left"] = 3
        response = form.submit()

        # assert results
        timer_date = now() + timedelta(days=1, hours=2, minutes=3)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        obj = Timer.objects.get(structure_name="Timer 4")
        self.assertEqual(obj.eve_solar_system, solar_system)
        self.assertEqual(obj.structure_type, structure_type)
        self.assertEqual(obj.timer_type, Timer.Type.ANCHORING)
        self.assertAlmostEqual(obj.date, timer_date, delta=timedelta(seconds=10))

    def test_user_without_permission_can_not_add_timer(self):
        # login
        self.app.set_user(UserNoAccessFactory())

        # Try to access page
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:timer_list"))

    def test_user_with_permission_can_edit_his_timer(self):
        # setup
        user = UserWithCreateFactory()
        timer = TimerFactory(user=user)

        # login
        self.app.set_user(user)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, HTTPStatus.OK)

        # user clicks on "Edit Timer" for timer
        edit_timer = self.app.get(reverse("structuretimers:edit", args=[timer.pk]))
        self.assertEqual(edit_timer.status_code, HTTPStatus.OK)

        # user enters data and clicks create
        form = edit_timer.forms["add-timer-form"]
        form["owner_name"] = "The Boys"
        response = form.submit()
        timer.refresh_from_db()

        # assert results
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertEqual(timer.owner_name, "The Boys")

    def test_user_without_permission_can_not_edit_a_timer(self):
        # setup
        user = UserWithAccessFactory()
        timer = TimerFactory()

        # login
        self.app.set_user(user)

        # user tries to access page for edit directly
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:edit", args=[timer.pk]))

    def test_user_with_normal_permission_can_not_edit_other_timers(self):
        # setup
        user = UserWithCreateFactory()
        timer = TimerFactory()

        # login
        self.app.set_user(user)

        # user tries to access page for edit directly
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:edit", args=[timer.pk]))

    def test_manager_can_edit_other_timers(self):
        # setup
        user = UserWithManageFactory()
        timer = TimerFactory()

        # login
        self.app.set_user(user)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, HTTPStatus.OK)

        # user clicks on "Edit Timer" for timer 1
        edit_timer = self.app.get(reverse("structuretimers:edit", args=[timer.pk]))
        self.assertEqual(edit_timer.status_code, HTTPStatus.OK)

        # user enters data and clicks create
        form = edit_timer.forms["add-timer-form"]
        form["owner_name"] = "The Boys"
        response = form.submit()
        timer.refresh_from_db()

        # assert results
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertEqual(timer.owner_name, "The Boys")

    def test_manager_can_not_edit_other_timers_when_corp_restricted(self):
        # setup
        user = UserWithManageFactory()
        timer = TimerFactory(visibility=Timer.Visibility.CORPORATION)

        # login
        self.app.set_user(user)

        # user tries to access page for edit directly
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:edit", args=[timer.pk]))

    def test_manager_can_not_edit_other_timers_when_opsec(self):
        # setup
        user = UserWithManageFactory()
        timer = TimerFactory(is_opsec=True)

        # login
        self.app.set_user(user)

        # user tries to access page for edit directly
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:edit", args=[timer.pk]))

    def test_manager_can_delete_timer_from_other(self):
        # setup
        user = UserWithManageFactory()
        timer = TimerFactory()

        # login
        self.app.set_user(user)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, HTTPStatus.OK)

        # user clicks on "Delete Timer" for timer 2
        confirm_page = self.app.get(reverse("structuretimers:delete", args=[timer.pk]))
        self.assertEqual(confirm_page.status_code, HTTPStatus.OK)

        # user enters data and clicks create
        form = confirm_page.forms["confirm-delete-form"]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_user_can_delete_own_timer(self):
        # setup
        user = UserWithCreateFactory()
        timer = TimerFactory(user=user)

        # login
        self.app.set_user(user)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, HTTPStatus.OK)

        # user clicks on "Delete Timer" for timer 2
        confirm_page = self.app.get(reverse("structuretimers:delete", args=[timer.pk]))
        self.assertEqual(confirm_page.status_code, HTTPStatus.OK)

        # user enters data and clicks create
        form = confirm_page.forms["confirm-delete-form"]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_user_can_not_delete_timer_from_others(self):
        # setup
        user = UserWithCreateFactory()
        timer = TimerFactory()

        # login
        self.app.set_user(user)

        # user tries to access page for edit directly
        with self.assertRaises(AppError):
            self.app.get(reverse("structuretimers:delete", args=[timer.pk]))


"""
@patch(MODELS_PATH+ ".sleep", new=lambda x: x)
@patch(MODELS_PATH+ ".dhooks_lite.Webhook.execute")
class TestSendNotifications(LoadTestDataMixin, TestCase):
    def setUp(self) -> None:
        self.webhook = DiscordWebhookFactory(
            name="Dummy", url="http://www.example.com"
        )
        self.rule = NotificationRule.objects.create(minutes=NotificationRule.MINUTES_0)
        self.rule.webhooks.add(self.webhook)

    def test_normal(self, mock_execute):
        TimerFactory(
            structure_name="Test_1",
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now() + timedelta(seconds=2),
        )
        sleep(3)
        self.assertEqual(mock_execute.call_count, 1)
"""


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".sleep", new=lambda x: x)
@patch(TASKS_PATH + ".notify", spec=True)
@patch(MODELS_PATH + ".dhooks_lite.Webhook.execute", spec=True)
class TestSendTestMessageToWebhook(NoSocketsTestCase):
    def test_without_user(self, mock_execute, mock_notify):
        # given
        webhook = DiscordWebhookFactory()

        # when
        send_test_message_to_webhook.delay(webhook_pk=webhook.pk)

        # then
        self.assertEqual(mock_execute.call_count, 1)
        self.assertFalse(mock_notify.called)

    def test_with_user(self, mock_execute, mock_notify):
        # given
        webhook = DiscordWebhookFactory()
        user = UserWithAccessFactory()

        # when
        send_test_message_to_webhook.delay(webhook_pk=webhook.pk, user_pk=user.pk)

        # then
        self.assertEqual(mock_execute.call_count, 1)
        self.assertTrue(mock_notify.called)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
class TestTimerSave(NoSocketsTestCase):
    def test_schedule_notifications_for_new_timers_2(self):
        # given
        NotificationRuleFactory()

        # when
        timer = Timer.objects.create(
            date=now() + timedelta(hours=4),
            eve_solar_system=EveSolarSystemLowSecFactory(),
            structure_type=CitadelTypeFactory(),
        )
        # then
        self.assertTrue(ScheduledNotification.objects.filter(timer=timer).exists())
