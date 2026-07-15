"""Unit tests for deterministic recommendation tools."""

import unittest

from weather_outfit_adk.tools import classify_activity, plan_outfit, check_safety


class ToolTests(unittest.TestCase):
    def test_hiking_is_sport_activity(self):
        result = classify_activity("Going hiking this afternoon")
        self.assertEqual(result["category"], "sports")
        self.assertEqual(result["movement_level"], "high")

    def test_cold_weather_adds_outerwear(self):
        result = plan_outfit(
            temperature=25,
            rain_chance=10,
            wind_speed=5,
            activity_category="casual",
        )
        self.assertEqual(result["outer_layer"], "heavy winter coat")
        self.assertIn("gloves", result["accessories"])

    def test_extreme_heat_is_high_risk(self):
        result = check_safety(temperature=100, wind_speed=4, rain_chance=0)
        self.assertEqual(result["risk_level"], "high")
        self.assertTrue(result["has_warnings"])


if __name__ == "__main__":
    unittest.main()
