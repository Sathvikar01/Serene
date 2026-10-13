"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import type { ReactNode } from "react";
import { MobileMenu } from "./MobileMenu";
import { SurfaceNav } from "./SurfaceNav";
import { Wordmark } from "./Wordmark";
import { LoadingProvider } from "@/components/layout/LoadingProvider";
import styles from "./AppShell.module.css";

// One top bar at every width, as on the reference sheet: the wordmark, then
// the five surfaces in tracked capitals. Below 60rem the links move into a
// menu sheet behind a single button. Exactly one of the two is visible.
//
// On the landing page the bar is held empty: entering Serene flies the
// bloom's flower into the logo's place, then the bar fills in.
export function AppShell({ children, demo = false }: { children: ReactNode; demo?: boolean }) {
  const pathname = usePathname();
  const landing = pathname === "/";

  return (
    <LoadingProvider initialLoading={!landing}>
      <div className={styles.shell}>
        <a href="#content" className={styles.skip}>
          Skip to content
        </a>

        <header className={styles.topbar} data-shell-bar="" data-landing={landing || undefined}>
          <Wordmark />
          <div className={styles.barNav}>
            <SurfaceNav variant="bar" />
          </div>
          {demo ? <Link className={styles.ask} href="/agent" aria-current={pathname === "/agent" ? "page" : undefined}>Ask Serene</Link> : null}
          <div className={styles.menu}>
            <MobileMenu />
          </div>
        </header>

        <main id="content" tabIndex={-1} className={styles.main} data-landing={landing || undefined}>
          {children}
        </main>
      </div>
    </LoadingProvider>
  );
}
