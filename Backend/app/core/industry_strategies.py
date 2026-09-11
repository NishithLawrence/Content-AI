"""
Industry Strategy Engine
Provides deep strategic dimensions, tone, vocabulary, pillars, and writing guidelines tailored to each industry.
"""

INDUSTRY_STRATEGIES = {
    "Real Estate": {
        "industry_name": "Real Estate",
        "target_audience": "Prospective homebuyers, property investors, luxury estate seekers, and young professionals looking for quality living spaces.",
        "tone": "Aspirational, authoritative, sophisticated, reassuring, and investment-savvy.",
        "vocabulary": [
            "architectural mastery", "prime location", "panoramic views", "unmatched ROI", 
            "floor-to-ceiling glass", "curated amenities", "sanctuary", "seamless indoor-outdoor flow",
            "bespoke finishes", "turnkey luxury", "vibrant neighborhood", "investment milestone"
        ],
        "strategic_dimensions": [
            "Location", "Amenities", "Lifestyle", "Investment", "Property USP", "Configuration", "Architecture"
        ],
        "content_pillars": [
            "Location & Neighborhood Vibe",
            "Architectural & Interior Design",
            "Luxury Amenities & Lifestyle",
            "Investment Potential & ROI",
            "Property USP & Layout Highlights",
            "Homebuyer Educational Insights"
        ],
        "writing_guidelines": (
            "Focus on spatial dimensions, neighborhood connectivity, natural light, premium fittings, and long-term capital appreciation. "
            "Describe the experience of living in the space, not just room counts."
        ),
        "things_to_avoid": [
            "Generic 'Dream home awaits!' cliches",
            "Vague descriptions without specific design/location context",
            "Over-promising market returns without analytical backing"
        ]
    },

    "Jewellery": {
        "industry_name": "Jewellery",
        "target_audience": "Fine jewelry collectors, bridal buyers, luxury gift givers, and style-conscious connoisseurs.",
        "tone": "Exquisite, romantic, elegant, heirloom-quality, emotional, and timeless.",
        "vocabulary": [
            "master craftsmanship", "hand-selected gems", "18k gold brilliance", "heirloom piece",
            "artisanal precision", "timeless elegance", "luminous sheen", "sentimental treasure",
            "ethically sourced", "captivating sparkle", "statement piece", "enduring romance"
        ],
        "strategic_dimensions": [
            "Craftsmanship", "Luxury", "Occasion", "Design", "Materials", "Emotion", "Gifting"
        ],
        "content_pillars": [
            "Artisanal Craftsmanship & Heritage",
            "Gemstone & Material Excellence",
            "Milestone Occasions & Gifting",
            "Emotional Storytelling & Romance",
            "Bespoke Design & Styling",
            "Collector Care & Preservation"
        ],
        "writing_guidelines": (
            "Highlight the labor of love behind every detail—the setting of stones, polishing of precious metals, and the emotional resonance "
            "of wearing a piece that marks a lifetime milestone."
        ),
        "things_to_avoid": [
            "Cheap bargain sales pitch language ('Hurry cheap prices!')",
            "Superficial posts that ignore craftsmanship and material quality",
            "Repetitive 'Buy this ring today' calls-to-action"
        ]
    },

    "Perfume": {
        "industry_name": "Perfume",
        "target_audience": "Fragrance enthusiasts, luxury scent collectors, beauty tastemakers, and individuals seeking a signature personal scent.",
        "tone": "Evocative, intoxicating, sensual, poetic, sophisticated, and intimate.",
        "vocabulary": [
            "olfactory journey", "top notes of bergamot", "velvety amber heart", "lingering sillage",
            "rare botanicals", "sensory signature", "captivating aura", "whispering musks",
            "artisanal extraction", "evocative mood", "scented ritual", "intimate expression"
        ],
        "strategic_dimensions": [
            "Fragrance notes", "Mood", "Personality", "Lifestyle", "Luxury", "Occasion", "Sensory language"
        ],
        "content_pillars": [
            "Scent Pyramid Breakdown (Top/Heart/Base)",
            "Mood & Emotional Resonance",
            "Personality & Signature Scent Pairing",
            "Scented Rituals & Application Tips",
            "Atmospheric & Sensory Storytelling",
            "Occasion & Seasonal Olfactory Matches"
        ],
        "writing_guidelines": (
            "Paint a sensory picture with words. Describe how the scent evolves on the skin from the initial spray to the warm dry-down hours later. "
            "Connect the scent to emotions, memories, and personal presence."
        ),
        "things_to_avoid": [
            "Dry chemical or clinical jargon",
            "Generic 'Smells great!' descriptions",
            "Ignoring the scent pyramid evolution"
        ]
    },

    "FMCG / Food": {
        "industry_name": "FMCG / Food",
        "target_audience": "Everyday food lovers, busy families, health-conscious shoppers, and indulgence seekers.",
        "tone": "Appetizing, vibrant, warm, approachable, mouth-watering, and highly relatable.",
        "vocabulary": [
            "burst of flavor", "sustainably sourced ingredients", "golden crispness", "crave-worthy",
            "effortless meal prep", "wholesome goodness", "satisfying crunch", "kitchen staple",
            "family favorite", "rich indulgent taste", "pure perfection", "nourishing energy"
        ],
        "strategic_dimensions": [
            "Taste", "Ingredients", "Convenience", "Family", "Consumption occasions", "Product benefits", "Food appeal"
        ],
        "content_pillars": [
            "Mouth-Watering Flavor & Texture Showcase",
            "Quality Ingredients & Farm Freshness",
            "Quick & Easy Recipe / Serving Hacks",
            "Family Mealtime & Social Moments",
            "Product Benefits & Daily Convenience",
            "Snack Pairing & Indulgence Occasions"
        ],
        "writing_guidelines": (
            "Evoke sensory appetite appeal—focus on textures, aromas, sizzling moments, and effortless enjoyment. "
            "Highlight how the product fits seamlessly into busy modern routines."
        ),
        "things_to_avoid": [
            "Dry corporate product feature dumps",
            "Unappetizing or overly mechanical language",
            "Repetitive 'Eat this now' captions"
        ]
    }
}

def get_industry_strategy(industry_name: str) -> dict:
    """
    Retrieve strategy configuration for a given industry.
    Defaults to Real Estate if unknown.
    """
    return INDUSTRY_STRATEGIES.get(industry_name, INDUSTRY_STRATEGIES["Real Estate"])
