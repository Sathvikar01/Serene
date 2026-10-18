import type { Metadata } from "next";
import { LiveInvestigations } from "@/components/investigations/LiveInvestigations";
import { EmptyState } from "@/components/layout/EmptyState";
import { Page } from "@/components/layout/Page";
import { RecordControl } from "@/components/session/RecordControl";
import { DemoInvestigations } from "@/components/demo/DemoInvestigations";

export const metadata: Metadata = { title: "Investigations" };
export const dynamic = "force-dynamic";

// Read from the `investigations` projection over the Realtime projection path
// (#33), for the signed-in parent's chosen child (#87). Signed out,
// unconfigured or with no child, the surface shows the honest unconnected state.
export default function InvestigationsPage() {
  const demo = process.env.SERENE_DEMO_MODE === "1";
  return (
    <Page
      title="Investigations"
      status={demo ? null : <RecordControl next="/investigations" />}
    >
      {demo ? (
        <DemoInvestigations mode="all" />
      ) : (
        <LiveInvestigations
          mode="all"
          unconnected={
            <EmptyState title="No open investigations">
              <p>
                New questions and their evidence will appear here.
              </p>
            </EmptyState>
          }
        />
      )}
    </Page>
  );
}
