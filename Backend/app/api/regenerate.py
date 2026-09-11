from fastapi import APIRouter, HTTPException, status
from app.models.content import RegeneratePostRequest, GeneratedPost
from app.services.ai_service import regenerate_single_post

router = APIRouter()

@router.post(
    "/regenerate-post",
    response_model=GeneratedPost,
    status_code=status.HTTP_200_OK,
    summary="Regenerate a single social media post"
)
def regenerate_post(request: RegeneratePostRequest):
    """
    Regenerate a specific post in the content plan while preserving industry, platform,
    and reference context parameters.
    """
    try:
        updated_post = regenerate_single_post(request)
        return updated_post
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during post regeneration: {str(e)}"
        )
