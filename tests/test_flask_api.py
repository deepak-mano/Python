from __future__ import annotations

import unittest

from src.flask_api import create_app


class FlaskApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_validate_endpoint_accepts_valid_address(self) -> None:
        response = self.client.post(
            "/validate",
            json={
                "line1": "111 Wellington St",
                "line2": "",
                "city": "Ottawa",
                "province": "ON",
                "postal_code": "K1A 0A9",
            },
        )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(payload)
        self.assertTrue(payload["is_valid"])
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["normalized_address"]["postal_code"], "K1A 0A9")

    def test_validate_endpoint_rejects_invalid_postal_prefix(self) -> None:
        response = self.client.post(
            "/validate",
            json={
                "line1": "111 Wellington St",
                "line2": "",
                "city": "Ottawa",
                "province": "ON",
                "postal_code": "V1A 0A9",
            },
        )

        payload = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(payload)
        self.assertFalse(payload["is_valid"])
        self.assertTrue(payload["errors"])

    def test_validate_endpoint_rejects_missing_json(self) -> None:
        response = self.client.post("/validate", data="not-json", content_type="text/plain")

        payload = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(payload)
        self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()
