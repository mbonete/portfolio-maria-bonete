import { Hina_Mincho, Instrument_Sans } from "next/font/google";
import "./f.css";

// The same pair as the Gold Screen: Hina Mincho for the big names, Instrument Sans for everything else.
const display = Hina_Mincho({
  variable: "--font-f-display",
  weight: "400",
  subsets: ["latin"],
});

const text = Instrument_Sans({
  variable: "--font-f-text",
  subsets: ["latin"],
});

export default function LabFLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${display.variable} ${text.variable} flex-1 flex flex-col w-full`}>
      {children}
    </div>
  );
}
