from django.test import TestCase


class SimpleTest(TestCase):
    def test_home_status(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
