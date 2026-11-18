from django.test import TestCase

from .matching import match_skills
from .scam import screen_advert


class ScamScreeningTests(TestCase):
    def test_high_risk(self):
        text = (
            "URGENT! Guaranteed job in Dubai, no interview. Pay a KES 5,000 "
            "registration fee and send your ID copy to jobs@gmail.com or WhatsApp us only."
        )
        result = screen_advert(text)
        self.assertEqual(result["level"], "High")
        self.assertIn("Asks for a fee or deposit", result["indicators"])

    def test_medium_risk(self):
        result = screen_advert("Pay a registration fee to secure your slot. Apply now.")
        self.assertEqual(result["level"], "Medium")

    def test_low_risk(self):
        text = "We are hiring a Python developer in Nairobi. Apply through our careers page."
        result = screen_advert(text)
        self.assertEqual(result["level"], "Low")
        self.assertEqual(result["indicators"], [])


class MatchingTests(TestCase):
    def test_only_confirmed_skills_count(self):
        result = match_skills("Looking for Python, Django and SQL skills", ["Python", "SQL"])
        self.assertEqual(result["matched"], ["python", "sql"])
        self.assertEqual(result["missing"], ["django"])
        self.assertEqual(result["score"], 67)

    def test_no_required_skills(self):
        result = match_skills("A friendly team player wanted", [])
        self.assertEqual(result["score"], 0)