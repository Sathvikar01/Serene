import { useId, type ReactNode } from "react";
import { investigationAnchor, InvestigationDetail } from "@/components/investigations/InvestigationDetail";
import { EmptyState } from "@/components/layout/EmptyState";
import { Icon } from "@/components/system/Icon";
import { Onward, Time } from "@/components/system/Record";
import { SafetyBadge } from "@/components/system/SafetyBadge";
import { LEARNING_STATUS_LABELS } from "@/lib/causal-twin/provenance";
import { variableLabel } from "@/lib/causal-twin/categories";
import type { Investigation } from "@/lib/investigations/model";
import { PHASE_LABELS } from "@/lib/investigations/present";
import type { Projections } from "@/lib/projections/sync";
import { awaitingDecision, childStateFrom, learningsFrom } from "@/lib/today/model";
import styles from "./Today.module.css";

type TodayBriefProps = {
  /** The investigation the parent most needs to see (the kernel's newest still under way). */
  current: Investigation | null;
  investigations: readonly Investigation[];
  projections: Projections;
  status: ReactNode;
};


// Today: what matters now. One thing leads, the current investigation and
// what Serene will do next; what needs the parent, what Serene holds and
// what it has learned recede beside it. Everything is read from the chosen
// child's live projections (#33); a piece that does not pass its checks is
// left out, never filled in.
export function TodayBrief({ current, investigations, projections, status }: TodayBriefProps) {
  const others = investigations.filter((i) => i !== current);
  const awaiting = awaitingDecision(projections);
  const childState = childStateFrom(projections);
  const learnings = learningsFrom(projections);
  const asked = current?.next_action.kind === "WAIT_FOR_PARENT_ANSWER" ? current : null;
  const needs = (asked ? 1 : 0) + (awaiting?.length ?? 0);
  const experimentsUnavailable = awaiting === null && !!projections.experiments;

  return (
    <div className={styles.today} data-investigations>
      {status}
      <div className={styles.layout}>
        <div className={styles.attention}>
          {needs === 0 && !experimentsUnavailable ? <p className={styles.quiet}>Nothing needs your attention.</p> : (
          <Side title="Needs you" icon="hand" emphasis={needs > 0}>
            {needs > 0 ? (
            <ul className={styles.needs}>
              {asked?.next_action.question ? (
                <li className={styles.need}>
                  <span className={styles.needKind}>
                    <Icon name="ask" /> A question for you
                  </span>
                  <Onward href={`#${investigationAnchor(asked.investigation_id)}`}>View question</Onward>
                </li>
              ) : null}
              {awaiting?.map((e) => (
                <li key={e.experiment_id} className={styles.need}>
                  <span className={styles.needKind}>
                    <SafetyBadge safety={e.safety_class} size="sm" />
                  </span>
                  <span className={styles.needText}>{e.intervention.description}</span>
                  <Onward href={`/experiments#experiment-${e.experiment_id}`}>Decide in Experiments</Onward>
                </li>
              ))}
            </ul>
            ) : null}
            {experimentsUnavailable ? (
              <p className={styles.quiet}>Experiments could not be read here. Open Experiments to see them.</p>
            ) : null}
          </Side>)}
        </div>
        <div className={styles.focus}>
          {current ? (
            <InvestigationDetail investigation={current} headingLevel="h2" variant="brief" />
          ) : (
            <EmptyState title="No open investigations">
              <p>Nothing is being looked into. An investigation opens when a concern has more than one plausible explanation.</p>
            </EmptyState>
          )}
          {investigations.length > 1 && current ? (
            <p>
              <Onward href={`/investigations#${investigationAnchor(current.investigation_id)}`}>
                See all {investigations.length} investigations
              </Onward>
            </p>
          ) : null}
        </div>

        <div className={styles.side}>
          {childState ? (
            <Side title="Memory" icon="memory">
              <p className={styles.evidenceLine}>
                {childState.evidence.VERIFIED} verified{childState.evidence.UNVERIFIED > 0 ? ` · ${childState.evidence.UNVERIFIED} unchecked` : ""}{childState.evidence.REJECTED > 0 ? ` · ${childState.evidence.REJECTED} rejected` : ""}
              </p>
              <Onward href="/memory" ariaLabel="View memory">View</Onward>
            </Side>
          ) : null}

          {learnings && learnings.length > 0 ? (
            <Side title="Learned in context" icon="leaf">
              {learnings.length === 0 ? (
                <p className={styles.quiet}>
                  Nothing learned yet. A learning is kept only after an experiment you approved supports it, and only
                  for the situations it was tested in.
                </p>
              ) : (
                <ul className={styles.learnings}>
                  {learnings.map((l) => (
                    <li key={l.learning_id} data-learning-status={l.status}>
                      <span className={styles.learningContexts}>{l.contexts.map(variableLabel).join(", ")}</span>
                      <span className={styles.quiet}>
                        {LEARNING_STATUS_LABELS[l.status]} · review after <Time iso={l.review_after} />
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              <Onward href="/memory">How memory is kept</Onward>
            </Side>
          ) : null}

          {others.length > 0 ? (
            <Side title="Other questions" icon="branch">
              <ul className={styles.others}>
                {others.map((inv) => (
                  <li key={inv.investigation_id}>
                    <a href={`/investigations#${investigationAnchor(inv.investigation_id)}`} className={styles.other}>
                      <span className={styles.otherPhase}>{PHASE_LABELS[inv.phase]}</span>
                      <span className={styles.otherQuestion}>{inv.question}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </Side>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Side({
  title,
  icon,
  emphasis = false,
  children,
}: {
  title: string;
  icon: "hand" | "memory" | "leaf" | "branch";
  emphasis?: boolean;
  children: ReactNode;
}) {
  const id = useId();
  return (
    <section className={styles.panel} aria-labelledby={id} data-emphasis={emphasis || undefined}>
      <h2 id={id} className={styles.panelTitle}>
        <Icon name={icon} />
        {title}
      </h2>
      {children}
    </section>
  );
}
