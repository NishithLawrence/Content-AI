import os
import sys
import unittest

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ai_service import extract_json_payload, strip_json_comments_and_sanitize

class TestGeminiJSONParser(unittest.TestCase):

    def test_A_clean_json(self):
        raw = '{"industry": "Real Estate", "duration": "1 Week", "platform": "Instagram", "total_posts": 3, "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]}, "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]}'
        res = extract_json_payload(raw)
        self.assertEqual(res["industry"], "Real Estate")
        self.assertIn("posts", res)

    def test_B_fenced_json(self):
        raw = """```json
{"industry": "Real Estate", "duration": "1 Week", "platform": "Instagram", "total_posts": 3, "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]}, "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]}
```"""
        res = extract_json_payload(raw)
        self.assertEqual(res["industry"], "Real Estate")

    def test_C_intro_outro_text(self):
        raw = """Here is your custom content plan:
```json
{"industry": "Real Estate", "duration": "1 Week", "platform": "Instagram", "total_posts": 3, "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]}, "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]}
```
Hope this helps your marketing team!"""
        res = extract_json_payload(raw)
        self.assertEqual(res["duration"], "1 Week")

    def test_D_inline_comments(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 3, // EXACT post count required
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        self.assertEqual(res["total_posts"], 3)

    def test_E_standalone_comments(self):
        raw = """{
  // Primary configuration
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 3,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        self.assertEqual(res["industry"], "Real Estate")

    def test_F_block_comments(self):
        raw = """{
  /* Industry Framework
     Target audience & tone */
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 3,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        self.assertEqual(res["industry"], "Real Estate")

    def test_G_trailing_commas(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 3,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase",],},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"],},],
}"""
        res = extract_json_payload(raw)
        self.assertEqual(res["total_posts"], 3)

    def test_H_posts_as_dictionary(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": {
    "1": {"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}
  }
}"""
        res = extract_json_payload(raw)
        self.assertIn("posts", res)
        # Normalize dict to list
        if isinstance(res["posts"], dict):
            res["posts"] = list(res["posts"].values())
        self.assertIsInstance(res["posts"], list)
        self.assertEqual(len(res["posts"]), 1)

    def test_I_nested_outer_wrapper(self):
        raw = """{
  "content_calendar": {
    "industry": "Real Estate",
    "duration": "1 Week",
    "platform": "Instagram",
    "total_posts": 1,
    "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
    "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Test", "visual_direction": "Room", "hashtags": ["#home"]}]
  }
}"""
        res = extract_json_payload(raw)
        self.assertIn("posts", res)
        self.assertEqual(res["industry"], "Real Estate")

    def test_J_https_url_in_string(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Check out https://example.com/property for virtual tour!", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertIn("https://example.com/property", caption)

    def test_K_http_url_in_string(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Check out http://example.com/property for virtual tour!", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertIn("http://example.com/property", caption)

    def test_L_literal_newline_in_caption(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Welcome to luxury living.
Second line of caption.", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertIn("\nSecond line of caption.", caption)

    def test_M_multiple_literal_paragraph_breaks(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Hook line here!

Body line here with spacing!

CTA line here!", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertIn("Hook line here!\n\nBody line here", caption)

    def test_N_already_escaped_newline_not_double_escaped(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "First line\\nSecond line", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertEqual(caption, "First line\nSecond line")

    def test_O_escaped_quotes_in_string(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Featured in \\"Architectural Digest\\" magazine!", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertIn('"Architectural Digest"', caption)

    def test_P_https_url_remains_unchanged(self):
        raw = """{
  "industry": "Real Estate",
  "duration": "1 Week",
  "platform": "Instagram",
  "total_posts": 1,
  "content_strategy": {"target_audience": "Buyers", "tone": "Friendly", "content_pillars": ["Showcase"]},
  "posts": [{"post_number": 1, "day": "Day 1", "content_pillar": "Showcase", "caption": "Visit https://luxuryrealestate.com/123-main-st for listing!", "visual_direction": "Room", "hashtags": ["#home"]}]
}"""
        res = extract_json_payload(raw)
        caption = res["posts"][0]["caption"]
        self.assertEqual(caption, "Visit https://luxuryrealestate.com/123-main-st for listing!")

if __name__ == "__main__":
    unittest.main()
