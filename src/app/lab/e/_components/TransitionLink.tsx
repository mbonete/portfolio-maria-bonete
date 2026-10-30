"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ComponentProps } from "react";

type Doc = Document & { startViewTransition?: (cb: () => Promise<void>) => unknown };

let settle: (() => void) | null = null;

// Wraps client navigation in a same-document View Transition, so an element sharing a
// view-transition-name (the project image) morphs from the list into the case study.
export default function TransitionLink({ href, onClick, ...rest }: ComponentProps<typeof Link> & { href: string }) {
  const router = useRouter();
  const pathname = usePathname();

  // The new route has rendered: let the transition capture it.
  useEffect(() => {
    settle?.();
    settle = null;
  }, [pathname]);

  return (
    <Link
      href={href}
      onClick={(e) => {
        onClick?.(e);
        const doc = document as Doc;
        if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0 || !doc.startViewTransition) return;
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        e.preventDefault();
        doc.startViewTransition(
          () =>
            new Promise<void>((resolve) => {
              settle = resolve;
              router.push(href);
              // Never hold the page hostage if the route doesn't change.
              window.setTimeout(resolve, 1200);
            }),
        );
      }}
      {...rest}
    />
  );
}
