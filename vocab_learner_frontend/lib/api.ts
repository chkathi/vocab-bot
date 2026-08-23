// lib/api.ts
import type {
  Question,
  CurrentSet,
  AnswerRequest,
  AnswerResponse,
  HistoryResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not set — check .env.local");
}

export async function getQuestion(): Promise<Question> {
  const res = await fetch(`${API_URL}/question`);
  if (!res.ok) throw new Error("Failed to fetch question");
  return res.json();
}

export async function getCurrentSet(): Promise<CurrentSet> {
  const res = await fetch(`${API_URL}/current_set`);
  if (!res.ok) throw new Error("Failed to fetch current set");
  return res.json();
}

export async function submitAnswer(
  payload: AnswerRequest
): Promise<AnswerResponse> {
  const res = await fetch(`${API_URL}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit answer");
  return res.json();
}

export async function getHistory(): Promise<HistoryResponse> {
  const res = await fetch(`${API_URL}/history`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}