import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.models.content import GenerateContentRequest, GeneratedContentResponse
from app.core.industry_strategies import get_industry_strategy

# Load environment variables from .env if present
load_dotenv()

def get_ai_client_and_model():
    """
    Initialize OpenAI client based on environment configuration.
    Supports standard OpenAI, custom base URLs, and Gemini OpenAI compatibility endpoint.
    """
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = os.getenv("AI_MODEL_NAME")

    if not api_key:
        raise RuntimeError("AI API key is not configured.")

    if not model_name:
        if base_url and "generativelanguage.googleapis.com" in base_url:
            model_name = "gemini-2.5-flash"
        elif os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            model_name = "gemini-2.5-flash"
        else:
            model_name = "gpt-4o-mini"

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    return client, model_name

def build_system_and_user_prompt(request: GenerateContentRequest, strategy: dict) -> tuple[str, str]:
    """
    Construct dynamic prompt enforcing industry strategy, content pillars, platform rules,
    anti-hallucination constraints, and reference material context.
    """
    system_prompt = (
        f"You are a world-class social media content strategist specializing in the {strategy['industry_name']} industry.\n"
        f"Your mission is to generate a highly tailored, industry-specific social media content calendar.\n"
        f"You MUST NOT sound like a generic motivational post generator or produce repetitive sales fluff.\n"
        f"STRICT FACTUAL ACCURACY RULE:\n"
        f"- Use the reference material as the primary source for brand/product-specific facts.\n"
        f"- If a specific fact is not present in the reference material, do not invent it.\n"
        f"- Do not invent pricing, locations, ingredients, product specifications, awards, certifications, fragrance notes, medical claims, or other factual claims.\n"
        f"- General creative wording is allowed, but factual claims MUST be supported by the reference material when provided."
    )

    platform_rules = {
        "Instagram": (
            "- Highly visual, punchy hooks, engaging tone, and crisp storytelling.\n"
            "- Include 3-5 relevant, targeted hashtags per post.\n"
            "- Visual direction should detail camera angles, lighting, color palette, and subjects."
        ),
        "LinkedIn": (
            "- Professional, insightful, industry-oriented, and authoritative.\n"
            "- Focus on expertise, market trends, craftsmanship, and value propositions.\n"
            "- Include 2-3 professional hashtags per post."
        ),
        "Facebook": (
            "- Accessible, warm, community-friendly, and conversational.\n"
            "- Encourage comments, shares, and family/lifestyle connection.\n"
            "- Include 2-3 broad hashtags per post."
        )
    }

    selected_platform_rule = platform_rules.get(request.platform, platform_rules["Instagram"])

    user_prompt = f"""
INDUSTRY STRATEGY FRAMEWORK:
- Industry: {strategy['industry_name']}
- Target Audience: {strategy['target_audience']}
- Brand Tone: {strategy['tone']}
- Industry Vocabulary & Concepts: {', '.join(strategy['vocabulary'])}
- Required Strategic Dimensions: {', '.join(strategy['strategic_dimensions'])}
- Content Pillars Available: {', '.join(strategy['content_pillars'])}
- Writing Guidelines: {strategy['writing_guidelines']}
- Things to Avoid: {', '.join(strategy['things_to_avoid'])}

PLATFORM REQUIREMENTS ({request.platform}):
{selected_platform_rule}

REFERENCE MATERIAL (PRIMARY SOURCE OF TRUTH):
{request.reference_context if request.reference_context else "No reference file uploaded. Use industry best practices while avoiding ungrounded specific corporate claims."}

ANTI-HALLUCINATION & FACTUAL GROUNDING RULES:
1. Use the reference material above as the primary source for brand/product-specific facts (brand name, product names, location, USPs, ingredients, notes, features).
2. If a specific fact (e.g. price, specific location, certifications) is NOT present in the reference material, DO NOT invent it.
3. Do not invent pricing, locations, ingredients, product specifications, awards, certifications, fragrance notes, medical claims, or other factual claims.
4. General creative wording is allowed, but all brand and product facts MUST match the reference material.

CONTENT PLAN CONSTRAINTS:
- Timeframe: {request.duration}
- EXACT Total Posts Required: {request.post_count}

ANTI-GENERIC QUALITY RULES:
1. Every post MUST belong to a distinct content pillar from the available list above.
2. DO NOT use generic phrases like "Elevate your...", "Unleash your...", or "Dream home waiting for you".
3. Write authentic, industry-informed captions using the vocabulary provided and brand facts from the reference material.
4. Ensure posts vary across educational, emotional, lifestyle, showcase, and strategic angles—DO NOT make every post a hard sell.
5. Visual directions must be vivid and specific to the {strategy['industry_name']} sector.

REQUIRED STRUCTURED JSON OUTPUT SCHEME:
Return ONLY a raw valid JSON object (no markdown, no code block wrappers) matching this schema:

{{
  "industry": "{strategy['industry_name']}",
  "duration": "{request.duration}",
  "platform": "{request.platform}",
  "total_posts": {request.post_count},
  "content_strategy": {{
    "target_audience": "{strategy['target_audience']}",
    "tone": "{strategy['tone']}",
    "content_pillars": [3 to 5 chosen pillar names]
  }},
  "posts": [
    // MUST contain exactly {request.post_count} post objects
    {{
      "post_number": 1,
      "day": "Day 1",
      "content_pillar": "Pillar Name from list",
      "caption": "Full post caption with hook, body, and CTA incorporating real brand facts from reference material if present",
      "visual_direction": "Detailed visual creative direction",
      "hashtags": ["#Hashtag1", "#Hashtag2"]
    }}
  ]
}}
"""
    return system_prompt, user_prompt

