import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please create backend/.env"
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=API_KEY)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Interview Agent",
    description="AI-powered technical interview preparation platform",
    version="2.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5183",
        "http://localhost:5182",
        "http://localhost:5180",
        "http://localhost:5173",
        "http://localhost:5174",

        "https://ai-interview-agent-pi-ten.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class InterviewRequest(BaseModel):
    topic: str
    difficulty: str
    project: str = ""


class AnswerRequest(BaseModel):
    question: str
    answer: str
    topic: str
    difficulty: str


class EvaluationRequest(BaseModel):
    question: str
    answer: str
    topic: str
    difficulty: str
    project: str = ""


# =========================================================
# SESSION MODELS
# =========================================================

class SessionQuestionRequest(BaseModel):
    topic: str
    difficulty: str
    project: str = ""
    question_number: int = 1
    total_questions: int = 5
    previous_questions: list[str] = []


class SessionEvaluationRequest(BaseModel):
    question: str
    answer: str
    topic: str
    difficulty: str
    project: str = ""
    question_number: int = 1


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Interview Agent Backend Running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Interview Agent API",
        "gemini": "configured",
    }


# =========================================================
# GENERATE SINGLE INTERVIEW QUESTION
# =========================================================

@app.post("/api/interview")
def generate_interview_question(
    request: InterviewRequest
):

    prompt = f"""
You are an expert technical interviewer.

Generate ONE technical interview question for a
software engineering candidate.

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Candidate Project:
{
    request.project
    if request.project
    else "No project information provided."
}

Requirements:

1. Ask exactly ONE technical interview question.
2. Make it suitable for a real software engineering interview.
3. If project information is provided, personalize the question.
4. Do not provide the answer.
5. Do not provide hints.
6. Do not add explanations.
7. Return only the interview question.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        question = (response.text or "").strip()

        if not question:
            raise Exception(
                "Gemini returned an empty response."
            )

        return {
            "success": True,
            "question": question,
            "topic": request.topic,
            "difficulty": request.difficulty,
        }

    except Exception as error:

        print(
            "Gemini question generation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(error)}",
        )


# =========================================================
# OLD EVALUATE ANSWER ENDPOINT
# =========================================================

@app.post("/api/evaluate-answer")
def evaluate_answer(
    request: AnswerRequest
):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer to the interview question.

INTERVIEW QUESTION:
{request.question}

CANDIDATE ANSWER:
{request.answer}

TOPIC:
{request.topic}

DIFFICULTY:
{request.difficulty}

Evaluate the answer based on:

- Technical correctness
- Understanding of the concept
- Completeness
- Clarity
- Practical understanding

Return the evaluation in EXACTLY this format:

Score: X/10

Feedback:
Write 2-4 sentences of constructive feedback.

Strengths:

- Strength 1
- Strength 2

Improvements:

- Improvement 1
- Improvement 2

Rules:

1. Give a score between 0 and 10.
2. Be fair and realistic.
3. Do not give the model answer.
4. Do not ask another question.
5. Keep the evaluation concise.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        evaluation = (response.text or "").strip()

        if not evaluation:
            raise Exception(
                "Gemini returned an empty evaluation."
            )

        return {
            "success": True,
            "evaluation": evaluation,
        }

    except Exception as error:

        print(
            "Gemini evaluation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(error)}",
        )


# =========================================================
# EVALUATE SINGLE INTERVIEW ANSWER
# =========================================================

@app.post("/api/evaluate")
def evaluate_interview_answer(
    request: EvaluationRequest
):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Interview Question:
{request.question}

Candidate Answer:
{request.answer}

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Candidate Project:
{
    request.project
    if request.project
    else "No project information provided."
}

Evaluate:

1. Technical correctness
2. Clarity
3. Completeness
4. Relevance

Return ONLY valid JSON:

{{
    "score": 0,
    "feedback": "Detailed feedback",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ]
}}

Score must be between 0 and 10.

Return ONLY JSON.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        result = (response.text or "").strip()

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        evaluation = json.loads(result)

        return {
            "success": True,
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", ""),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", []),
        }

    except Exception as error:

        print(
            "Gemini evaluation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate answer"
        )


# =========================================================
# SESSION QUESTION
# =========================================================

@app.post("/api/session-question")
def generate_session_question(
    request: SessionQuestionRequest
):

    previous_questions_text = "\n".join(
        [
            f"{index + 1}. {question}"
            for index, question
            in enumerate(request.previous_questions)
        ]
    )

    if not previous_questions_text:
        previous_questions_text = "No previous questions."


    prompt = f"""
