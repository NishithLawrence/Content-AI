import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

class TestPhase4SinglePostRegeneration(unittest.TestCase):

    def test_01_regenerate_single_post(self):
        """Test POST /api/regenerate-post endpoint replacing single post"""
        mock_post_json = json.dumps({
            "post_number": 2,
            "day": "Day 3",
            "content_pillar": "Emotional Storytelling",
            "caption": "Fresh regenerated caption celebrating milestones with Aurelia Jewels.",
            "visual_direction": "New close up angle showing hand craftsmanship.",
            "hashtags": ["#AureliaJewels", "#Regenerated", "#Luxury"]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_post_json

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion):

            payload = {
                "industry": "Jewellery",
                "platform": "Instagram",
                "duration": "1 Week",
                "post_number": 2,
                "day": "Day 3",
                "content_pillar": "Emotional Storytelling",
                "reference_context": "Brand: Aurelia Jewels, Location: Chennai",
                "original_caption": "Old caption to replace."
            }

            response = client.post("/api/regenerate-post", json=payload)
            self.assertEqual(response.status_code, 200, f"Error: {response.text}")
            
            data = response.json()
            self.assertEqual(data["post_number"], 2)
            self.assertEqual(data["day"], "Day 3")
            self.assertEqual(data["content_pillar"], "Emotional Storytelling")
            self.assertIn("Fresh regenerated caption", data["caption"])
            self.assertEqual(len(data["hashtags"]), 3)

if __name__ == "__main__":
    unittest.main()
