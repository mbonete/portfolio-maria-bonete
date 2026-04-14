export default function Contact() {
  return (
    <section
      id="contact"
      className="py-20 border-t border-neutral-800"
    >
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />{" "}
        Contact
      </h2>
      <p className="text-neutral-400 max-w-xl">
        Want to work together, or just say hi? Email is the fastest way to
        reach me.
      </p>
      <div className="mt-6 flex flex-wrap gap-4 text-sm">
        <a
          href="mailto:mbonetedev@gmail.com"
          className="underline underline-offset-4 decoration-neutral-400 hover:decoration-primary hover:text-primary transition-colors"
        >
          mbonetedev@gmail.com
        </a>
        <a
          href="https://github.com/mbonete"
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-4 decoration-neutral-400 hover:decoration-primary hover:text-primary transition-colors"
        >
          GitHub
        </a>
        <a
          href="https://www.linkedin.com/in/maria-bonete"
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-4 decoration-neutral-400 hover:decoration-primary hover:text-primary transition-colors"
        >
          LinkedIn
        </a>
        <a
          href="https://www.mariabonete.com/static/cv.pdf"
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-4 decoration-neutral-400 hover:decoration-primary hover:text-primary transition-colors"
        >
          CV
        </a>
      </div>
    </section>
  );
}
