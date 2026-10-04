import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.src.ai.pipeline import pipeline
from backend.src.schemas.analyzer import (
    AnalysisResponseWrapper,
    AnalyzeTextInput,
    ResumeAnalysisResult,
)
from backend.src.services.resume_parser import parse_and_clean_resume_file

router = APIRouter(prefix="/analyzer", tags=["Resume Analyzer"])
logger = logging.getLogger(__name__)


@router.post(
    "/analyze-file",
    response_model=AnalysisResponseWrapper,
    summary="Analyze uploaded resume file against job requirements and self-description",
    description="Uploads a resume file (PDF, DOCX, TXT), cleans content, and generates missing requirements, 5 interview questions, and a preparation roadmap.",
)
async def analyze_resume_file(
    resume_file: UploadFile = File(..., description="Resume file in PDF, DOCX, or TXT format"),
    job_description: str = Form(..., min_length=20, description="Target job description"),
    self_description: Optional[str] = Form("", description="Candidate self-description, current focus, or context"),
) -> AnalysisResponseWrapper:
    try:
        content_bytes = await resume_file.read()
        if not content_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        filename = resume_file.filename or "resume.pdf"
        result = pipeline.analyze(
            job_description=job_description,
            resume_file_bytes=content_bytes,
            filename=filename,
            self_description=self_description or "",
        )

        return AnalysisResponseWrapper(
            success=True,
            message="Resume analysis generated successfully from uploaded file.",
            data=result,
        )

    except ValueError as e:
        logger.warning(f"Validation error during resume analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during resume analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}",
        )


@router.post(
    "/analyze-text",
    response_model=AnalysisResponseWrapper,
    summary="Analyze raw resume text against job requirements and self-description",
    description="Accepts raw resume text directly along with job description and self-description.",
)
async def analyze_resume_text(
    payload: AnalyzeTextInput,
) -> AnalysisResponseWrapper:
    try:
        result = pipeline.analyze(
            job_description=payload.job_description,
            resume_raw_text=payload.resume_text,
            self_description=payload.self_description or "",
        )

        return AnalysisResponseWrapper(
            success=True,
            message="Resume analysis generated successfully from text.",
            data=result,
            resume_char_count=len(payload.resume_text),
        )

    except ValueError as e:
        logger.warning(f"Validation error during text resume analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during text resume analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}",
        )


@router.post(
    "/parse-file",
    summary="Parse and clean uploaded resume without AI analysis",
    description="Utility endpoint to preview extracted and cleaned text from a resume document.",
)
async def parse_file_only(
    resume_file: UploadFile = File(..., description="Resume file in PDF, DOCX, or TXT format"),
):
    try:
        content_bytes = await resume_file.read()
        filename = resume_file.filename or "resume.pdf"
        cleaned_text = parse_and_clean_resume_file(filename, content_bytes)
        return {
            "success": True,
            "filename": filename,
            "char_count": len(cleaned_text),
            "cleaned_text": cleaned_text,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse resume: {str(e)}",
        )
