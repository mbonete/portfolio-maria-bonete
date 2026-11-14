// A phone showing the real app: a store screenshot, a loop recorded from the game, or the live site.
export default function Phone({ children, size }: { children: React.ReactNode; size?: "lead" }) {
  return (
    <div className="lf-phone" data-size={size}>
      <div className="lf-phone-screen">{children}</div>
    </div>
  );
}
