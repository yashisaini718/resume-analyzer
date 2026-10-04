from typing import List, Optional
from pydantic import BaseModel, Field


class MissingRequirement(BaseModel):
    requirement: str = Field(
        ...,
        description="The specific qualification, skill, experience, or tool mentioned in the job description that is missing or insufficiently demonstrated in the resume.",
    )
    category: str = Field(
        ...,
        description="Category of the missing requirement (e.g., Technical Skill, Soft Skill, Experience Level, Domain Knowledge, Certification, Tool/Framework).",
    )
    importance: str = Field(
        ...,
        description="Importance level: 'Critical' (hard blocker/must-have), 'High' (significant differentiator), 'Medium' (nice-to-have), or 'Low'.",
    )
    gap_reasoning: str = Field(
        ...,
        description="Explanation of why this is considered a gap based on comparison between the resume/self-description and job requirements.",
    )
    fix_recommendation: str = Field(
        ...,
        description="Actionable advice on how the candidate can address this gap (e.g., specific project, phrasing change, or topic to study).",
    )


class InterviewQuestion(BaseModel):
    question_number: int = Field(
        ...,
        description="Index of the question (1 through 5).",
    )
    question: str = Field(
        ...,
        description="The interview question tailored to the job requirements, user's resume, and identified experience gaps.",
    )
    question_type: str = Field(
        ...,
        description="Type of question: 'Technical Deep-Dive', 'System Design / Architecture', 'Behavioral / Leadership', 'Problem-Solving / Scenario', or 'Resume Gap Defense'.",
    )
    why_asked: str = Field(
        ...,
        description="Why the hiring manager would ask this specific question for this role given the candidate's profile.",
    )
    key_points_to_cover: List[str] = Field(
        ...,
        description="3 to 5 crucial bullet points the candidate should highlight in their answer.",
    )


class RoadmapStep(BaseModel):
    phase_number: int = Field(
        ...,
        description="Sequence number of the preparation phase.",
    )
    phase_name: str = Field(
        ...,
        description="Title of the phase (e.g., 'Foundation & Core Gap Closure', 'Hands-on Projects & Architecture', 'Interview Drills & System Design').",
    )
    timeline: str = Field(
        ...,
        description="Suggested timeframe (e.g., 'Week 1-2', 'Week 3-4', 'Month 1').",
    )
    objectives: List[str] = Field(
        ...,
        description="Primary goals to achieve in this phase.",
    )
    action_items: List[str] = Field(
        ...,
        description="Concrete, actionable steps to execute during this phase.",
    )
    recommended_projects_or_resources: List[str] = Field(
        ...,
        description="Recommended projects to build, courses/docs to review, or mock topics to practice.",
    )


class ResumeAnalysisResult(BaseModel):
    profile_summary: str = Field(
        ...,
        description="High-level synthesis of candidate's current alignment with the target job, taking into account resume and self-description.",
    )
    overall_match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Estimated match percentage score from 0 to 100 based on job requirements.",
    )
    missing_requirements: List[MissingRequirement] = Field(
        ...,
        description="List of all missing or underrepresented skills and requirements from the job description.",
    )
    interview_questions: List[InterviewQuestion] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Exactly 5 curated interview preparation questions addressing technical depth and resume gaps.",
    )
    preparation_roadmap: List[RoadmapStep] = Field(
        ...,
        description="Chronological step-by-step roadmap for preparing to land and succeed in this role.",
    )


class AnalyzeTextInput(BaseModel):
    resume_text: str = Field(
        ...,
        min_length=20,
        description="Raw or extracted resume content.",
    )
    job_description: str = Field(
        ...,
        min_length=20,
        description="Target job description with requirements.",
    )
    self_description: Optional[str] = Field(
        default="",
        description="Additional context about the user's background, current learning, aspirations, or unlisted projects.",
    )


class AnalysisResponseWrapper(BaseModel):
    success: bool = True
    message: str = "Resume analysis generated successfully."
    data: ResumeAnalysisResult
    resume_char_count: Optional[int] = None
