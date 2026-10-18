import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Page } from "@/components/layout/Page";
import { mayaDemoEnabled } from "@/lib/demo/server";
import { MayaDemoView } from "./MayaDemoView";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Maya’s pickup story", robots: { index: false, follow: false } };

export default function MayaDemoPage() {
  if (!mayaDemoEnabled()) notFound();
  return <Page
    title="Maya’s pickup story"
    question="Why might daycare pickup be hard for Maya?"
    lead="Follow Maya’s fictional pickup story through its recorded reports, trial and reviewed memory."
    width="wide"
    status={null}
  >
    <MayaDemoView />
  </Page>;
}
