// lib/types.ts

// A single word within the current set (from GET /current_set)
export interface Word {
  word: string;
  definition: string;
  mastered: boolean;
  streak: number;
  times_seen: number;
  user_sentence: string;
}

// GET /current_set response
export interface CurrentSet {
  set_id: string;
  set_complete: boolean;
  completed_date: string | null;
  words: Word[];
}

// GET /question response
export interface Question {
  word: string;
  options: string[];
  correct_answer: string;
}

// POST /answer request body
export interface AnswerRequest {
  word: string;
  chosen_definition: string;
}

// POST /answer response
export interface AnswerResponse {
  correct: boolean;
  correct_definition: string;
  word_mastered: boolean;
  set_completed: boolean;
}

// GET /history — still unconfirmed, see note below
export interface HistoryEntry {
  words: Word[];
  completed_date: string;
}

export interface HistoryResponse {
  message?: string;
  history: HistoryEntry[];
}