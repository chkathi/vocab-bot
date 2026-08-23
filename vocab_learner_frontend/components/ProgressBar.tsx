// components/ProgressBar.tsx
"use client";

import { useState, useEffect } from "react";
import { getCurrentSet } from "@/lib/api";
import type { CurrentSet } from "@/lib/types";
import styles from "./ProgressBar.module.css";

export default function ProgressBar({
  refreshTrigger,
}: {
  refreshTrigger: number;
}) {
  const [set, setSet] = useState<CurrentSet | null>(null);

  useEffect(() => {
    getCurrentSet().then(setSet);
  }, [refreshTrigger]);

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