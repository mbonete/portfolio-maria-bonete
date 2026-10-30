import { person } from "@/lab/content";
import { contactLine } from "../_content";

const ext = { target: "_blank", rel: "noreferrer" } as const;

// The closing line of the inner pages: whoever read this far is the visitor most worth keeping.
export default function ContactStrip() {
  return (
    <aside className="le-strip" aria-label="Contact">
      <p>{contactLine}</p>
      <div className="le-links">
        <a href={person.links.linkedin} {...ext} className="le-link-strong">LinkedIn</a>
        <a href={person.links.cv} {...ext}>CV (PDF)</a>
      </div>
    </aside>
  );
}
