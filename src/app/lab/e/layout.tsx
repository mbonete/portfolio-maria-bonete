import { Shippori_Mincho, Zen_Kaku_Gothic_New } from "next/font/google";
import "./e.css";

const display = Shippori_Mincho({
  variable: "--font-e-display",
  weight: ["500", "600"],
  subsets: ["latin"],
});

const text = Zen_Kaku_Gothic_New({
  variable: "--font-e-text",
  weight: ["400", "500", "700"],
  subsets: ["latin"],
});

export default function LabELayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${display.variable} ${text.variable} flex-1 flex flex-col w-full`}>
      {children}
    </div>
  );
}