def generate_mock_content(request: GenerateContentRequest, strategy: dict) -> GeneratedContentResponse:
    posts = []
    pillars = strategy.get("content_pillars", ["Brand Showcase", "Educational & Value", "Lifestyle & Emotional"])
    ref_note = f" (Reference Context: {request.reference_context[:80]})" if request.reference_context else ""
    
    for i in range(1, request.post_count + 1):
        pillar = pillars[(i - 1) % len(pillars)]
        posts.append({
            "post_number": i,
            "day": f"Day {i}",
            "content_pillar": pillar,
            "caption": f"✨ Discover excellence in {strategy['industry_name']}. Post {i} designed for {request.platform}.{ref_note} #Excellence",
            "visual_direction": f"High resolution aesthetic visual direction tailored for {strategy['industry_name']}.",
            "hashtags": [f"#{strategy['industry_name'].replace(' ', '').replace('/', '')}", f"#{request.platform}", "#ContentStrategy"]
        })
    return GeneratedContentResponse(
        industry=strategy["industry_name"],
        duration=request.duration,
        platform=request.platform,
        total_posts=request.post_count,
        content_strategy={
            "target_audience": strategy["target_audience"],
            "tone": strategy["tone"],
            "content_pillars": pillars[:3]
        },
        posts=posts
    )

def generate_mock_single_post(request: "RegeneratePostRequest", strategy: dict) -> "GeneratedPost":
    from app.models.content import GeneratedPost
    return GeneratedPost(
        post_number=request.post_number,
        day=request.day,
        content_pillar=request.content_pillar,
        caption=f"✨ Freshly regenerated caption for {strategy['industry_name']} post on {request.platform} ({request.day})!",
        visual_direction=f"Updated creative visual direction for {strategy['industry_name']} with enhanced lighting and depth.",
        hashtags=[f"#{strategy['industry_name'].replace(' ', '').replace('/', '')}", "#Regenerated", f"#{request.platform}"]
    )

def generate_content(request: GenerateContentRequest) -> GeneratedContentResponse:
    """
    Main service function to generate, validate, and return structured AI content.
    """
    strategy = get_industry_strategy(request.industry)
    use_mock = os.getenv("AI_USE_MOCK", "false").lower() in ("true", "1", "t", "yes")

    if use_mock:
        return generate_mock_content(request, strategy)

    client, model_name = get_ai_client_and_model()
    system_prompt, user_prompt = build_system_and_user_prompt(request, strategy)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if "gpt-" in model_name or "gemini-" in model_name else None,
            temperature=0.7,
            max_tokens=3000
        )
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError("AI generation failed. Please try again.")

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    content = content.strip()

    # Clean potential markdown block formatting if present
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    # Validate with Pydantic
    try:
        validated_response = GeneratedContentResponse.model_validate_json(content)
    except Exception:
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    # Enforce exact post_count matching
    if len(validated_response.posts) != request.post_count:
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    return validated_response

def regenerate_single_post(request: "RegeneratePostRequest") -> "GeneratedPost":
    """
    Generate a fresh replacement for a single specific post in the content calendar.
    """
    from app.models.content import GeneratedPost
    strategy = get_industry_strategy(request.industry)
    use_mock = os.getenv("AI_USE_MOCK", "false").lower() in ("true", "1", "t", "yes")

    if use_mock:
        return generate_mock_single_post(request, strategy)

    client, model_name = get_ai_client_and_model()

    system_prompt = (
        f"You are a expert social media copywriter specializing in the {strategy['industry_name']} industry.\n"
        f"Generate a single fresh, compelling social media post for {request.platform}.\n"
        f"STRICT FACTUAL ACCURACY: Use reference material as primary source of brand facts when present."
    )

    user_prompt = f"""
REGENERATE SINGLE POST PARAMETERS:
- Industry: {strategy['industry_name']}
- Platform: {request.platform}
- Post Number: {request.post_number}
- Day: {request.day}
- Content Pillar: {request.content_pillar}
- Brand Tone: {strategy['tone']}
- Vocabulary: {', '.join(strategy['vocabulary'])}

REFERENCE MATERIAL:
{request.reference_context if request.reference_context else "No reference file uploaded."}

PREVIOUS CAPTION TO REPLACE:
{request.original_caption if request.original_caption else "None"}

INSTRUCTIONS:
Write a completely NEW and creative caption, visual direction, and 3-5 hashtags for this specific post under the '{request.content_pillar}' pillar. Do NOT repeat the previous caption verbatim.

REQUIRED JSON OUTPUT FORMAT:
Return ONLY a raw valid JSON object matching this schema:
{{
  "post_number": {request.post_number},
  "day": "{request.day}",
  "content_pillar": "{request.content_pillar}",
  "caption": "Fresh new caption with hook, body, and CTA",
  "visual_direction": "Detailed visual creative direction",
  "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3"]
}}
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if "gpt-" in model_name or "gemini-" in model_name else None,
            temperature=0.8,
            max_tokens=1000
        )
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError("AI generation failed. Please try again.")

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        validated_post = GeneratedPost.model_validate_json(content)
    except Exception:
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    return validated_post


