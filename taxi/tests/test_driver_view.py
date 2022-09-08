from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Driver

DRIVER_URL = reverse("taxi:driver-list")


class PublicDriverTests(TestCase):
    def test_login_required(self):
        res = self.client.get(DRIVER_URL)

        self.assertNotEqual(res.status_code, 200)


class PrivateDriverTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "test",
            "test12345"
        )
        self.client.force_login(self.user)

    def test_retrieve_drivers(self):
        Driver.objects.create(username="test1", password="test1", license_number="TES12345")
        res = self.client.get(DRIVER_URL)
        drivers = Driver.objects.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            list(res.context["driver_list"]), list(drivers)
        )
        self.assertTemplateUsed(res, "taxi/driver_list.html")
