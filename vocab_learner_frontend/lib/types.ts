// lib/types.ts

export interface Word {
  word: string;
  definition: string;
  mastered: boolean;
  streak: number;
  times_seen: number;
  user_sentence: string;
}

export interface CurrentSet {
  set_id: string;
  set_complete: boolean;
  completed_date: string | null;
  words: Word[];
}

export interface Question {
  word: string;
  options: string[];
  correct_answer: string;
}

export interface AnswerRequest {
  word: string;
  chosen_definition: string;
}

export interface AnswerResponse {
  correct: boolean;
  correct_definition: string;
  word_mastered: boolean;
  set_completed: boolean;
}

export interface HistoryEntry {
  words: Word[];
  completed_date: string;
}

export interface HistoryResponse {
  message?: string;
  history: HistoryEntry[];
}