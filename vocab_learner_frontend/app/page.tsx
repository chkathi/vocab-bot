// app/page.tsx
"use client";

import { useState } from "react";
import Quiz from "@/components/Quiz";
import ProgressBar from "@/components/ProgressBar";
import History from "@/components/History";
import styles from "./page.module.css";

export default function Home() {
  const [refreshCount, setRefreshCount] = useState(0);
  const [tab, setTab] = useState<"history" | "practice">("history");
  const [selectedSetId, setSelectedSetId] = useState<string | null>(null);

  function handleSelectSet(setId: string) {
    setSelectedSetId(setId);
    setTab("practice");
  }

  return (
    <div>
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tab === "history" ? styles.tabActive : ""}`}
          onClick={() => setTab("history")}
        >
          History
        </button>
        <button
          className={`${styles.tab} ${tab === "practice" ? styles.tabActive : ""}`}
          onClick={() => setTab("practice")}
          disabled={!selectedSetId}
        >
          Practice
        </button>
      </div>

      {tab === "practice" && selectedSetId ? (
        <>
          <ProgressBar setId={selectedSetId} refreshTrigger={refreshCount} />
          <Quiz
            setId={selectedSetId}
            onAnswerSubmitted={() => setRefreshCount((c) => c + 1)}
            onBackToHistory={() => setTab("history")}
          />
        </>
      ) : (
        <History onSelectSet={handleSelectSet} />
      )}
    </div>
  );
}