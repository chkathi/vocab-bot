// components/History.tsx
"use client";

import { useState, useEffect } from "react";
import { listSets, generateSet, ApiError } from "@/lib/api";
import type { WordSet } from "@/lib/types";
import styles from "./History.module.css";

interface HistoryProps {
  onSelectSet: (setId: string) => void;
}

export default function History({ onSelectSet }: HistoryProps) {
  const [sets, setSets] = useState<WordSet[] | null>(null);
  const [openSets, setOpenSets] = useState<Set<string>>(new Set());
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSets();
  }, []);

  function loadSets() {
    setError(null);
    listSets()
      .then(setSets)
      .catch((e: ApiError) => setError(e.message));
  }

  function toggleSet(setId: string) {
    setOpenSets((prev) => {
      const next = new Set(prev);
      if (next.has(setId)) {
        next.delete(setId);
      } else {
        next.add(setId);
      }
      return next;
    });
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      await generateSet();
      loadSets();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setGenerating(false);
    }
  }

  function statusLabel(set: WordSet) {
    if (set.set_complete) {
      return `Mastered ${new Date(set.completed_date!).toLocaleDateString()}`;
    }
    const masteredCount = set.words.filter((w) => w.mastered).length;
    return `In progress — ${masteredCount}/${set.words.length} mastered`;
  }

  if (error) {
    return (
      <div className={styles.wrapper}>
        <p className={styles.empty}>{error}</p>
        <button className={styles.generateButton} onClick={loadSets}>
          Retry
        </button>
      </div>
    );
  }

  if (!sets) return <p className={styles.empty}>Loading...</p>;

  return (
    <div className={styles.wrapper}>
      <button
        className={styles.generateButton}
        onClick={handleGenerate}
        disabled={generating}
      >
        {generating ? "Generating..." : "Generate new set"}
      </button>

      {sets.length === 0 ? (
        <p className={styles.empty}>No sets yet — generate one to start.</p>
      ) : (
        sets.map((set) => {
          const isOpen = openSets.has(set.set_id);

          return (
            <div key={set.set_id} className={styles.setCard}>
              <div className={styles.setHeaderRow}>
                <button
                  className={styles.headerToggle}
                  onClick={() => toggleSet(set.set_id)}
                >
                  <div className={styles.headerText}>
                    <span className={styles.setId}>Set {set.set_id}</span>
                    <span
                      className={
                        set.set_complete
                          ? styles.statusMastered
                          : styles.statusInProgress
                      }
                    >
                      {statusLabel(set)}
                    </span>
                  </div>
                  <span
                    className={`${styles.chevron} ${
                      isOpen ? styles.chevronOpen : ""
                    }`}
                  >
                    ▼
                  </span>
                </button>
                <button
                  className={styles.selectButton}
                  onClick={() => onSelectSet(set.set_id)}
                >
                  Practice
                </button>
              </div>

              {isOpen && (
                <div className={styles.wordGrid}>
                  {set.words.map((w) => (
                    <div key={w.word} className={styles.row}>
                      <span className={styles.word}>{w.word}</span>
                      <span className={styles.definition}>{w.definition}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}