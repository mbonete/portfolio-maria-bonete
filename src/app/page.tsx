import dynamic from "next/dynamic";
import Hero from "@/components/Hero";
import Nav from "@/components/Nav";

const About = dynamic(() => import("@/components/About"));
const Experience = dynamic(() => import("@/components/Experience"));
const Projects = dynamic(() => import("@/components/Projects"));
const Contact = dynamic(() => import("@/components/Contact"));

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
      <footer className="mx-auto max-w-5xl px-6 py-10 text-sm text-neutral-400">
        © {new Date().getFullYear()} Maria Bonete. Made with love from Spain.
      </footer>
    </>
  );
}
