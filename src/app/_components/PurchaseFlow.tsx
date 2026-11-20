// Rules 1 to 3 of the purchases article, in the order the game applies them to each purchase Google
// reports. Going along the line is "yes"; the note under a step says what happens otherwise.
const steps = [
  { step: "Is it paid?", note: "Still pending: nothing yet, and it is checked again on the next return." },
  { step: "Is its token new?", note: "Seen before: the game consumes it and grants nothing." },
  { step: "Save the coins and the token in one save", note: "If the app closes here, Google returns the purchase on the next check." },
  { step: "Consume the purchase", note: "The pack can be bought again." },
];

export default function PurchaseFlow() {
  return (
    <ol className="lf-flow">
      {steps.map((s) => (
        <li key={s.step}>
          <p className="lf-flow-step">{s.step}</p>
          <p className="lf-flow-note">{s.note}</p>
        </li>
      ))}
    </ol>
  );
}
