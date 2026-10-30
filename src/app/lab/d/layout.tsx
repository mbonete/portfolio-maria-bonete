import { Sofia_Sans, Sofia_Sans_Extra_Condensed } from "next/font/google";
import "./d.css";

const display = Sofia_Sans_Extra_Condensed({
  variable: "--font-d-display",
  subsets: ["latin"],
});

const text = Sofia_Sans({
  variable: "--font-d-text",
  subsets: ["latin"],
});

export default function LabDLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${display.variable} ${text.variable} flex-1 flex flex-col w-full`}>
      {children}
    </div>
  );
}
