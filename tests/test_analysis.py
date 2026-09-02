import unittest

from app.analysis import analyze_text


class AnalysisTests(unittest.TestCase):
    def test_extracts_indian_cyber_indicators(self):
        text = "OTP fraud by +919876543210, UPI test@upi, and URL https://example.test/login."
        result = analyze_text(text)
        self.assertIn("+919876543210", result["extracted_indicators"]["phones_india"])
        self.assertIn("test@upi", result["extracted_indicators"]["upi_or_handles"])
        self.assertTrue(any(item["label"] == "financial_cyber_fraud" for item in result["crime_categories"]))

    def test_empty_text_is_low_risk(self):
        result = analyze_text("")
        self.assertEqual(result["risk_score"], 0)


if __name__ == "__main__":
    unittest.main()
