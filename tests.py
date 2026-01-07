import unittest
from enrichment import enrich_offline
from message_gen import EMAIL_TEMPLATES

class TestLeadSystem(unittest.TestCase):

    def test_enrichment_structure(self):
        """Test that offline enrichment returns all required fields."""
        dummy_lead = {
            "industry": "Technology",
            "role": "CTO",
            "company_name": "TechCorp"
        }
        result = enrich_offline(dummy_lead)
        
        self.assertIn("company_size", result)
        self.assertIn("pain_points", result)
        self.assertIn("buying_triggers", result)
        self.assertGreater(result["confidence_score"], 0)
        print("✓ Enrichment Structure Valid")

    def test_message_templates(self):
        """Test that templates format correctly without errors."""
        # Test Email Variant A
        tmpl_a = EMAIL_TEMPLATES["A"]
        formatted = tmpl_a.format(
            first_name="John",
            company="Acme",
            industry="Tech",
            role="Dev",
            pain_point="costs",
            size="Small"
        )
        self.assertIn("John", formatted)
        self.assertIn("Acme", formatted)
        print("✓ Message Templates Valid")

if __name__ == '__main__':
    unittest.main()