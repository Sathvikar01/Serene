import type { Metadata } from "next";
import { Page } from "@/components/layout/Page";
import { LiveMemory } from "@/components/memory/LiveMemory";
import { RecordControl } from "@/components/session/RecordControl";
import { MemoryView } from "@/components/memory/MemoryView";
import { memorySourceFrom } from "@/lib/memory/source";
import demoPayload from "@/fixtures/synthetic-memory-dream.json";

export const metadata: Metadata = { title: "Memory" };
export const dynamic = "force-dynamic";

export default function MemoryPage() {
  const demo = process.env.SERENE_DEMO_MODE === "1";
  return (
    <Page
      title="Memory"
      status={demo ? null : <RecordControl next="/memory" />}
    >
      {demo ? <MemoryView source={memorySourceFrom(demoPayload)} /> : <LiveMemory />}
    </Page>
  );
}
