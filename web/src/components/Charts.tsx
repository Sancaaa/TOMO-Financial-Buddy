import { rupiahShort } from "../lib/format";

export interface Slice {
  name: string;
  value: number;
  color: string;
}

export function Donut({
  data,
  centerLabel,
  size = 180,
  thickness = 26,
}: {
  data: Slice[];
  centerLabel?: string;
  size?: number;
  thickness?: number;
}) {
  const total = data.reduce((s, d) => s + d.value, 0);
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  const cx = size / 2;
  let acc = 0;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Donut kategori">
      <circle cx={cx} cy={cx} r={r} fill="none" stroke="var(--cream-2)" strokeWidth={thickness} />
      <g transform={`rotate(-90 ${cx} ${cx})`}>
        {total > 0 &&
          data.map((d, i) => {
            const len = (d.value / total) * c;
            const pct = Math.round((d.value / total) * 100);
            const el = (
              <circle
                key={i}
                cx={cx}
                cy={cx}
                r={r}
                fill="none"
                stroke={d.color}
                strokeWidth={thickness}
                strokeDasharray={`${len} ${c - len}`}
                strokeDashoffset={-acc}
              >
                <title>{`${d.name}: ${rupiahShort(d.value)} · ${pct}%`}</title>
              </circle>
            );
            acc += len;
            return el;
          })}
      </g>
      {centerLabel && (
        <text
          x={cx}
          y={cx}
          textAnchor="middle"
          dominantBaseline="central"
          fill="var(--ink)"
          style={{ fontFamily: "var(--ff-display)", fontWeight: 700, fontSize: 16 }}
        >
          {centerLabel}
        </text>
      )}
    </svg>
  );
}

export interface TrendBar {
  label: string;
  expense: number;
  income: number;
}

export function Bars({ data }: { data: TrendBar[] }) {
  const W = 320;
  const H = 150;
  const pad = 22;
  const max = Math.max(1, ...data.map((d) => Math.max(d.expense, d.income)));
  const n = data.length;
  const slot = (W - pad) / Math.max(1, n);
  const barW = Math.min(14, slot / 3);
  const chartH = H - pad;

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Tren bulanan">
      {data.map((d, i) => {
        const x = pad + i * slot + slot / 2;
        const eh = (d.expense / max) * chartH;
        const ih = (d.income / max) * chartH;
        return (
          <g key={i}>
            <rect x={x - barW - 1} y={chartH - eh} width={barW} height={eh} rx={3} fill="var(--tomato)">
              <title>{`${d.label} · keluar ${rupiahShort(d.expense)}`}</title>
            </rect>
            <rect x={x + 1} y={chartH - ih} width={barW} height={ih} rx={3} fill="var(--leaf)">
              <title>{`${d.label} · masuk ${rupiahShort(d.income)}`}</title>
            </rect>
            <text x={x} y={H - 6} textAnchor="middle" fill="var(--ink-muted)" style={{ fontSize: 10 }}>
              {d.label}
            </text>
          </g>
        );
      })}
      <text x={pad - 4} y={10} textAnchor="start" fill="var(--ink-muted)" style={{ fontSize: 9 }}>
        {rupiahShort(max)}
      </text>
    </svg>
  );
}
