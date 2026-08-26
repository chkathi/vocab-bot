// lib/types.ts

export interface Word {
  word: string;
  definition: string;
  mastered: boolean;
  streak: number;
  times_seen: number;
  user_sentence: string;
}

export interface WordSet {
  set_id: string;
  words: Word[];
  set_complete: boolean;
  completed_date: string | null;
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