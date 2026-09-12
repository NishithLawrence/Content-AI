from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

class GenerateContentRequest(BaseModel):
    industry: str = Field(..., description="Selected industry (Real Estate, Jewellery, Perfume, FMCG / Food)")
    duration: str = Field(..., description="Content plan duration (1 Week, 2 Weeks, 1 Month)")
    post_count: int = Field(..., description="Number of posts requested (3, 6, 12)")
    platform: str = Field(default="Instagram", description="Target platform (Instagram, LinkedIn, Facebook)")
    reference_context: Optional[str] = Field(default="", description="Optional reference material text context")

    @field_validator('industry')
    def validate_industry(cls, v):
        valid = ["Real Estate", "Jewellery", "Perfume", "FMCG / Food"]
        if v not in valid:
            raise ValueError(f"Industry must be one of {valid}")
        return v

    @field_validator('duration')
    def validate_duration(cls, v):
        valid = ["1 Week", "2 Weeks", "1 Month"]
        if v not in valid:
            raise ValueError(f"Duration must be one of {valid}")
        return v

    @field_validator('post_count')
    def validate_post_count(cls, v):
        if v not in [3, 6, 12]:
            raise ValueError("post_count must be 3, 6, or 12")
        return v

    @model_validator(mode='after')
    def validate_duration_and_count(self):
        duration_map = {
            "1 Week": 3,
            "2 Weeks": 6,
            "1 Month": 12
        }
        expected = duration_map.get(self.duration)
        if expected is not None and self.post_count != expected:
            raise ValueError(f"Duration '{self.duration}' requires post_count to be {expected}, got {self.post_count}")
        return self

    @field_validator('platform')
    def validate_platform(cls, v):
        valid = ["Instagram", "LinkedIn", "Facebook"]
        if v not in valid:
            raise ValueError(f"Platform must be one of {valid}")
        return v

class RegeneratePostRequest(BaseModel):
    industry: str = Field(..., description="Selected industry")
    platform: str = Field(default="Instagram", description="Target platform")
    duration: str = Field(default="1 Week", description="Plan duration")
    post_number: int = Field(..., description="Number of the post to regenerate")
    day: str = Field(..., description="Day string (e.g. Day 1)")
    content_pillar: str = Field(..., description="Content pillar for this post")
    reference_context: Optional[str] = Field(default="", description="Optional reference context")
    original_caption: Optional[str] = Field(default="", description="Original caption to replace")

class ContentStrategy(BaseModel):
    target_audience: str
    tone: str
    content_pillars: List[str]

    @field_validator('content_pillars', mode='before')
    def validate_content_pillars(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(',') if p.strip()]
        return v

class GeneratedPost(BaseModel):
    post_number: int
    day: str
    content_pillar: str
    caption: str
    visual_direction: str
    hashtags: List[str]

    @field_validator('hashtags', mode='before')
    def validate_hashtags(cls, v):
        if isinstance(v, str):
            import re
            tags = re.findall(r'#?\w+', v)
            return [t if t.startswith('#') else f'#{t}' for t in tags]
        elif isinstance(v, list):
            return [str(t) if str(t).startswith('#') else f'#{t}' for t in v]
        return v

class GeneratedContentResponse(BaseModel):
    industry: str
    duration: str
    platform: str
    total_posts: int
    content_strategy: ContentStrategy
    posts: List[GeneratedPost]
