import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import SurfaceError from "./error";
import GlobalError from "./global-error";

afterEach(() => vi.restoreAllMocks());

describe("error-boundary privacy", () => {
  for (const [name, Boundary, code] of [
    ["view", SurfaceError, "SERENE_VIEW_RENDER_FAILED"],
    ["root", GlobalError, "SERENE_ROOT_RENDER_FAILED"],
  ] as const) {
    it(`${name} reports a fixed code without logging private messages, stacks or digests`, async () => {
      const log = vi.spyOn(console, "error").mockImplementation(() => {});
      const privateText = "Synthetic Maya's private pickup narrative and synthetic credential";
      const error = Object.assign(new Error(privateText), { digest: privateText });
      error.stack = privateText;
      const reset = vi.fn();
      const { container } = render(<Boundary error={error} reset={reset} />);
      expect(log).toHaveBeenCalledWith(code);
      expect(JSON.stringify(log.mock.calls)).not.toContain(privateText);
      expect(container).not.toHaveTextContent(privateText);
      await userEvent.setup().click(screen.getByRole("button", { name: "Try again" }));
      expect(reset).toHaveBeenCalledOnce();
    });
  }
});
