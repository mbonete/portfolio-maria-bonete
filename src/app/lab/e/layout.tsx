import { Shippori_Mincho, Zen_Kaku_Gothic_New } from "next/font/google";
import "./e.css";

// Both faces are Japanese, so Google splits them into hundreds of slices and next/font would preload
// every one. Without preload, unicode-range fetches only the slices the page's characters need.
const display = Shippori_Mincho({
  variable: "--font-e-display",
  weight: ["500", "600"],
  subsets: ["latin"],
  preload: false,
});

const text = Zen_Kaku_Gothic_New({
  variable: "--font-e-text",
  weight: ["400", "500", "700"],
  subsets: ["latin"],
  preload: false,
});

export default function LabELayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${display.variable} ${text.variable} flex-1 flex flex-col w-full`}>
      {children}
    </div>
  );
}
