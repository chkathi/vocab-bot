// lib/api.ts
import type {
  Question,
  WordSet,
  AnswerRequest,
  AnswerResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not set — check .env.local");
}

export type ApiErrorKind = "not_found" | "upstream_failure" | "network" | "unknown";

export class ApiError extends Error {
  kind: ApiErrorKind;

  constructor(message: string, kind: ApiErrorKind) {
    super(message);
    this.kind = kind;
  }
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;

  try {
    res = await fetch(`${API_URL}${path}`, options);
  } catch {
    // fetch() itself threw -- server unreachable, no response at all
    throw new ApiError("Could not reach the server", "network");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const message = body?.error ?? `Request failed (${res.status})`;

    if (res.status === 404) {
      throw new ApiError(message, "not_found");
    }
    if (res.status === 502) {
      throw new ApiError(message, "upstream_failure");
    }
    throw new ApiError(message, "unknown");
  }

  return res.json();
}

export function listSets(): Promise<WordSet[]> {
  return apiFetch("/sets");
}

export function getSet(setId: string): Promise<WordSet> {
  return apiFetch(`/sets/${setId}`);
}

export function generateSet(): Promise<WordSet> {
  return apiFetch("/sets/generate", { method: "POST" });
}

export function getQuestion(setId: string): Promise<Question | { message: string; question: null }> {
  return apiFetch(`/sets/${setId}/question`);
}

export function submitAnswer(
  setId: string,
  payload: AnswerRequest
): Promise<AnswerResponse> {
  return apiFetch(`/sets/${setId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}