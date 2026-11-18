import type { Metadata } from "next";
import { Hina_Mincho, Instrument_Sans } from "next/font/google";
import "./globals.css";
import "./site.css";
import OverscrollColour from "./_components/OverscrollColour";
import { share, siteUrl } from "@/share";

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

const title = "Maria Bonete: full-stack developer";
const description =
  "Full-stack developer working remotely from Madrid: web and mobile (React Native and native Android). Case studies, shipped projects, and how I work with coding agents.";

export const metadata: Metadata = {
  metadataBase: siteUrl,
  title: { default: title, template: "%s · Maria Bonete" },
  description,
  ...share({ title, description, path: "/", image: "site" }),
  twitter: { card: "summary_large_image" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${text.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <OverscrollColour />
        {children}
      </body>
    </html>
  );
}
