export default function BackgroundFx() {
  return (
    <div
      aria-hidden
      className="fixed inset-0 -z-10 overflow-hidden pointer-events-none"
    >
      <div
        className="absolute rounded-full blur-3xl animate-drift-a will-change-transform"
        style={{
          top: "-10%",
          left: "-10%",
          width: "clamp(360px, 60vw, 900px)",
          height: "clamp(360px, 60vw, 900px)",
          background:
            "radial-gradient(circle at 30% 30%, var(--color-primary), transparent 65%)",
          opacity: "var(--blob-opacity)",
          transform: "translateZ(0)",
        }}
      />
      <div
        className="absolute rounded-full blur-3xl animate-drift-b will-change-transform"
        style={{
          bottom: "-15%",
          right: "-10%",
          width: "clamp(360px, 65vw, 1000px)",
          height: "clamp(360px, 65vw, 1000px)",
          background:
            "radial-gradient(circle at 70% 70%, var(--color-secondary), transparent 65%)",
          opacity: "var(--blob-opacity)",
          transform: "translateZ(0)",
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle, currentColor 1px, transparent 1px)",
          backgroundSize: "24px 24px",
          color: "var(--foreground)",
          opacity: "var(--grid-opacity)",
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 30%, var(--background) 100%)",
        }}
      />
    </div>
  );
}
