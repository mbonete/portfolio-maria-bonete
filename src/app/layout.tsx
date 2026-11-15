import type { Metadata } from "next";
import { Hina_Mincho, Instrument_Sans } from "next/font/google";
import "./globals.css";
import "./site.css";

// Hina Mincho for the big names, Instrument Sans for everything else.
const display = Hina_Mincho({
  variable: "--font-f-display",
  weight: "400",
  subsets: ["latin"],
});

const text = Instrument_Sans({
  variable: "--font-f-text",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: { default: "Maria Bonete: full-stack developer", template: "%s · Maria Bonete" },
  description:
    "Full-stack developer in Madrid, specialising in AI-driven engineering, web, React Native and Web3. Case studies, shipped projects, and how I work with coding agents.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${text.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
