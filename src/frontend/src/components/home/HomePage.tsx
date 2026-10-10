"use client";

import { useCallback, useMemo, useState } from "react";
import { buildChapters } from "./chapters";
import { CarScene } from "./CarScene";
import { Hero } from "./Hero";
import { HowItWorks } from "./HowItWorks";
import { Preloader } from "./Preloader";
import { ScenarioStrip } from "./ScenarioStrip";
import { SplitSection } from "./SplitSection";
import { MediaContext } from "./MediaImage";
import { useHomeData } from "./useHomeData";
import type { FrameStatus } from "./useCarFrames";

// Fünf Abschnitte, eine Geschichte: Versprechen → wie es arbeitet (Scroll) → Zahlen und Rollen → Modell wählen → Nachweis.
export function HomePage({ media }: { media: string[] }) {
  const data = useHomeData();
  const chapters = useMemo(() => buildChapters(data), [data]);
  const [frames, setFrames] = useState<{ status: FrameStatus; progress: number }>({ status: "loading", progress: 0 });
  const onFramesStatus = useCallback((status: FrameStatus, progress: number) => setFrames({ status, progress }), []);

  return (
    <MediaContext.Provider value={media}>
    <main>
      <Preloader progress={frames.progress} done={frames.status !== "loading"} />
      <Hero data={data} />
      <CarScene chapters={chapters} onFramesStatus={onFramesStatus} />
      <HowItWorks data={data} />
      <ScenarioStrip data={data} />
      <SplitSection />
    </main>
    </MediaContext.Provider>
  );
}
