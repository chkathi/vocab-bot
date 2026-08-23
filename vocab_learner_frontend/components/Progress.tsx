// components/ProgressBar.tsx
"use client";

import { useState, useEffect } from "react";
import { getCurrentSet } from "@/lib/api";
import type { CurrentSet } from "@/lib/types";

export default function ProgressBar({ refreshTrigger }: { refreshTrigger: number }) {
  const [set, setSet] = useState<CurrentSet | null>(null);

  useEffect(() => {
    getCurrentSet().then(setSet);
  }, [refreshTrigger]);

  if (!set) return null;

  const masteredCount = set.words.filter((w) => w.mastered).length;

  return (
    <div>
      <p>{masteredCount}/{set.words.length} mastered</p>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {set.words.map((w) => (
          <span key={w.word} style={{ opacity: w.mastered ? 1 : 0.5 }}>
            {w.word}
          </span>
        ))}
      </div>
    </div>
  );
}