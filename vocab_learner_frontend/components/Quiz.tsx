// components/Quiz.tsx
"use client";

import { useState, useEffect } from "react";
import { getQuestion, submitAnswer, ApiError } from "@/lib/api";
import type { Question, AnswerResponse } from "@/lib/types";
import styles from "./Quiz.module.css";

export default function Quiz({
  setId,
  onAnswerSubmitted,
  onBackToHistory,
}: {
  setId: string;
  onAnswerSubmitted: () => void;
  onBackToHistory: () => void;
}) {
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [complete, setComplete] = useState(false);

  async function loadQuestion() {
    setLoading(true);
    setError(null);
    setSelected(null);
    setResult(null);
    setComplete(false);

    try {
      const q = await getQuestion(setId);
      if ("question" in q && q.question === null) {
        // Set has no pending words left -- already mastered, or user
        // selected a completed set to "practice" without re-quizzing yet.
        setComplete(true);
      } else {
        setQuestion(q as Question);
      }
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadQuestion();
  }, [setId]);

  async function handleSubmit() {
    if (!question || !selected) return;

    try {
      const res = await submitAnswer(setId, {
        word: question.word,
        chosen_definition: selected,
      });
      setResult(res);
      onAnswerSubmitted();
    } catch (e) {
      setError((e as ApiError).message);
    }
  }

  function handleContinue() {
    if (result?.set_completed) {
      setComplete(true);
    } else {
      loadQuestion();
    }
  }

  if (error) {
    return (
      <div className={styles.card}>
        <p className={styles.error}>{error}</p>
        <button onClick={loadQuestion} className={styles.retryButton}>
          Retry
        </button>
      </div>
    );
  }

  if (complete) {
    return (
      <div className={styles.card}>
        <p className={styles.setComplete}>🎉 Set complete!</p>
        <button onClick={onBackToHistory} className={styles.continueButton}>
          Back to History
        </button>
      </div>
    );
  }

  if (loading || !question) return <p>Loading...</p>;

  return (
    <div className={styles.card}>
      <div className={styles.word}>{question.word}</div>

      {!result ? (
        <>
          {question.options.map((opt) => (
            <button
              key={opt}
              onClick={() => setSelected(opt)}
              className={`${styles.option} ${
                selected === opt ? styles.optionSelected : ""
              }`}
            >
              {opt}
            </button>
          ))}
          <button
            onClick={handleSubmit}
            disabled={!selected}
            className={styles.submitButton}
          >
            Submit
          </button>
        </>
      ) : (
        <>
          <p
            className={
              result.correct ? styles.feedbackCorrect : styles.feedbackIncorrect
            }
          >
            {result.correct ? "Correct!" : "Incorrect."}
          </p>
          <p className={styles.definition}>
            Correct definition: {result.correct_definition}
          </p>
          {result.set_completed && (
            <p className={styles.setComplete}>🎉 Set complete!</p>
          )}
          <button onClick={handleContinue} className={styles.continueButton}>
            {result.set_completed ? "Back to History" : "Continue"}
          </button>
        </>
      )}
    </div>
  );
}