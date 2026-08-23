// app/page.tsx
"use client";

import { useState } from "react";
import Quiz from "@/components/Quiz";
import ProgressBar from "@/components/ProgressBar";
import History from "@/components/History";
import styles from "./page.module.css";

export default function Home() {
  const [refreshCount, setRefreshCount] = useState(0);
  const [tab, setTab] = useState<"quiz" | "history">("quiz");

  return (
    <div>
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tab === "quiz" ? styles.tabActive : ""}`}
          onClick={() => setTab("quiz")}
        >
          Quiz
        </button>
        <button
          className={`${styles.tab} ${tab === "history" ? styles.tabActive : ""}`}
          onClick={() => setTab("history")}
        >
          History
        </button>
      </div>

      {tab === "quiz" ? (
        <>
          <ProgressBar refreshTrigger={refreshCount} />
          <Quiz onAnswerSubmitted={() => setRefreshCount((c) => c + 1)} />
        </>
      ) : (
        <History />
      )}
    </div>
  );
}