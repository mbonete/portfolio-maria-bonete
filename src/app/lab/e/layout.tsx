import { Hina_Mincho, Instrument_Sans } from "next/font/google";
import "./e.css";

// Display: Hina Mincho, a slender Mincho, at its one weight. Text: Instrument Sans, variable,
// with a true italic for the quiet secondary lines.
const display = Hina_Mincho({
  variable: "--font-e-display",
  weight: "400",
  subsets: ["latin"],
});

const text = Instrument_Sans({
  variable: "--font-e-text",
  style: ["normal", "italic"],
  subsets: ["latin"],
});

export default function LabELayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${display.variable} ${text.variable} flex-1 flex flex-col w-full`}>
      {children}
    </div>
  );
}
