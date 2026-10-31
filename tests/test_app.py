import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app, generate_character  # noqa: E402

REQUIRED_KEYS = [
    "name", "age", "gender", "job", "personalities",
    "hobby", "skill", "catchphrase", "favorite", "bio",
]


class TestGenerateCharacter(unittest.TestCase):
    def test_required_fields(self):
        c = generate_character(12345)
        for key in REQUIRED_KEYS:
            self.assertIn(key, c)
            self.assertTrue(c[key], f"{key} が空です")

    def test_field_constraints(self):
        for seed in range(50):
            c = generate_character(seed)
            self.assertTrue(18 <= c["age"] <= 60)
            self.assertIn(c["gender"], ["女性", "男性"])
            self.assertIn(len(c["personalities"]), (2, 3))
            self.assertIn(c["name"], c["bio"])

    def test_same_seed_reproducible(self):
        self.assertEqual(generate_character(777), generate_character(777))

    def test_different_seeds_differ(self):
        chars = [generate_character(s) for s in range(10)]
        # 10件すべて同一にはならない（ランダム性がある）
        self.assertGreater(len({c["name"] for c in chars}), 1)
        self.assertGreater(len({c["bio"] for c in chars}), 1)


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok"})

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("charamaker", res.get_data(as_text=True))

    def test_index_with_seed_reproducible(self):
        body1 = self.client.get("/?seed=42").get_data(as_text=True)
        body2 = self.client.get("/?seed=42").get_data(as_text=True)
        self.assertEqual(body1, body2)

    def test_img_returns_png(self):
        res = self.client.get("/img?seed=42")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "image/png")
        self.assertTrue(res.data.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_img_same_seed_same_bytes(self):
        a = self.client.get("/img?seed=99").data
        b = self.client.get("/img?seed=99").data
        self.assertEqual(a, b)

    def test_invalid_seed_no_500(self):
        for url in ["/?seed=abc", "/img?seed=abc", "/img?seed=", "/?seed=%"]:
            res = self.client.get(url)
            self.assertNotEqual(res.status_code, 500, url)
            self.assertEqual(res.status_code, 200, url)


if __name__ == "__main__":
    unittest.main()