You are conducting a professional technical interview.

This is question {request.question_number}
out of {request.total_questions}.

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Candidate Project:
{
    request.project
    if request.project
    else "No project information provided."
}

Previous questions:
{previous_questions_text}

Generate ONE new technical interview question.

Rules:

1. Ask exactly ONE question.
2. Do NOT repeat any previous question.
3. Gradually increase conceptual depth.
4. Keep the question appropriate for the selected difficulty.
5. Personalize it using the candidate project when useful.
6. Do not provide the answer.
7. Do not provide hints.
8. Return ONLY the question.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        question = (response.text or "").strip()

        if not question:
            raise Exception(
                "Gemini returned an empty question."
            )

        return {
            "success": True,
            "question": question,
            "question_number": request.question_number,
            "total_questions": request.total_questions,
        }

    except Exception as error:

        print(
            "Session question generation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(error)}",
        )


# =========================================================
# SESSION ANSWER EVALUATION
# =========================================================

@app.post("/api/session-evaluate")
def evaluate_session_answer(
    request: SessionEvaluationRequest
):

    prompt = f"""
You are an expert technical interviewer.

Evaluate this candidate's answer during a
multi-question technical interview.

Question number:
{request.question_number}

Interview Question:
{request.question}

Candidate Answer:
{request.answer}

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Candidate Project:
{
    request.project
    if request.project
    else "No project information provided."
}

Evaluate:

1. Technical correctness
2. Understanding
3. Completeness
4. Clarity
5. Practical application
6. Interview communication quality

Return ONLY valid JSON:

{{
    "score": 0,
    "feedback": "2-4 sentences of constructive feedback",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ]
}}

Rules:

- Score must be between 0 and 10.
- Be fair.
- Do not provide a model answer.
- Return ONLY JSON.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        result = (response.text or "").strip()

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        evaluation = json.loads(result)

        return {
            "success": True,
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", ""),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", []),
        }

    except Exception as error:

        print(
            "Session evaluation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate session answer"
        )


# =========================================================
# FINAL INTERVIEW REPORT
# =========================================================

class FinalReportRequest(BaseModel):
    topic: str
    difficulty: str
    project: str = ""
    evaluations: list[dict] = []


@app.post("/api/session-report")
def generate_session_report(
    request: FinalReportRequest
):

    evaluations_text = json.dumps(
        request.evaluations,
        indent=2
    )

    prompt = f"""
You are a senior technical interviewer.

Generate a final interview performance report.

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Project:
{
    request.project
    if request.project
    else "No project information provided."
}

Question evaluations:
{evaluations_text}

Calculate the overall performance from the
provided scores.

Return ONLY valid JSON:

{{
    "overall_score": 0,
    "performance": "Excellent",
    "summary": "Short overall performance summary",
    "strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],
    "weak_areas": [
        "Weak area 1",
        "Weak area 2"
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        "Recommendation 3"
    ]
}}

Rules:

- overall_score must be between 0 and 10.
- performance should be one of:
  Excellent, Good, Average, Needs Improvement.
- Return ONLY JSON.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        result = (response.text or "").strip()

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        report = json.loads(result)

        return {
            "success": True,
            "overall_score": report.get(
                "overall_score",
                0
            ),
            "performance": report.get(
                "performance",
                "Needs Improvement"
            ),
            "summary": report.get(
                "summary",
                ""
            ),
            "strengths": report.get(
                "strengths",
                []
            ),
            "weak_areas": report.get(
                "weak_areas",
                []
            ),
            "recommendations": report.get(
                "recommendations",
                []
            ),
        }

    except Exception as error:

        print(
            "Final report error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate final interview report"
        )