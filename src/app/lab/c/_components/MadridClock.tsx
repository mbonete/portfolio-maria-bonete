"use client";

import { useSyncExternalStore } from "react";
import { person } from "@/lab/content";

const fmt = new Intl.DateTimeFormat("en-GB", {
  timeZone: person.timezone,
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

function subscribe(onChange: () => void) {
  const id = setInterval(onChange, 15_000);
  return () => clearInterval(id);
}

export default function MadridClock() {
  const time = useSyncExternalStore(
    subscribe,
    () => fmt.format(new Date()),
    () => "--:--",
  );
  return <time className="tabular-nums">{time}</time>;
}
