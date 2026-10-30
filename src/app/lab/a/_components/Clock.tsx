"use client";

import { useSyncExternalStore } from "react";
import { person } from "@/lab/content";

const fmt = new Intl.DateTimeFormat("en-GB", {
  timeZone: person.timezone,
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
  timeZoneName: "short",
});

function subscribe(onChange: () => void) {
  const id = setInterval(onChange, 1000);
  return () => clearInterval(id);
}

const snapshot = () => fmt.format(Date.now());
const serverSnapshot = () => "--:--:--";

export default function Clock({ className }: { className?: string }) {
  const time = useSyncExternalStore(subscribe, snapshot, serverSnapshot);
  return (
    <time className={className} suppressHydrationWarning>
      {time}
    </time>
  );
}
