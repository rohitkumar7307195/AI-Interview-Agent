import os

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
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5183",
        "http://127.0.0.1:5183",

        "http://localhost:5182",
        "http://127.0.0.1:5182",

        "http://localhost:5180",
        "http://127.0.0.1:5180",

        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "http://localhost:5174",
        "http://127.0.0.1:5174",
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
# GENERATE INTERVIEW QUESTION
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
{request.project if request.project else "No project information provided."}

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
# EVALUATE CANDIDATE ANSWER
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
# EVALUATE INTERVIEW ANSWER
# =========================================================

class EvaluationRequest(BaseModel):
    question: str
    answer: str
    topic: str
    difficulty: str
    project: str = ""


@app.post("/api/evaluate")
def evaluate_answer(request: EvaluationRequest):

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
{request.project if request.project else "No project information provided."}

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

        result = response.text.strip()

        # Remove markdown code fences
        if result.startswith("```json"):
            result = result[7:]

        if result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        import json

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