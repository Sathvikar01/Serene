import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { TodayBrief } from "./TodayBrief";

it("keeps unreadable experiment decisions visible instead of claiming nothing needs attention", () => {
  render(<TodayBrief current={null} investigations={[]} status={null} projections={{
    experiments: {
      child_id: `chd_${"1".repeat(32)}`,
      projection: "experiments",
      state: { version: "invalid" },
      last_sequence: 1,
      last_event_hash: "a".repeat(64),
    },
  }} />);
  expect(screen.getByText("Experiments could not be read here. Open Experiments to see them.")).toBeVisible();
  expect(screen.queryByText("Nothing needs your attention.")).not.toBeInTheDocument();
});

it("keeps the compact empty state for a valid empty experiments projection", () => {
  render(<TodayBrief current={null} investigations={[]} status={null} projections={{
    experiments: {
      child_id: `chd_${"1".repeat(32)}`,
      projection: "experiments",
      state: {},
      last_sequence: 0,
      last_event_hash: "0".repeat(64),
    },
  }} />);
  expect(screen.getByText("Nothing needs your attention.")).toBeVisible();
  expect(screen.queryByText(/Experiments could not be read/)).not.toBeInTheDocument();
});
