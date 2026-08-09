import { useState } from "react";
import "./App.css";

const API_BASE_URL = "https://ai-interview-agent-5mxs.onrender.com";

function App() {
  const [topic, setTopic] = useState("JavaScript");
  const [difficulty, setDifficulty] = useState("Beginner");
  const [project, setProject] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);

  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState("");

  const generateQuestion = async () => {
    setLoading(true);
    setError("");
    setQuestion("");
    setAnswer("");
    setEvaluation(null);

    try {
      console.log("Calling Render backend...");

      const response = await fetch(
        `${API_BASE_URL}/api/interview`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic,
            difficulty,
            project,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Interview API Error:", errorText);
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      console.log("Question received:", data);

      if (!data.question) {
        throw new Error("Backend did not return a question.");
      }

      setQuestion(data.question);
    } catch (err) {
      console.error("GENERATE QUESTION ERROR:", err);

      setError(
        err.message ||
          "Failed to generate interview question."
      );
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!question) {
      setError(
        "Please generate an interview question first."
      );
      return;
    }

    if (!answer.trim()) {
      setError(
        "Please write your answer before submitting."
      );
      return;
    }

    setEvaluating(true);
    setError("");
    setEvaluation(null);

    try {
      console.log("Sending answer for AI evaluation...");

      const response = await fetch(
        `${API_BASE_URL}/api/evaluate`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question,
            answer,
            topic,
            difficulty,
            project,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Evaluation API Error:", errorText);

        throw new Error(
          `Evaluation failed: ${response.status}`
        );
      }

      const data = await response.json();

      console.log("AI evaluation received:", data);

      setEvaluation(data);
    } catch (err) {
      console.error("SUBMIT ANSWER ERROR:", err);

      setError(
        err.message ||
          "Failed to evaluate your answer."
      );
    } finally {
      setEvaluating(false);
    }
  };

  const startNewQuestion = () => {
    setQuestion("");
    setAnswer("");
    setEvaluation(null);
    setError("");
  };

  return (
    <div className="app">

      <header className="hero">

        <div className="badge">
          AI READY
        </div>

        <h1>
          AI Interview Agent
        </h1>

        <p className="hero-tagline">
          AI-POWERED INTERVIEW PREPARATION
        </p>

        <h2>
          Master Your Technical Interview
        </h2>

        <p className="hero-description">
          Practice personalized technical interview
          questions and receive AI-powered feedback.
        </p>

      </header>

      <main className="container">

        <section className="card">

          <h2>
            Start Interview Practice
          </h2>

          <p>
            Configure your interview and generate an
            AI-powered technical question.
          </p>

          <div className="form-group">

            <label>
              Interview Topic
            </label>

            <input
              type="text"
              value={topic}
              onChange={(event) =>
                setTopic(event.target.value)
              }
              placeholder="Example: JavaScript"
            />

          </div>

          <div className="form-group">

            <label>
              Difficulty
            </label>

            <select
              value={difficulty}
              onChange={(event) =>
                setDifficulty(event.target.value)
              }
            >
              <option value="Beginner">
                Beginner
              </option>

              <option value="Intermediate">
                Intermediate
              </option>

              <option value="Advanced">
                Advanced
              </option>

              <option value="Expert">
                Expert
              </option>
            </select>

          </div>

          <div className="form-group">

            <label>
              Project Information
            </label>

            <textarea
              value={project}
              onChange={(event) =>
                setProject(event.target.value)
              }
              placeholder="Example: AI Interview Agent built using React, FastAPI and Gemini"
              rows="4"
            />

          </div>

          <button
            className="primary-button"
            onClick={generateQuestion}
            disabled={loading}
          >
            {loading
              ? "Generating Question..."
              : "Generate Interview Question"}
          </button>

        </section>

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {question && (
          <section className="card question-card">

            <div className="section-label">
              AI INTERVIEW QUESTION
            </div>

            <h2 className="question">
              {question}
            </h2>

            <div className="question-meta">

              <span>
                {topic}
              </span>

              <span>
                {difficulty}
              </span>

            </div>

          </section>
        )}

        {question && (
          <section className="card">

            <h2>
              Your Answer
            </h2>

            <p>
              Explain your answer as you would during
              a real technical interview.
            </p>

            <textarea
              className="answer-box"
              value={answer}
              onChange={(event) =>
                setAnswer(event.target.value)
              }
              placeholder="Write your technical answer here..."
              rows="10"
            />

            <button
              className="primary-button"
              onClick={submitAnswer}
              disabled={
                evaluating || !answer.trim()
              }
            >
              {evaluating
                ? "AI Evaluating..."
                : "Submit Answer"}
            </button>

          </section>
        )}

        {evaluation && (
          <section className="card evaluation-card">

            <div className="section-label">
              AI EVALUATION
            </div>

            {evaluation.score !== undefined && (
              <div className="score">
                Score: {evaluation.score}/10
              </div>
            )}

            {evaluation.feedback && (
              <div className="evaluation-section">

                <h3>
                  Feedback
                </h3>

                <p>
                  {evaluation.feedback}
                </p>

              </div>
            )}

            {Array.isArray(evaluation.strengths) &&
              evaluation.strengths.length > 0 && (
                <div className="evaluation-section">

                  <h3>
                    Strengths
                  </h3>

                  <ul>
                    {evaluation.strengths.map(
                      (strength, index) => (
                        <li key={index}>
                          {strength}
                        </li>
                      )
                    )}
                  </ul>

                </div>
              )}

            {Array.isArray(evaluation.improvements) &&
              evaluation.improvements.length > 0 && (
                <div className="evaluation-section">

                  <h3>
                    Improvements
                  </h3>

                  <ul>
                    {evaluation.improvements.map(
                      (improvement, index) => (
                        <li key={index}>
                          {improvement}
                        </li>
                      )
                    )}
                  </ul>

                </div>
              )}

            <button
              className="secondary-button"
              onClick={startNewQuestion}
            >
              Start New Question
            </button>

          </section>
        )}

      </main>

      <footer>
        <p>
          AI Interview Agent • React + FastAPI + Gemini
        </p>
      </footer>

    </div>
  );
}

export default App;