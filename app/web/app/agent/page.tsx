import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Page } from "@/components/layout/Page";
import { AgentChat } from "@/components/agent/AgentChat";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Ask Serene", robots: { index: false, follow: false } };

export default function AgentPage() {
  if (process.env.SERENE_DEMO_MODE !== "1") notFound();
  return <Page title="Ask Serene"
    status={null}>
    <AgentChat />
  </Page>;
}
