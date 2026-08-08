import { useState } from "react";
import "./App.css";


const API_URL = "http://127.0.0.1:8001";


function App() {

  // =====================================================
  // STATE
  // =====================================================

  const [topic, setTopic] = useState("");

  const [difficulty, setDifficulty] =
    useState("Beginner");

  const [project, setProject] =
    useState("");

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [evaluation, setEvaluation] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [evaluating, setEvaluating] =
    useState(false);

  const [error, setError] =
    useState("");


  // =====================================================
  // GENERATE QUESTION
  // =====================================================

  const generateQuestion = async () => {

    setError("");
    setQuestion("");
    setAnswer("");
    setEvaluation("");

    if (!topic.trim()) {

      setError(
        "Please enter an interview topic."
      );

      return;
    }

    setLoading(true);

    try {

      console.log(
        "Calling interview API..."
      );

      const response = await fetch(
        `${API_URL}/api/interview`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            "Accept":
              "application/json",
          },

          body: JSON.stringify({
            topic: topic.trim(),

            difficulty:
              difficulty,

            project:
              project.trim(),
          }),
        }
      );


      const data =
        await response.json();


      console.log(
        "Interview API response:",
        data
      );


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to generate interview question"
        );
      }


      setQuestion(
        data.question
      );


    } catch (error) {

      console.error(
        "Question API Error:",
        error
      );


      setError(
        error.message ||
        "Failed to connect to backend."
      );


    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // SUBMIT ANSWER
  // =====================================================

  const submitAnswer = async () => {

    setError("");
    setEvaluation("");


    if (!question) {

      setError(
        "Please generate a question first."
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


    try {

      console.log(
        "Submitting candidate answer..."
      );


      const response = await fetch(
        `${API_URL}/api/evaluate-answer`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            "Accept":
              "application/json",
          },

          body: JSON.stringify({
            question:
              question,

            answer:
              answer.trim(),

            topic:
              topic,

            difficulty:
              difficulty,
          }),
        }
      );


      const data =
        await response.json();


      console.log(
        "Evaluation API response:",
        data
      );


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to evaluate answer"
        );
      }


      setEvaluation(
        data.evaluation
      );


    } catch (error) {

      console.error(
        "Evaluation API Error:",
        error
      );


      setError(
        error.message ||
        "Failed to evaluate your answer."
      );


    } finally {

      setEvaluating(false);

    }
  };


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="app">


      {/* =================================================
          NAVBAR
      ================================================= */}

      <header className="navbar">

        <div className="logo">
          AI Interview Agent
        </div>


        <div className="status">

          <span className="status-dot"></span>

          AI Ready

        </div>

      </header>



      {/* =================================================
          MAIN
      ================================================= */}

      <main className="container">


        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero">

          <div className="badge">
            AI-POWERED INTERVIEW PREPARATION
          </div>


          <h1>

            Master Your{" "}

            <span>
              Technical Interview
            </span>

          </h1>


          <p className="subtitle">

            Practice personalized technical
            interview questions and receive
            AI-powered feedback.

          </p>

        </section>



        {/* =================================================
            INTERVIEW CARD
        ================================================= */}

        <section className="interview-card">


          <div className="card-header">

            <h2>
              Start Interview Practice
            </h2>


            <p>
              Configure your interview and
              generate an AI-powered question.
            </p>

          </div>



          {/* =================================================
              TOPIC + DIFFICULTY
          ================================================= */}

          <div className="form-grid">


            {/* TOPIC */}

            <div className="form-group">

              <label>
                Interview Topic
              </label>


              <input
                type="text"
                placeholder="JavaScript, React, Python, DSA..."
                value={topic}
                onChange={(e) =>
                  setTopic(
                    e.target.value
                  )
                }
              />

            </div>



            {/* DIFFICULTY */}

            <div className="form-group">

              <label>
                Difficulty
              </label>


              <select
                value={difficulty}
                onChange={(e) =>
                  setDifficulty(
                    e.target.value
                  )
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

          </div>



          {/* =================================================
              PROJECT
          ================================================= */}

          <div className="form-group">

            <label>
              Project Information
            </label>


            <textarea
              rows="5"
              placeholder="Describe your project and technologies used..."
              value={project}
              onChange={(e) =>
                setProject(
                  e.target.value
                )
              }
            />

          </div>



          {/* =================================================
              GENERATE BUTTON
          ================================================= */}

          <button
            className="generate-btn"
            onClick={
              generateQuestion
            }
            disabled={loading}
          >

            {loading
              ? "Generating Question..."
              : "Generate Interview Question"
            }

          </button>



          {/* =================================================
              QUESTION
          ================================================= */}

          {question && (

            <div className="question-card">


              <div className="question-label">

                AI INTERVIEW QUESTION

              </div>


              <h3>

                {question}

              </h3>


              <div className="question-meta">

                <span>
                  {topic}
                </span>


                <span>
                  {difficulty}
                </span>

              </div>

            </div>

          )}



          {/* =================================================
              ANSWER SECTION
          ================================================= */}

          {question && (

            <div className="answer-section">


              <h2>
                Your Answer
              </h2>


              <p>
                Explain your answer as you would
                during a real technical interview.
              </p>


              <textarea
                className="answer-box"
                rows="8"
                placeholder="Write your answer here..."
                value={answer}
                onChange={(e) =>
                  setAnswer(
                    e.target.value
                  )
                }
              />


              <button
                className="submit-btn"
                onClick={
                  submitAnswer
                }
                disabled={
                  evaluating
                }
              >

                {evaluating
                  ? "Evaluating Answer..."
                  : "Submit Answer"
                }

              </button>

            </div>

          )}



          {/* =================================================
              ERROR
          ================================================= */}

          {error && (

            <div className="error-box">

              <strong>
                Error:
              </strong>{" "}

              {error}

            </div>

          )}



          {/* =================================================
              AI EVALUATION
          ================================================= */}

          {evaluation && (

            <div className="evaluation-card">


              <div className="evaluation-label">

                AI EVALUATION

              </div>


              <pre>
                {evaluation}
              </pre>


            </div>

          )}

        </section>

      </main>

    </div>

  );
}


export default App;