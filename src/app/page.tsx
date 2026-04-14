import Hero from "@/components/Hero";
import About from "@/components/About";
import Experience from "@/components/Experience";
import Projects from "@/components/Projects";
import Contact from "@/components/Contact";
import Nav from "@/components/Nav";

export default function Home() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-6">
        <Hero />
        <About />
        <Experience />
        <Projects />
        <Contact />
      </main>
      <footer className="mx-auto max-w-5xl px-6 py-10 text-sm text-neutral-500">
        © {new Date().getFullYear()} Maria Bonete. Made with love from Spain.
      </footer>
    </>
  );
}
