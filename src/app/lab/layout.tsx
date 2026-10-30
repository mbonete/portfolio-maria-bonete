import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Lab — Maria Bonete",
  robots: { index: false, follow: false },
};

export default function LabLayout({ children }: { children: React.ReactNode }) {
  return <div className="flex-1 flex flex-col w-full">{children}</div>;
}
