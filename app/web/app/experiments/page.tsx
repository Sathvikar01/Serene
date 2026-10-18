import type { Metadata } from "next";
import { LiveExperiments } from "@/components/experiments/LiveExperiments";
import { Page } from "@/components/layout/Page";
import { RecordControl } from "@/components/session/RecordControl";
import { ExperimentsView } from "@/components/experiments/ExperimentsView";
import { experimentsSourceFrom } from "@/lib/experiments/source";
import demoPayload from "@/fixtures/synthetic-experiments.json";

export const metadata: Metadata = { title: "Experiments" };
export const dynamic = "force-dynamic";

// The selected child's projection and authenticated transport share the
// existing family session. Only projection updates change displayed stages.

export default function ExperimentsPage() {
  const demo = process.env.SERENE_DEMO_MODE === "1";
  return (
    <Page
      title="Experiments"
      status={demo ? null : <RecordControl next="/experiments" />}
    >
      {demo ? <ExperimentsView source={experimentsSourceFrom(demoPayload)} decide={null} /> : <LiveExperiments />}
    </Page>
  );
}
