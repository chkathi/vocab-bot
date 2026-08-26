// components/ProgressBar.tsx
"use client";

import { useState, useEffect } from "react";
import { getSet } from "@/lib/api";
import type { WordSet } from "@/lib/types";
import styles from "./ProgressBar.module.css";

export default function ProgressBar({
  setId,
  refreshTrigger,
}: {
  setId: string;
  refreshTrigger: number;
}) {
  const [set, setSet] = useState<WordSet | null>(null);

  useEffect(() => {
    getSet(setId).then(setSet).catch(() => setSet(null));
  }, [setId, refreshTrigger]);

  if (!set) return null;

  const masteredCount = set.words.filter((w) => w.mastered).length;

  return (
    <div className={styles.wrapper}>
      <p className={styles.count}>
        {masteredCount}/{set.words.length} mastered
      </p>
      <div className={styles.chips}>
        {set.words.map((w) => (
          <span
            key={w.word}
            className={`${styles.chip} ${
              w.mastered ? styles.chipMastered : ""
            }`}
          >
            {w.word}
          </span>
        ))}
      </div>
    </div>
  );
}