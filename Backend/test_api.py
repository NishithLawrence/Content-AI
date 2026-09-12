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
from app.models.content import GeneratedContentResponse, ContentStrategy, GeneratedPost

client = TestClient(app)

class TestContentPlatformAPI(unittest.TestCase):

    def test_01_health_check(self):
        """Test GET /api/health endpoint"""
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")

    def test_02_missing_api_key(self):
        """Test POST /api/generate-content when API key is missing"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
            payload = {
                "industry": "Real Estate",
                "duration": "1 Week",
                "post_count": 3,
                "platform": "Instagram"
            }
            response = client.post("/api/generate-content", json=payload)
            self.assertEqual(response.status_code, 500)
            self.assertIn("AI API key is not configured.", response.json().get("detail", ""))

    def test_03_invalid_industry_validation(self):
        """Test validation error when invalid industry is provided"""
        payload = {
            "industry": "Automotive",
            "duration": "1 Week",
            "post_count": 3,
            "platform": "Instagram"
        }
        response = client.post("/api/generate-content", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_04_duration_post_count_mismatch(self):
        """Test validation error when post_count does not match duration (1 Week must be 3)"""
        payload = {
            "industry": "Real Estate",
            "duration": "1 Week",
            "post_count": 6,
            "platform": "Instagram"
        }
        response = client.post("/api/generate-content", json=payload)
        self.assertEqual(response.status_code, 400)

    def _create_mock_ai_response(self, industry: str, duration: str, post_count: int, platform: str):
        """Helper to create valid mock AI JSON responses for unit tests"""
        posts = []
        for i in range(1, post_count + 1):
            posts.append({
                "post_number": i,
                "day": f"Day {i}",
                "content_pillar": "Brand Showcase",
                "caption": f"Captivating caption for {industry} post {i}.",
                "visual_direction": f"High quality aesthetic shot for {industry}.",
                "hashtags": [f"#{industry.replace(' ', '').replace('/', '')}", "#Luxury", "#Quality"]
            })

        return json.dumps({
            "industry": industry,
            "duration": duration,
            "platform": platform,
            "total_posts": post_count,
            "content_strategy": {
                "target_audience": "Target audience",
                "tone": "Sophisticated",
                "content_pillars": ["Brand Showcase", "Lifestyle", "Education"]
            },
            "posts": posts
        })

    def test_05_all_four_industries_and_post_counts(self):
        """Test generation flow and validation for all 4 industries across 1 Week (3), 2 Weeks (6), 1 Month (12)"""
        test_cases = [
            ("Real Estate", "1 Week", 3),
            ("Jewellery", "2 Weeks", 6),
            ("Perfume", "1 Month", 12),
            ("FMCG / Food", "1 Week", 3),
        ]

        for industry, duration, expected_count in test_cases:
            mock_json_str = self._create_mock_ai_response(industry, duration, expected_count, "Instagram")

            # Mock OpenAI ChatCompletion response
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = mock_json_str

            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
                 patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
                
                payload = {
                    "industry": industry,
                    "duration": duration,
                    "post_count": expected_count,
                    "platform": "Instagram"
                }
                response = client.post("/api/generate-content", json=payload)
                self.assertEqual(response.status_code, 200, f"Failed for {industry} ({duration})")
                
                data = response.json()
                self.assertEqual(data["industry"], industry)
                self.assertEqual(data["duration"], duration)
                self.assertEqual(data["total_posts"], expected_count)
                self.assertEqual(len(data["posts"]), expected_count)

                # Validate every post contains all 6 required fields
                for post in data["posts"]:
                    self.assertIn("post_number", post)
                    self.assertIn("day", post)
                    self.assertIn("content_pillar", post)
                    self.assertIn("caption", post)
                    self.assertIn("visual_direction", post)
                    self.assertIn("hashtags", post)
                    self.assertIsInstance(post["hashtags"], list)

    def test_06_live_ai_call_if_key_configured(self):
        """Executes live AI API call if OPENAI_API_KEY or GEMINI_API_KEY is configured in .env"""
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("\n[SKIP] Live AI test skipped because OPENAI_API_KEY or GEMINI_API_KEY is not set in .env")
            return

        payload = {
            "industry": "Real Estate",
            "duration": "1 Week",
            "post_count": 3,
            "platform": "Instagram"
        }
        print(f"\n[LIVE TEST] Calling AI provider with key present...")
        response = client.post("/api/generate-content", json=payload)
        self.assertEqual(response.status_code, 200, f"Live call failed: {response.text}")
        data = response.json()
        self.assertEqual(data["total_posts"], 3)
        self.assertEqual(len(data["posts"]), 3)
        print("[LIVE TEST SUCCESS] Generated 3 posts with live AI!")

if __name__ == "__main__":
    unittest.main()
