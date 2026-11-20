"use client";

import { useEffect, useState } from "react";

// A shell command to paste into a terminal, with a button that copies it. The command stays selectable
// by hand, for browsers that block the clipboard.
export default function CopyCommand({ command, label }: { command: string; label: string }) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");

  useEffect(() => {
    if (state === "idle") return;
    const t = setTimeout(() => setState("idle"), 2400);
    return () => clearTimeout(t);
  }, [state]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setState("copied");
    } catch {
      setState("failed");
    }
  }

  return (
    <div className="lf-command">
      <pre aria-label={label}>
        <code>{command}</code>
      </pre>
      <button type="button" onClick={copy} data-state={state}>
        {state === "copied" ? "Copied" : state === "failed" ? "Couldn't copy: select it instead" : "Copy the command"}
      </button>
      <span className="lf-sr" role="status">
        {state === "copied" ? "Command copied." : state === "failed" ? "Couldn't copy. Select the command and copy it." : ""}
      </span>
    </div>
  );
}
