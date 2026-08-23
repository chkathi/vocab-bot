// components/History.tsx
"use client";

import { useState, useEffect } from "react";
import { getHistory } from "@/lib/api";
import type { HistoryResponse } from "@/lib/types";
import styles from "./History.module.css";

export default function History() {
  const [data, setData] = useState<HistoryResponse | null>(null);
  const [openSets, setOpenSets] = useState<Set<string>>(new Set());

  useEffect(() => {
    getHistory().then(setData);
  }, []);

  function toggleSet(key: string) {
    setOpenSets((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  }

  if (!data) return <p className={styles.empty}>Loading...</p>;

  if (!data.history || data.history.length === 0) {
    return (
      <p className={styles.empty}>{data.message || "No sets mastered yet."}</p>
    );
  }

  return (
    <div className={styles.wrapper}>
      {data.history.map((entry, i) => {
        const key = entry.completed_date + i;
        const isOpen = openSets.has(key);

        return (
          <div key={key}>
            <button
              className={styles.dateHeader}
              onClick={() => toggleSet(key)}
            >
              <span className={styles.dateLabel}>
                Set completed{" "}
                {new Date(entry.completed_date).toLocaleDateString()}
              </span>
              <span
                className={`${styles.chevron} ${
                  isOpen ? styles.chevronOpen : ""
                }`}
              >
                ▼
              </span>
            </button>

            {isOpen && (
              <div className={styles.setCard}>
                {entry.words.map((w) => (
                  <div key={w.word} className={styles.row}>
                    <span className={styles.word}>{w.word}</span>
                    <span className={styles.definition}>{w.definition}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}