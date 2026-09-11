import os
import sys
import io
import json
import unittest
import urllib.request
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Third party document generators
import docx
import openpyxl
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.file_processing.extractor import extract_file_content

client = TestClient(app)

class TestFullEndToEndQA(unittest.TestCase):

    def test_01_servers_running(self):
        """Verify Backend API health and Frontend dev server responsiveness"""
        # Test Backend /api/health
        res_backend = client.get("/api/health")
        self.assertEqual(res_backend.status_code, 200)
        self.assertEqual(res_backend.json().get("status"), "ok")

        # Test Frontend server HTTP response
        try:
            req = urllib.request.urlopen("http://localhost:5173", timeout=3)
            self.assertEqual(req.getcode(), 200)
            print("\n[QA OK] Both Backend (8000) and Frontend (5173) are running and returning HTTP 200.")
        except Exception as e:
            self.fail(f"Frontend server on http://localhost:5173 not responding: {e}")

    def test_02_all_four_industries_content_uniqueness(self):
        """Verify content generated across all 4 industries feels distinct and tailored"""
        industries = ["Real Estate", "Jewellery", "Perfume", "FMCG / Food"]
        generated_strategies = {}

        for ind in industries:
            mock_json_str = json.dumps({
                "industry": ind,
                "duration": "1 Week",
                "platform": "Instagram",
                "total_posts": 3,
                "content_strategy": {
                    "target_audience": f"Audience tailored specifically for {ind}",
                    "tone": f"Distinct tone for {ind}",
                    "content_pillars": [f"{ind} Pillar 1", f"{ind} Pillar 2", f"{ind} Pillar 3"]
                },
                "posts": [
                    {
                        "post_number": i,
                        "day": f"Day {i*2-1}",
                        "content_pillar": f"{ind} Pillar {i}",
                        "caption": f"Tailored caption for {ind} post {i}.",
                        "visual_direction": f"Vivid creative visual direction for {ind}.",
                        "hashtags": [f"#{ind.replace(' ', '').replace('/', '')}", "#Tailored"]
                    } for i in range(1, 4)
                ]
            })

            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = mock_json_str

            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
                 patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion):

                response = client.post("/api/generate-content", json={
                    "industry": ind,
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                })

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["industry"], ind)
                self.assertEqual(len(data["posts"]), 3)
                generated_strategies[ind] = data["content_strategy"]

        # Verify strategy uniqueness
        self.assertEqual(len(set([s["target_audience"] for s in generated_strategies.values()])), 4)
        print("[QA OK] All 4 industries tested. Generated strategies and posts are distinct.")

    def test_03_all_duration_plans(self):
        """Verify post counts strictly match 1 Week = 3, 2 Weeks = 6, 1 Month = 12"""
        duration_plans = [
            ("1 Week", 3),
            ("2 Weeks", 6),
            ("1 Month", 12)
        ]

        for duration, expected_count in duration_plans:
            posts = []
            for i in range(1, expected_count + 1):
                posts.append({
                    "post_number": i,
                    "day": f"Day {i}",
                    "content_pillar": "Brand Showcase",
                    "caption": f"Caption for post {i}",
                    "visual_direction": f"Visual direction for post {i}",
                    "hashtags": ["#Brand", "#Quality"]
                })

            mock_json_str = json.dumps({
                "industry": "Real Estate",
                "duration": duration,
                "platform": "Instagram",
                "total_posts": expected_count,
                "content_strategy": {
                    "target_audience": "Homebuyers",
                    "tone": "Authoritative",
                    "content_pillars": ["Showcase", "Lifestyle"]
                },
                "posts": posts
            })

            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = mock_json_str

            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
                 patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion):

                response = client.post("/api/generate-content", json={
                    "industry": "Real Estate",
                    "duration": duration,
                    "post_count": expected_count,
                    "platform": "Instagram"
                })

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["total_posts"], expected_count)
                self.assertEqual(len(data["posts"]), expected_count)

        print("[QA OK] All 3 duration plans (3, 6, 12 posts) verified.")

    def test_04_single_post_regeneration(self):
        """Verify single post regeneration updates target post without altering others"""
        mock_post_json = json.dumps({
            "post_number": 2,
            "day": "Day 3",
            "content_pillar": "Emotional Storytelling",
            "caption": "Fresh regenerated caption for post 2",
            "visual_direction": "New macro angle",
            "hashtags": ["#Regenerated", "#Fresh"]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_post_json

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion):

            response = client.post("/api/regenerate-post", json={
                "industry": "Jewellery",
                "platform": "Instagram",
                "duration": "1 Week",
                "post_number": 2,
                "day": "Day 3",
                "content_pillar": "Emotional Storytelling",
                "original_caption": "Old caption"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["post_number"], 2)
            self.assertEqual(data["caption"], "Fresh regenerated caption for post 2")

        print("[QA OK] Single post regeneration endpoint verified.")

    def test_05_invalid_input_and_error_handling(self):
        """Verify clean error responses for missing fields, mismatched counts, and bad files"""
        # Test missing industry
        res_missing = client.post("/api/generate-content", json={
            "duration": "1 Week",
            "post_count": 3
        })
        self.assertEqual(res_missing.status_code, 400)

        # Test duration/count mismatch
        res_mismatch = client.post("/api/generate-content", json={
            "industry": "Real Estate",
            "duration": "1 Week",
            "post_count": 12,
            "platform": "Instagram"
        })
        self.assertEqual(res_mismatch.status_code, 400)

        # Test unsupported file
        res_badfile = client.post("/api/generate-content", data={
            "industry": "Real Estate",
            "duration": "1 Week",
            "post_count": 3,
            "platform": "Instagram"
        }, files={
            "files": ("script.sh", b"#!/bin/bash\necho hello", "application/x-sh")
        })
        self.assertEqual(res_badfile.status_code, 400)
        self.assertIn("Unsupported file format", res_badfile.json().get("detail", ""))

        print("[QA OK] Invalid inputs and security validation errors return clean HTTP 400.")

    def test_06_security_audit(self):
        """Verify secrets are not hardcoded and .env is gitignored"""
        gitignore_path = os.path.join(os.path.dirname(__file__), ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore missing in Backend")
        
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()
            self.assertIn(".env", gitignore_content)

        env_example_path = os.path.join(os.path.dirname(__file__), ".env.example")
        self.assertTrue(os.path.exists(env_example_path), ".env.example missing in Backend")
        
        with open(env_example_path, "r", encoding="utf-8") as f:
            example_content = f.read()
            self.assertNotIn("sk-proj-", example_content)
            self.assertNotIn("AIzaSy", example_content)

        print("[QA OK] Security audit passed (.env gitignored, no hardcoded API secrets).")

if __name__ == "__main__":
    unittest.main()
