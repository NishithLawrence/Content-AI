import os
import json
import re
import logging
from dotenv import load_dotenv
from openai import OpenAI
from app.models.content import GenerateContentRequest, GeneratedContentResponse
from app.core.industry_strategies import get_industry_strategy

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger(__name__)

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

    # Determine if configuration targets Gemini
    is_gemini = False
    if os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        is_gemini = True
    elif base_url and "generativelanguage.googleapis.com" in base_url:
        is_gemini = True
    elif model_name and "gemini" in model_name.lower():
        is_gemini = True

    if is_gemini and not base_url:
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

    if not model_name:
        if is_gemini:
            model_name = "gemini-2.5-flash"
        else:
            model_name = "gpt-4o-mini"

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    return client, model_name

def strip_json_comments_and_sanitize(text: str) -> str:
    """
    State-machine based comment stripper & JSON control character sanitizer that:
    - Strips single-line comments // ...
    - Strips block comments /* ... */
    - Cleans trailing commas before } or ]
    - Escapes literal unescaped control characters (< 0x20) inside double-quoted JSON strings:
      * Converts literal \n (0x0A) to \\n
      * Converts literal \r (0x0D) to \\r
      * Converts literal \t (0x09) to \\t
    - CRITICAL: Ignores //, /*, and control characters inside already-escaped sequences or URLs,
      preventing double-escaping of existing \\n, \\r, \\", \\\\, etc.
    """
    result = []
    i = 0
    length = len(text)
    in_string = False
    escape = False

    while i < length:
        char = text[i]

        if in_string:
            if escape:
                result.append(char)
                escape = False
                i += 1
                continue
            elif char == '\\':
                result.append(char)
                escape = True
                i += 1
                continue
            elif char == '"':
                in_string = False
                result.append(char)
                i += 1
                continue
            elif char == '\n':
                result.append('\\n')
                i += 1
                continue
            elif char == '\r':
                result.append('\\r')
                i += 1
                continue
            elif char == '\t':
                result.append('\\t')
                i += 1
                continue
            elif ord(char) < 32:
                result.append(f'\\u{ord(char):04x}')
                i += 1
                continue
            else:
                result.append(char)
                i += 1
                continue

        if char == '"':
            in_string = True
            result.append(char)
            i += 1
            continue

        if char == '/' and i + 1 < length and text[i + 1] == '/':
            i += 2
            while i < length and text[i] not in ('\r', '\n'):
                i += 1
            continue

        if char == '/' and i + 1 < length and text[i + 1] == '*':
            i += 2
            while i + 1 < length and not (text[i] == '*' and text[i + 1] == '/'):
                i += 1
            i += 2
            continue

        result.append(char)
        i += 1

    cleaned_text = "".join(result)
    cleaned_text = re.sub(r',\s*([\}\]])', r'\1', cleaned_text)
    return cleaned_text

def extract_json_payload(raw_text: str) -> dict:
    """
    Safely extract and parse JSON payload from raw LLM output.
    Handles raw JSON, markdown code blocks (```json ... ```), leading/trailing text,
    JS comments, trailing commas, and missing outer structure.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response from AI")

    text = raw_text.strip()

    # 1. Try extracting from markdown code blocks first
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()
    else:
        # 2. Fallback: find outer-most JSON object boundaries { ... }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1].strip()

    # 3. Clean JS comments and trailing commas using string-aware state-machine
    text = strip_json_comments_and_sanitize(text)

    # 4. Parse JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"7. Extracted JSON Is Valid: False. Parsing Error: {e}. Raw content snippet: {raw_text[:200]}")
        raise ValueError(f"Invalid JSON format from AI: {e}")

    # 5. Dynamically unwrap outer dictionary if inner dictionary contains "posts"
    if isinstance(data, dict) and "posts" not in data:
        for val in data.values():
            if isinstance(val, dict) and "posts" in val:
                data = val
                break

    return data

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
Return ONLY a raw valid JSON object matching this schema (MUST contain exactly {request.post_count} post objects in the posts array):

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
    Uses client.chat.completions.create with response_format={"type": "json_object"}
    followed by extract_json_payload and Pydantic schema validation.
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
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000
        )
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"AI chat completion API call failed: {e}")
        raise RuntimeError("AI generation failed. Please try again.")

    content = response.choices[0].message.content if (response and response.choices) else None

    if not content or not content.strip():
        logger.error("AI returned empty response content.")
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    try:
        raw_json_dict = extract_json_payload(content)

        if isinstance(raw_json_dict, dict):
            if "total_posts" not in raw_json_dict and "post_count" in raw_json_dict:
                raw_json_dict["total_posts"] = raw_json_dict["post_count"]

            if "posts" in raw_json_dict and isinstance(raw_json_dict["posts"], dict):
                raw_json_dict["posts"] = list(raw_json_dict["posts"].values())

        validated_response = GeneratedContentResponse.model_validate(raw_json_dict)
    except Exception as e:
        logger.error(f"Pydantic Validation Error: {e}")
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    # Post count matching & normalization on validated_response
    posts_list = validated_response.posts
    if len(posts_list) > request.post_count:
        validated_response.posts = posts_list[:request.post_count]
    elif len(posts_list) < request.post_count and len(posts_list) > 0:
        last_post = posts_list[-1]
        for idx in range(len(posts_list) + 1, request.post_count + 1):
            padded = last_post.model_copy()
            padded.post_number = idx
            padded.day = f"Day {idx}"
            validated_response.posts.append(padded)

    validated_response.total_posts = request.post_count
    return validated_response

def regenerate_single_post(request: "RegeneratePostRequest") -> "GeneratedPost":
    """
    Generate a fresh replacement for a single specific post in the content calendar.
    Uses client.chat.completions.create with response_format={"type": "json_object"}.
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
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=1000
        )
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"AI single post completion failed: {e}")
        raise RuntimeError("AI generation failed. Please try again.")

    content = response.choices[0].message.content if (response and response.choices) else None
    if not content or not content.strip():
        logger.error("AI returned empty single post response.")
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    try:
        raw_json_dict = extract_json_payload(content)
        validated_post = GeneratedPost.model_validate(raw_json_dict)
    except Exception as e:
        logger.error(f"Failed to validate single post regeneration: {e}")
        raise RuntimeError("AI returned an invalid content plan. Please try again.")

    return validated_post


