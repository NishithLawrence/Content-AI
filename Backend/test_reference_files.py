import os
import sys
import io
import json
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Third-party document generators for tests
import docx
import openpyxl
from reportlab.pdfgen import canvas
import pypdf

load_dotenv()

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.file_processing.extractor import extract_file_content, extract_reference_context
from app.models.content import GeneratedContentResponse

client = TestClient(app)

class TestReferenceFileIntelligence(unittest.TestCase):

    def _create_test_pdf_bytes(self, brand: str, location: str, usp: str) -> bytes:
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(100, 750, f"Brand: {brand}")
        c.drawString(100, 730, f"Location: {location}")
        c.drawString(100, 710, f"USP: {usp}")
        c.save()
        return buf.getvalue()

    def _create_test_docx_bytes(self, property_name: str, config: str, location: str) -> bytes:
        doc = docx.Document()
        doc.add_heading(property_name, 0)
        doc.add_paragraph(f"Configuration: {config}")
        doc.add_paragraph(f"Location: {location}")
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _create_test_xlsx_bytes(self, product: str, ingredients: str, usp: str) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Product Details"
        ws.append(["Product Name", "Ingredients", "USP"])
        ws.append([product, ingredients, usp])
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def test_01_jewellery_pdf_extraction_and_grounding(self):
        """TEST 1: Jewellery + PDF containing brand information (Aurelia Jewels, Chennai, Handcrafted solitaire)"""
        pdf_bytes = self._create_test_pdf_bytes("Aurelia Jewels", "Chennai", "Handcrafted solitaire jewellery")
        
        # Verify extraction
        extracted_text = extract_file_content(pdf_bytes, "brand_profile.pdf", ".pdf")
        self.assertIn("Aurelia Jewels", extracted_text)
        self.assertIn("Chennai", extracted_text)
        self.assertIn("Handcrafted solitaire jewellery", extracted_text)

        # Mock AI completion that adheres to grounding rules
        mock_json_str = json.dumps({
            "industry": "Jewellery",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Fine jewelry collectors",
                "tone": "Exquisite & Timeless",
                "content_pillars": ["Artisanal Craftsmanship", "Emotional Storytelling", "Bespoke Design"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Artisanal Craftsmanship",
                    "caption": "Discover timeless elegance with Aurelia Jewels in Chennai. Our handcrafted solitaire jewellery brings unmatched sparkle.",
                    "visual_direction": "Close-up macro shot of solitaire ring reflecting warm light.",
                    "hashtags": ["#AureliaJewels", "#ChennaiLuxury", "#HandcraftedSolitaire"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Emotional Storytelling",
                    "caption": "Every piece from Aurelia Jewels celebrates lifetime milestones. Visit our Chennai boutique.",
                    "visual_direction": "Elegant bridal model wearing custom necklace.",
                    "hashtags": ["#JewelleryDesign", "#AureliaJewels"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Bespoke Design",
                    "caption": "Handcrafted solitaire masterpieces crafted exclusively for you at Aurelia Jewels.",
                    "visual_direction": "Jeweler shaping 18k gold setting on workbench.",
                    "hashtags": ["#BespokeJewelry", "#SolitaireRing"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "Jewellery",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                },
                files={
                    "files": ("brand_profile.pdf", pdf_bytes, "application/pdf")
                }
            )

            self.assertEqual(response.status_code, 200, f"Error: {response.text}")
            data = response.json()
            
            # Grounding check: verify generated content uses reference facts
            all_captions = " ".join([p["caption"] for p in data["posts"]])
            self.assertIn("Aurelia Jewels", all_captions)
            self.assertIn("Chennai", all_captions)

    def test_02_real_estate_docx_extraction_and_grounding(self):
        """TEST 2: Real Estate + DOCX containing property details (Grand Horizon Towers, 3 BHK, Bangalore)"""
        docx_bytes = self._create_test_docx_bytes("Grand Horizon Towers", "3 BHK Luxury Apartments", "Bangalore")
        
        extracted_text = extract_file_content(docx_bytes, "property_details.docx", ".docx")
        self.assertIn("Grand Horizon Towers", extracted_text)
        self.assertIn("3 BHK Luxury Apartments", extracted_text)
        self.assertIn("Bangalore", extracted_text)

        mock_json_str = json.dumps({
            "industry": "Real Estate",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Prospective homebuyers",
                "tone": "Aspirational & Sophisticated",
                "content_pillars": ["Architectural & Interior Design", "Luxury Amenities", "Location & Neighborhood Vibe"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Architectural & Interior Design",
                    "caption": "Experience luxury living at Grand Horizon Towers in Bangalore. Offering spacious 3 BHK Luxury Apartments.",
                    "visual_direction": "Wide shot of high-rise elevation bathed in sunset glow.",
                    "hashtags": ["#GrandHorizonTowers", "#BangaloreRealEstate", "#3BHKApartments"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Luxury Amenities",
                    "caption": "Unmatched comfort awaits you at Grand Horizon Towers, Bangalore.",
                    "visual_direction": "Infinity pool overlooking city skyline.",
                    "hashtags": ["#LuxuryLiving", "#BangaloreHomes"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Location & Neighborhood Vibe",
                    "caption": "Prime location connectivity at Grand Horizon Towers in Bangalore.",
                    "visual_direction": "Aerial drone capture of surrounding greenery.",
                    "hashtags": ["#PrimeLocation", "#BangaloreProperty"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "Real Estate",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                },
                files={
                    "files": ("property_details.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                }
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            all_captions = " ".join([p["caption"] for p in data["posts"]])
            self.assertIn("Grand Horizon Towers", all_captions)
            self.assertIn("Bangalore", all_captions)

    def test_03_perfume_txt_extraction_and_grounding(self):
        """TEST 3: Perfume + TXT containing fragrance information (Velvet Rose & Oud, Bergamot, Damask Rose)"""
        txt_content = "Fragrance Name: Velvet Rose & Oud\nTop Notes: Bergamot\nHeart Notes: Damask Rose\nBase Notes: Oud & Amber"
        txt_bytes = txt_content.encode('utf-8')

        extracted_text = extract_file_content(txt_bytes, "fragrance_notes.txt", ".txt")
        self.assertIn("Velvet Rose & Oud", extracted_text)
        self.assertIn("Bergamot", extracted_text)

        mock_json_str = json.dumps({
            "industry": "Perfume",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Fragrance connoisseurs",
                "tone": "Sensual & Intimate",
                "content_pillars": ["Scent Pyramid Breakdown", "Mood & Emotional Resonance", "Atmospheric Storytelling"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Scent Pyramid Breakdown",
                    "caption": "Immerse in Velvet Rose & Oud. Opening with crisp Bergamot, evolving into a heart of rich Damask Rose.",
                    "visual_direction": "Perfume bottle sitting beside fresh bergamot slices and red rose petals.",
                    "hashtags": ["#VelvetRoseOud", "#NicheFragrance"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Mood & Emotional Resonance",
                    "caption": "Let Velvet Rose & Oud leave a lingering trail of warm amber and oud.",
                    "visual_direction": "Moody aesthetic with warm golden light reflecting off crystal bottle.",
                    "hashtags": ["#SignatureScent", "#PerfumeLovers"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Atmospheric Storytelling",
                    "caption": "An olfactory journey embodied in Velvet Rose & Oud.",
                    "visual_direction": "Silhouetted bottle in soft candlelight.",
                    "hashtags": ["#LuxuryFragrance", "#OudNotes"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "Perfume",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                },
                files={
                    "files": ("fragrance_notes.txt", txt_bytes, "text/plain")
                }
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            all_captions = " ".join([p["caption"] for p in data["posts"]])
            self.assertIn("Velvet Rose & Oud", all_captions)
            self.assertIn("Bergamot", all_captions)

    def test_04_food_xlsx_extraction_and_grounding(self):
        """TEST 4: Food + XLSX containing product specs (Organic Oat Crunch, Rolled Oats)"""
        xlsx_bytes = self._create_test_xlsx_bytes("Organic Oat Crunch", "Rolled Oats, Honey, Almonds", "100% Organic Whole Grain")

        extracted_text = extract_file_content(xlsx_bytes, "product_specs.xlsx", ".xlsx")
        self.assertIn("Organic Oat Crunch", extracted_text)
        self.assertIn("Rolled Oats, Honey, Almonds", extracted_text)

        mock_json_str = json.dumps({
            "industry": "FMCG / Food",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Health-conscious food lovers",
                "tone": "Appetizing & Approachable",
                "content_pillars": ["Quality Ingredients", "Quick & Easy Serving", "Product Benefits"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Quality Ingredients",
                    "caption": "Fuel your morning with Organic Oat Crunch! Packed with wholesome Rolled Oats, Honey, and Almonds.",
                    "visual_direction": "Overhead bowl shot of crunchy granola topped with fresh berries and Greek yogurt.",
                    "hashtags": ["#OrganicOatCrunch", "#RolledOats", "#HealthyBreakfast"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Quick & Easy Serving",
                    "caption": "Enjoy effortless energy anytime with Organic Oat Crunch.",
                    "visual_direction": "Hands pouring milk into a vibrant ceramic breakfast bowl.",
                    "hashtags": ["#SnackTime", "#OrganicFood"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Product Benefits",
                    "caption": "100% Organic Whole Grain goodness in every bite of Organic Oat Crunch.",
                    "visual_direction": "Macro shot highlighting golden honey glaze on almond oat clusters.",
                    "hashtags": ["#WholeGrain", "#CleanEating"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "FMCG / Food",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                },
                files={
                    "files": ("product_specs.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                }
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            all_captions = " ".join([p["caption"] for p in data["posts"]])
            self.assertIn("Organic Oat Crunch", all_captions)
            self.assertIn("Rolled Oats", all_captions)

    def test_05_generation_without_reference_files(self):
        """TEST 5: Generation with no reference files must still work"""
        mock_json_str = json.dumps({
            "industry": "Real Estate",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Homebuyers",
                "tone": "Authoritative",
                "content_pillars": ["Location & Neighborhood Vibe", "Architectural Design", "Investment Potential"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Location & Neighborhood Vibe",
                    "caption": "Discover prime urban sanctuary living with panoramic city views.",
                    "visual_direction": "Sun-drenched living room with floor-to-ceiling glass.",
                    "hashtags": ["#PrimeRealEstate", "#UrbanSanctuary"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Architectural Design",
                    "caption": "Bespoke finishes and seamless indoor-outdoor flow redefine living spaces.",
                    "visual_direction": "Architectural shot of modern villa terrace.",
                    "hashtags": ["#ArchitectureDetail", "#BespokeLiving"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Investment Potential",
                    "caption": "Building long-term wealth through premium location property milestones.",
                    "visual_direction": "Clean graphic displaying home appreciation trends.",
                    "hashtags": ["#PropertyInvestment", "#RealEstateROI"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "Real Estate",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                }
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["total_posts"], 3)
            self.assertEqual(len(data["posts"]), 3)

    def test_06_unsupported_file_returns_clean_400_error(self):
        """TEST 6: Unsupported file (.exe or .zip) must return clean HTTP 400 validation error"""
        bad_file_bytes = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"

        response = client.post(
            "/api/generate-content",
            data={
                "industry": "Real Estate",
                "duration": "1 Week",
                "post_count": 3,
                "platform": "Instagram"
            },
            files={
                "files": ("malicious_program.exe", bad_file_bytes, "application/octet-stream")
            }
        )

        self.assertEqual(response.status_code, 400)
        detail = response.json().get("detail", "")
        self.assertIn("Unsupported file format '.exe'", detail)
        self.assertIn("Supported formats", detail)

    def test_07_multiple_reference_files_combined(self):
        """TEST 7: Multiple reference files combined into single reference context"""
        pdf_bytes = self._create_test_pdf_bytes("Aurelia Jewels", "Chennai", "Handcrafted solitaire jewellery")
        txt_bytes = b"Special Offers: Complimentary anniversary polishing for all solitaire purchases."

        mock_json_str = json.dumps({
            "industry": "Jewellery",
            "duration": "1 Week",
            "platform": "Instagram",
            "total_posts": 3,
            "content_strategy": {
                "target_audience": "Collectors",
                "tone": "Exquisite",
                "content_pillars": ["Artisanal Craftsmanship", "Milestone Occasions", "Collector Care"]
            },
            "posts": [
                {
                    "post_number": 1,
                    "day": "Day 1",
                    "content_pillar": "Artisanal Craftsmanship",
                    "caption": "Handcrafted solitaire excellence at Aurelia Jewels in Chennai.",
                    "visual_direction": "Macro diamond detail.",
                    "hashtags": ["#AureliaJewels"]
                },
                {
                    "post_number": 2,
                    "day": "Day 3",
                    "content_pillar": "Milestone Occasions",
                    "caption": "Mark your moments in Chennai with Aurelia Jewels.",
                    "visual_direction": "Bridal portrait.",
                    "hashtags": ["#Milestones"]
                },
                {
                    "post_number": 3,
                    "day": "Day 5",
                    "content_pillar": "Collector Care",
                    "caption": "Preserve brilliance with complimentary anniversary polishing at Aurelia Jewels.",
                    "visual_direction": "Jewelry care cleaning shot.",
                    "hashtags": ["#JewelryCare"]
                }
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_json_str

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}), \
             patch("openai.resources.chat.completions.completions.Completions.create", return_value=mock_completion):
            
            response = client.post(
                "/api/generate-content",
                data={
                    "industry": "Jewellery",
                    "duration": "1 Week",
                    "post_count": 3,
                    "platform": "Instagram"
                },
                files=[
                    ("files", ("brand_profile.pdf", pdf_bytes, "application/pdf")),
                    ("files", ("offers.txt", txt_bytes, "text/plain"))
                ]
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            all_captions = " ".join([p["caption"] for p in data["posts"]])
            self.assertIn("Aurelia Jewels", all_captions)
            self.assertIn("complimentary anniversary polishing", all_captions)

if __name__ == "__main__":
    unittest.main()
