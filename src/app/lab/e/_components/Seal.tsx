// The red seal: the site's home mark, stamped slightly out of true.
export default function Seal({ label }: { label: string }) {
  return (
    <a className="le-seal" href="#top" aria-label={label}>
      <svg viewBox="0 0 40 40" aria-hidden>
        <path d="M3.2 4.1c11-1.3 22.7-1.1 33.5-.2.9 10.7 1 21.6-.3 32.3-11 1-22.2 1.2-33.1.2C2.2 25.6 2.3 14.8 3.2 4.1Z" />
        <text x="20" y="27.5" textAnchor="middle">MB</text>
      </svg>
    </a>
  );
}
