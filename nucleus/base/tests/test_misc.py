from django.test import TestCase


class TestContribute(TestCase):
    def test_contribute_json(self):
        response = self.client.get("/contribute.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
