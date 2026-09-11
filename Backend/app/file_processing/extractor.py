import io
import os
import base64
from typing import List, Tuple
from fastapi import UploadFile
import pypdf
import docx
import pptx
import openpyxl
from PIL import Image

from app.file_processing.validators import validate_uploaded_file, MAX_FILE_SIZE_BYTES

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf"""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    extracted = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            extracted.append(f"--- Page {idx + 1} ---\n{text.strip()}")
    return "\n".join(extracted) if extracted else "No readable text found in PDF."

def extract_text_from_docx(file_bytes: bytes, filename: str) -> str:
    """Extract text and tables from DOC/DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table text
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    table_text.append(" | ".join(row_cells))
        
        full_text = []
        if paragraphs:
            full_text.append("\n".join(paragraphs))
        if table_text:
            full_text.append("\n--- Tables ---\n" + "\n".join(table_text))
            
        return "\n".join(full_text) if full_text else "No text content found in DOCX document."
    except Exception as e:
        # Fallback for binary legacy .doc or unparseable files
        try:
            raw_text = file_bytes.decode('utf-8', errors='ignore')
            cleaned = "".join([c for c in raw_text if c.isprintable() or c in "\n\r\t"]).strip()
            return cleaned[:2000] if cleaned else f"Could not parse binary DOC file: {str(e)}"
        except Exception:
            return f"Error extracting DOC text: {str(e)}"

def extract_text_from_pptx(file_bytes: bytes) -> str:
    """Extract text from PPT/PPTX slides"""
    prs = pptx.Presentation(io.BytesIO(file_bytes))
    slide_texts = []
    for idx, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text and shape.text.strip():
                texts.append(shape.text.strip())
        if texts:
            slide_texts.append(f"--- Slide {idx + 1} ---\n" + "\n".join(texts))
    return "\n\n".join(slide_texts) if slide_texts else "No text found in presentation slides."

def extract_text_from_xlsx(file_bytes: bytes) -> str:
    """Extract spreadsheet text from XLS/XLSX worksheets"""
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    sheet_texts = []
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        rows_str = []
        for row in sheet.iter_rows(values_only=True):
            cells = [str(val).strip() for val in row if val is not None and str(val).strip() != ""]
            if cells:
                rows_str.append(" | ".join(cells))
        if rows_str:
            sheet_texts.append(f"--- Sheet: {sheet_name} ---\n" + "\n".join(rows_str))
    return "\n\n".join(sheet_texts) if sheet_texts else "No data found in spreadsheet."

def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_bytes.decode('utf-8').strip()
    except UnicodeDecodeError:
        return file_bytes.decode('latin-1', errors='ignore').strip()

def process_image_file(file_bytes: bytes, filename: str) -> str:
    """
    Process image file (JPG, JPEG, PNG).
    Returns a structured text descriptor + base64 encoding if needed.
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        b64 = base64.b64encode(file_bytes).decode('utf-8')
        mime = f"image/{img.format.lower() if img.format else 'jpeg'}"
        return (
            f"[Image Reference: {filename} ({width}x{height} px, format {img.format})]\n"
            f"Attached Image Data URI: data:{mime};base64,{b64[:100]}... (base64 image payload ready for vision AI processing)"
        )
    except Exception as e:
        return f"[Image File: {filename}] (Error reading image properties: {str(e)})"

def extract_file_content(file_bytes: bytes, filename: str, ext: str) -> str:
    """Route file bytes to specific extractor based on extension"""
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_bytes, filename)
    elif ext in [".pptx", ".ppt"]:
        return extract_text_from_pptx(file_bytes)
    elif ext in [".xlsx", ".xls"]:
        return extract_text_from_xlsx(file_bytes)
    elif ext == ".txt":
        return extract_text_from_txt(file_bytes)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return process_image_file(file_bytes, filename)
    else:
        return f"Unsupported file type '{ext}'"

async def extract_reference_context(files: List[UploadFile]) -> str:
    """
    Process a list of UploadFile objects and combine them into a clean, normalized reference context string.
    """
    if not files:
        return ""

    reference_blocks = []
    
    for file in files:
        if not file or not file.filename:
            continue

        ext = validate_uploaded_file(file)
        content_bytes = await file.read()

        if len(content_bytes) > MAX_FILE_SIZE_BYTES:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds maximum allowed size of 10 MB."
            )

        if not content_bytes or len(content_bytes) == 0:
            reference_blocks.append(f"File: {file.filename}\n[Empty file content]")
            continue

        extracted_text = extract_file_content(content_bytes, file.filename, ext)

        block = f"File: {file.filename}\n{extracted_text.strip()}"
        reference_blocks.append(block)

    if not reference_blocks:
        return ""

    context_header = "REFERENCE MATERIAL (Primary Ground Truth Facts):\n"
    return context_header + "\n\n---\n\n".join(reference_blocks)
