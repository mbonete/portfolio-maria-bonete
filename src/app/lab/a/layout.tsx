import { Martian_Mono, Schibsted_Grotesk } from "next/font/google";
import "./instrument.css";

const sans = Schibsted_Grotesk({
  subsets: ["latin"],
  variable: "--a-sans",
  display: "swap",
});

const mono = Martian_Mono({
  subsets: ["latin"],
  variable: "--a-mono",
  display: "swap",
});

export default function InstrumentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={`${sans.variable} ${mono.variable} instr flex-1`}>
      {children}
    </div>
  );
}
