export function Tomato({
  size = 48,
  face = false,
  className,
}: {
  size?: number;
  face?: boolean;
  className?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      aria-hidden="true"
    >
      <path d="M49 34 C41 16 27 16 23 20 C33 22 37 28 41 36 Z" fill="#2E7D32" />
      <path d="M51 34 C59 16 73 16 77 20 C67 22 63 28 59 36 Z" fill="#4CAF50" />
      <path d="M36 30 C30 18 20 16 16 19 C25 22 28 27 31 34 Z" fill="#2E7D32" opacity=".85" />
      <rect x="47" y="16" width="6" height="20" rx="3" fill="#2E7D32" />
      <circle cx="50" cy="62" r="30" fill="#C0392B" />
      <ellipse cx="40" cy="52" rx="7" ry="5" fill="#fff" opacity=".13" />
      {face && (
        <g>
          <circle cx="41" cy="60" r="3.2" fill="#1C1007" />
          <circle cx="59" cy="60" r="3.2" fill="#1C1007" />
          <path d="M42 70 Q50 78 58 70" stroke="#1C1007" strokeWidth="3" fill="none" strokeLinecap="round" />
          <circle cx="34" cy="66" r="3" fill="#E74C3C" opacity=".45" />
          <circle cx="66" cy="66" r="3" fill="#E74C3C" opacity=".45" />
        </g>
      )}
    </svg>
  );
}
