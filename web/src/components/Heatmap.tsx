import { rupiah } from "../lib/format";

const WD = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"];

export function Heatmap({
  days,
  firstWeekday,
}: {
  days: { day: number; total: number }[];
  firstWeekday: number; // 0=Senin .. 6=Minggu
}) {
  const max = Math.max(1, ...days.map((d) => d.total));
  const blanks = Array.from({ length: firstWeekday });

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 4 }}>
      {WD.map((w) => (
        <div key={w} className="hint" style={{ textAlign: "center", fontSize: 10 }}>{w}</div>
      ))}
      {blanks.map((_, i) => (
        <div key={"b" + i} />
      ))}
      {days.map((d) => {
        const intensity = d.total > 0 ? 0.18 + 0.82 * (d.total / max) : 0;
        return (
          <div
            key={d.day}
            title={`${d.day}: ${rupiah(d.total)}`}
            style={{
              aspectRatio: "1 / 1",
              borderRadius: 6,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 10,
              background:
                d.total > 0
                  ? `color-mix(in srgb, var(--tomato) ${Math.round(intensity * 100)}%, var(--cream-2))`
                  : "var(--cream-2)",
              color: intensity > 0.5 ? "#fff" : "var(--ink-muted)",
            }}
          >
            {d.day}
          </div>
        );
      })}
    </div>
  );
}
