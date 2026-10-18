import { Page } from "@/components/layout/Page";
import { AgentChat } from "@/components/agent/AgentChat";

// Test builds only. Browser tests replace the service with scripted responses.
export default function AgentFixturePage() {
  return <Page title="Ask Serene" status={null}><AgentChat /></Page>;
}
