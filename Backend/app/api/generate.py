from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from typing import List, Optional
from app.models.content import GenerateContentRequest, GeneratedContentResponse
from app.services.ai_service import generate_content
from app.file_processing.extractor import extract_reference_context

router = APIRouter()

@router.post(
    "/generate-content",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Social Media Content Plan"
)
async def generate_social_content(
    request: Request,
    industry: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    post_count: Optional[int] = Form(None),
    platform: Optional[str] = Form("Instagram"),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate an industry-specific social media content calendar using AI.
    Accepts both multipart/form-data (with optional uploaded reference files) 
    and application/json requests.
    """
    try:
        req_industry = industry
        req_duration = duration
        req_post_count = post_count
        req_platform = platform or "Instagram"
        ref_context = ""

        content_type = request.headers.get("content-type", "")
        
        # Handle application/json request body if Form parameters are not provided
        if "application/json" in content_type:
            body_data = await request.json()
            req_industry = body_data.get("industry")
            req_duration = body_data.get("duration")
            req_post_count = body_data.get("post_count")
            req_platform = body_data.get("platform", "Instagram")
            ref_context = body_data.get("reference_context", "")

        # Extract reference context if files are uploaded via multipart/form-data
        if files:
            # Filter out any empty/unnamed file inputs
            valid_files = [f for f in files if f and f.filename]
            if valid_files:
                extracted_context = await extract_reference_context(valid_files)
                if extracted_context:
                    ref_context = (ref_context + "\n\n" + extracted_context).strip() if ref_context else extracted_context

        if not req_industry or not req_duration or req_post_count is None:
            raise ValueError("Missing required fields: industry, duration, and post_count are required.")

        # Construct and validate Pydantic request model
        gen_request = GenerateContentRequest(
            industry=req_industry,
            duration=req_duration,
            post_count=req_post_count,
            platform=req_platform,
            reference_context=ref_context
        )

        content_plan = generate_content(gen_request)
        return content_plan

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(re)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during content generation: {str(e)}"
        )
