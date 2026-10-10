"use client";

import { useCallback, useMemo, useState } from "react";
import { buildChapters } from "./chapters";
import { CarScene } from "./CarScene";
import { FeatureTiles } from "./FeatureTiles";
import { Hero } from "./Hero";
import { Preloader } from "./Preloader";
import { ScenarioSections } from "./ScenarioSections";
import { SplitSection } from "./SplitSection";
import { MediaContext } from "./MediaImage";
import { useHomeData } from "./useHomeData";
import type { FrameStatus } from "./useCarFrames";

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
      <FeatureTiles />
      <ScenarioSections data={data} />
      <SplitSection />
    </main>
    </MediaContext.Provider>
  );
}
