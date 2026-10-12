"use client";

import { useEffect, useState } from "react";
import { SurfaceLoading } from "@/components/layout/SurfaceLoading";
import { Page } from "@/components/layout/Page";

// Test builds only: inspect the actual transition component without adding
// a slow network request or artificial delay to the product.
export default function LoadingFixturePage() {
  const [pending, setPending] = useState(true);
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);
  return (
    <>
      <Page title="Today" question="What matters now?" lead="The page stays behind the loading logo while its record is being prepared." status={null}>
        <h2>Loading preview</h2>
        <p>When the record is ready, the logo returns to the header and this page becomes available.</p>
      </Page>
      {pending && <SurfaceLoading />}
      {/* Test-only control lets browser tests resolve work without fake waits. */}
      <button className="button" style={{ position: "fixed", right: 16, bottom: 16, zIndex: 101 }}
        disabled={!ready} onClick={() => setPending((value) => !value)}>
        {pending ? "Finish loading preview" : "Load preview again"}
      </button>
    </>
  );
}
