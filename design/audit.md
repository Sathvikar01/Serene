# Layout audit

Goal: reduce unused whitespace while preserving the original warm paper, ruled grid, uppercase typography, navigation and flower logo.

Follow-up: reduce visible text and remove unnecessary containers. Primary headers now use only their title. Today is a compact summary, evidence/workflow and memory history expand on demand, empty side panels are omitted, and the belief map uses the full width until a link is selected. Restore the existing local Ask Serene client and service connection from the user's working copy; keep that copy unchanged.

| Issue | Impact | Fix | Check |
| --- | --- | --- | --- |
| Default h4–h6 margins add unwanted gaps inside cards | High | Reset all heading margins; let component gap tokens control spacing | Browser checks confirm zero heading margins |
| Tall stacked page introductions delay the record | High | Place title and context alongside one another on wide screens; reduce padding | Today header drops from about 215px to 110px at 1440px |
| Narrow evidence columns beside a short rail leave unused space | Medium | Group short summaries above evidence that uses the full investigation width | Inspect populated investigation and Today layouts |
| Large section gaps and insets compound down long pages | Medium | 24px major gaps, 16px working-card padding and page gaps | Inspect all five surfaces at desktop, tablet and phone widths |
| Loader uses separate artwork and disappears without a handoff | High | Use BloomMark over a blurred page, rotate while pending, fly to the measured header mark when ready | Verify endpoint, interruption, reduced motion and restored page scrolling |

Checked: spacing, viewport fit, anchors, keyboard/menu navigation, and loading lifecycle. Full assistive-technology certification is outside this layout audit.
