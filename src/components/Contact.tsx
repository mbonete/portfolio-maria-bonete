import { Code, Briefcase, FileText, ArrowUpRight } from "lucide-react";

type Channel = {
  label: string;
  value: string;
  href: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
};

const channels: Channel[] = [
  {
    label: "GitHub",
    value: "github.com/mbonete",
    href: "https://github.com/mbonete",
    icon: Code,
  },
  {
    label: "LinkedIn",
    value: "maria-bonete",
    href: "https://www.linkedin.com/in/maria-bonete",
    icon: Briefcase,
  },
  {
    label: "CV",
    value: "Download PDF",
    href: "https://www.mariabonete.com/static/cv.pdf",
    icon: FileText,
  },
];

export default function Contact() {
  return (
    <section
      id="contact"
      className="md:py-20 py-16 border-t border-neutral-800"
    >
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />
        Contact
      </h2>
      <p className="text-neutral-400 mb-8">
        Want to get in touch? Reach out through any of the options below. I’d
        love to hear from you.
      </p>
      <div className="grid sm:grid-cols-3 gap-4">
        {channels.map((c) => {
          const Icon = c.icon;
          return (
            <a
              key={c.label}
              href={c.href}
              target="_blank"
              rel="noreferrer"
              className="group relative flex items-center gap-4 rounded-xl border border-neutral-800 bg-background/40 backdrop-blur-sm p-4 hover:border-primary/60 hover:shadow-[0_0_30px_-10px_var(--color-primary)] transition"
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900/60 group-hover:border-primary/60 group-hover:text-primary transition">
                <Icon className="h-5 w-5" strokeWidth={1.75} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs uppercase tracking-widest text-neutral-400">
                  {c.label}
                </div>
                <div className="truncate text-sm text-neutral-200 group-hover:text-primary transition-colors">
                  {c.value}
                </div>
              </div>
              <ArrowUpRight
                className="h-4 w-4 text-neutral-600 group-hover:text-primary group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition"
                strokeWidth={2}
              />
            </a>
          );
        })}
      </div>
    </section>
  );
}
