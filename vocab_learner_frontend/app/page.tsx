// app/page.tsx
"use client";

import { useState } from "react";
import Quiz from "@/components/Quiz";
import ProgressBar from "@/components/Progress";

export default function Home() {
  const [refreshCount, setRefreshCount] = useState(0);

  return (
    <div>
      <ProgressBar refreshTrigger={refreshCount} />
      <Quiz onAnswerSubmitted={() => setRefreshCount((c) => c + 1)} />
    </div>
  );
}