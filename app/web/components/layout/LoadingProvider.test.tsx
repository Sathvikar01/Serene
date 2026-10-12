import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { LoadingProvider, SurfaceLoading } from "./LoadingProvider";

afterEach(() => vi.restoreAllMocks());

it("waits for all record requests, then releases the overlay for reduced motion", async () => {
  vi.spyOn(window, "matchMedia").mockReturnValue({ matches: true } as MediaQueryList);
  const contents = (first: boolean, second: boolean) => (
    <LoadingProvider>
      <header data-shell-bar><a href="/today"><span data-brand-mark /></a></header>
      <p>Ready content</p>
      {first && <SurfaceLoading label="Loading investigations" />}
      {second && <SurfaceLoading label="Loading memory" />}
    </LoadingProvider>
  );
  const { rerender } = render(contents(true, true));
  await screen.findByRole("status", { name: "Loading memory" });
  rerender(contents(false, true));
  expect(screen.getByRole("status", { name: "Loading memory" })).toBeVisible();
  rerender(contents(false, false));
  await waitFor(() => expect(screen.queryByRole("status")).not.toBeInTheDocument());
  expect(screen.getByText("Ready content")).toBeVisible();
});

it("does not leave a blocking overlay when there is no header destination", async () => {
  const { rerender } = render(<LoadingProvider><SurfaceLoading /></LoadingProvider>);
  await screen.findByRole("status");
  rerender(<LoadingProvider><p>Record unavailable</p></LoadingProvider>);
  await waitFor(() => expect(screen.queryByRole("status")).not.toBeInTheDocument());
  expect(screen.getByText("Record unavailable")).toBeVisible();
});
