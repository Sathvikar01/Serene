import type { Metadata } from "next";
import { CausalTwinSurface } from "@/components/causal-twin/CausalTwinSurface";
import { LiveCausalTwin } from "@/components/causal-twin/LiveCausalTwin";
import { Page } from "@/components/layout/Page";
import { RecordControl } from "@/components/session/RecordControl";
import demoPayload from "@/fixtures/synthetic-causal-twin.json";
import { twinSourceFrom } from "@/lib/causal-twin/source";

export const metadata: Metadata = { title: "Causal Twin" };
export const dynamic = "force-dynamic";

// The live page reads the selected child's `causal_twin` projection on the
// signed-in family record. Demo mode uses the same surface with fictional data.
export default function CausalTwinPage() {
  const demo = process.env.SERENE_DEMO_MODE === "1";
  return (
    <Page
      title="Causal Twin"
      width="wide"
      status={demo ? null : <RecordControl next="/causal-twin" />}
    >
      {demo ? <CausalTwinSurface source={twinSourceFrom(demoPayload)} /> : <LiveCausalTwin />}
    </Page>
  );
}
