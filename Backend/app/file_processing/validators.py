import os
from fastapi import UploadFile, HTTPException, status

SUPPORTED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", 
    ".ppt", ".pptx", 
    ".xls", ".xlsx", 
    ".txt", 
    ".jpg", ".jpeg", ".png"
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit per file

def validate_uploaded_file(file: UploadFile) -> str:
    """
    Validate extension, file existence, and file size for an uploaded reference file.
    Returns the lowercased extension if valid, else raises HTTPException (400).
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file missing filename."
        )

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        supported_str = ", ".join(sorted(list(SUPPORTED_EXTENSIONS)))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}' for file '{file.filename}'. Supported formats: {supported_str}"
        )

    # Validate file size if file.size is available or check byte stream length
    if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File '{file.filename}' exceeds maximum allowed size of 10 MB."
        )

    return ext
