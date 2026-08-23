// scripts/auto-answer.mjs
const API_URL = "http://127.0.0.1:5000";

async function getQuestion() {
  const res = await fetch(`${API_URL}/question`);
  if (!res.ok) throw new Error("Failed to fetch question");
  return res.json();
}

async function submitAnswer(word, chosenDefinition) {
  const res = await fetch(`${API_URL}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, chosen_definition: chosenDefinition }),
  });
  if (!res.ok) throw new Error("Failed to submit answer");
  return res.json();
}

async function run() {
  let setCompleted = false;
  let count = 0;

  while (!setCompleted) {
    const question = await getQuestion();
    const result = await submitAnswer(question.word, question.correct_answer);

    count++;
    console.log(
      `${count}. ${question.word} → correct: ${result.correct}, mastered: ${result.word_mastered}`
    );

    if (result.set_completed) {
      setCompleted = true;
      console.log(`\n🎉 Set completed after ${count} answers.`);
    }
  }
}

run().catch((err) => {
  console.error("Auto-answer script failed:", err);
});