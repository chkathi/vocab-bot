// components/Quiz.tsx
"use client";

import { useState, useEffect } from "react";
import { getQuestion, submitAnswer } from "@/lib/api";
import type { Question, AnswerResponse } from "@/lib/types";
import styles from "./Quiz.module.css";

export default function Quiz({
  onAnswerSubmitted,
}: {
  onAnswerSubmitted: () => void;
}) {
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResponse | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadQuestion() {
    setLoading(true);
    setSelected(null);
    setResult(null);
    const q = await getQuestion();
    setQuestion(q);
    setLoading(false);
  }

  useEffect(() => {
    loadQuestion();
  }, []);

  async function handleSubmit() {
    if (!question || !selected) return;
    const res = await submitAnswer({
      word: question.word,
      chosen_definition: selected,
    });
    setResult(res);
    onAnswerSubmitted();
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
            <p className={styles.setComplete}>
              🎉 Set complete! Starting a new set.
            </p>
          )}
          <button onClick={loadQuestion} className={styles.continueButton}>
            Continue
          </button>
        </>
      )}
    </div>
  );
}