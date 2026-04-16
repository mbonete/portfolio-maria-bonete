import Image from "next/image";

export default function Hero() {
  return (
    <section className="md:py-20 py-16 flex flex-col md:flex-row items-center">
      <div className="flex-1">
        <p className="text-sm uppercase tracking-widest text-primary mb-4">
          Full-Stack Developer · React Native · Web3
        </p>
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-tight">
          Hi, I&apos;m{" "}
          <span className="bg-linear-to-r whitespace-nowrap from-primary to-secondary bg-clip-text text-transparent">
            Maria Bonete
          </span>
          .
          <br />
          <span className="text-neutral-500">
            I build fast, accessible web and mobile apps.
          </span>
        </h1>
        <div className="mt-8 flex gap-4">
          <a
            href="#projects"
            className="rounded-full bg-primary text-primary-foreground px-5 py-2.5 text-sm font-medium hover:opacity-90 transition shadow-[0_0_40px_-10px_var(--color-primary)]"
          >
            View projects
          </a>
          <a
            href="#contact"
            className="rounded-full border border-neutral-700 px-5 py-2.5 text-sm font-medium hover:border-primary hover:text-primary transition"
          >
            Get in touch
          </a>
        </div>
      </div>
      <div className="shrink-0 md:mt-0 mt-12 flex justify-center">
        <div className="relative w-44 md:w-[420px] aspect-square">
          <div
            aria-hidden
            className="absolute inset-0 rounded-full bg-primary/30 blur-[100px]"
          />
          <Image
            src="/neonimage.webp"
            alt=""
            aria-hidden
            fill
            sizes="(min-width: 768px) 420px, 176px"
            quality={65}
            priority
            className="opacity-95 object-contain select-none pointer-events-none"
          />
        </div>
      </div>
    </section>
  );
}
