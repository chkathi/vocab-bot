// components/Quiz.tsx
"use client";

import { useState, useEffect } from "react";
import { getQuestion, submitAnswer } from "@/lib/api";
import type { Question, AnswerResponse } from "@/lib/types";

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
    <div>
      <h2>{question.word}</h2>

      {!result ? (
        <>
          {question.options.map((opt) => (
            <div key={opt} style={{ margin: "8px 0" }}>
              <button
                onClick={() => setSelected(opt)}
                style={{
                  display: "block",
                  fontWeight: selected === opt ? "bold" : "normal",
                }}
              >
                {opt}
              </button>
            </div>
          ))}
          <button onClick={handleSubmit} disabled={!selected}>
            Submit
          </button>
        </>
      ) : (
        <>
          <p>{result.correct ? "Correct!" : "Incorrect."}</p>
          <p>Correct definition: {result.correct_definition}</p>
          {result.set_completed && (
            <p style={{ fontWeight: "bold" }}>
              🎉 Set complete! Starting a new set.
            </p>
          )}
          <button onClick={loadQuestion}>Continue</button>
        </>
      )}
    </div>
  );
}