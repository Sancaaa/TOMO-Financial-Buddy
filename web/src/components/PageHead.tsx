import type { ReactNode } from "react";

export function PageHead({
  eyebrow,
  title,
  right,
}: {
  eyebrow: string;
  title: string;
  right?: ReactNode;
}) {
  return (
    <header className="pagehead">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
      </div>
      {right && <div className="pagehead-right">{right}</div>}
    </header>
  );
}
