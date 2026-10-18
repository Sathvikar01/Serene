import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import Today from "./today/page";
import Investigations from "./investigations/page";
import Experiments from "./experiments/page";
import Memory from "./memory/page";
import CausalTwin from "./causal-twin/page";

afterEach(() => vi.unstubAllEnvs());

it.each([
  ["Today", Today, "[data-investigation-id]"],
  ["Investigations", Investigations, "[data-investigation-id]"],
  ["Experiments", Experiments, "[data-experiment-id]"],
  ["Memory", Memory, "[data-memory-review]"],
  ["Causal Twin", CausalTwin, ".react-flow"],
] as const)("keeps %s populated without repeated demo notices or disconnected record controls", async (title, Surface, selector) => {
  vi.stubEnv("SERENE_DEMO_MODE", "1");
  const { container } = render(<Surface />);
  expect(screen.getByRole("heading", { level: 1, name: title })).toBeVisible();
  await waitFor(() => expect(container.querySelector(selector)).not.toBeNull());
  expect(container.querySelector("[data-demo-notice]")).toBeNull();
  expect(container).not.toHaveTextContent(/Demo mode|fictional sample data|No family record connected/);
  expect(screen.queryByRole("button", { name: /approve/i })).not.toBeInTheDocument();
});
