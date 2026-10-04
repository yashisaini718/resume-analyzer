import json
import logging
import os
from typing import Optional

from google import genai
from google.genai import types

from backend.src.core.config import settings
from backend.src.schemas.analyzer import ResumeAnalysisResult
from backend.src.services.resume_parser import parse_and_clean_resume_file, clean_resume_text
from backend.src.ai.prompts import SYSTEM_PROMPT, build_analysis_prompt

logger = logging.getLogger(__name__)


class ResumeAnalysisPipeline:
    """
    End-to-end AI Pipeline for Resume Analysis:
    1. Loads and cleans uploaded resume files (PDF, DOCX, TXT) or raw resume text.
    2. Constructs prompt combining resume content, job description, and user self-description.
    3. Executes Gemini LLM call with structured JSON schema.
    4. Validates and returns structured outputs:
       - Missing requirements vs job description
       - 5 tailored interview preparation questions
       - Customized preparation roadmap
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or settings.GEMINI_MODEL or "gemini-3.8-flash"
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in .env or environment variables."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def prepare_resume_content(
        self,
        resume_file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        resume_raw_text: Optional[str] = None,
    ) -> str:
        """
        Extracts and cleans resume content from either uploaded file bytes or direct text.
        """
        if resume_file_bytes and filename:
            cleaned_text = parse_and_clean_resume_file(filename, resume_file_bytes)
        elif resume_raw_text:
            cleaned_text = clean_resume_text(resume_raw_text)
        else:
            raise ValueError("Either resume_file (bytes + filename) or resume_raw_text must be provided.")

        if not cleaned_text or len(cleaned_text.strip()) < 15:
            raise ValueError("Cleaned resume content is empty or contains insufficient text.")

        return cleaned_text

    def analyze(
        self,
        job_description: str,
        resume_file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        resume_raw_text: Optional[str] = None,
        self_description: str = "",
    ) -> ResumeAnalysisResult:
        """
        Executes the AI analysis pipeline.
        """
        if not job_description or len(job_description.strip()) < 20:
            raise ValueError("Job description is required and must be at least 20 characters.")

        # Step 1: Load and clean resume text
        cleaned_resume = self.prepare_resume_content(
            resume_file_bytes=resume_file_bytes,
            filename=filename,
            resume_raw_text=resume_raw_text,
        )

        # Step 2: Build the complete user prompt
        user_prompt = build_analysis_prompt(
            resume_text=cleaned_resume,
            job_description=job_description,
            self_description=self_description,
        )

        # Step 3: Invoke LLM with structured output schema
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=ResumeAnalysisResult,
            temperature=0.2,
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_prompt,
                config=config,
            )
            raw_output = response.text
        except Exception as e:
            logger.error(f"Error during Gemini API generation: {e}")
            raise RuntimeError(f"AI generation failed: {str(e)}") from e

        if not raw_output:
            raise RuntimeError("Model returned an empty response.")

        # Step 4: Parse & validate structured Pydantic response
        try:
            result = ResumeAnalysisResult.model_validate_json(raw_output)
            
            # Ensure interview questions count is strictly 5
            if len(result.interview_questions) > 5:
                result.interview_questions = result.interview_questions[:5]
                for idx, q in enumerate(result.interview_questions, 1):
                    q.question_number = idx

            return result
        except Exception as err:
            logger.error(f"Failed to validate response against ResumeAnalysisResult: {err}. Raw text: {raw_output}")
            # Fallback JSON parsing if needed
            try:
                data = json.loads(raw_output)
                return ResumeAnalysisResult.model_validate(data)
            except Exception as nested_err:
                raise ValueError(f"Model output format validation failed: {str(nested_err)}") from nested_err


pipeline = ResumeAnalysisPipeline()
