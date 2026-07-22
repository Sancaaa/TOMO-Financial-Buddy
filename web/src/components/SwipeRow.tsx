import { useRef, useState } from "react";

export interface SwipeAction {
  label: string;
  kind: "edit" | "del";
  onClick: () => void;
}

const ACTION_W = 76;

/**
 * Baris yang bisa digeser ke kiri untuk memunculkan aksi cepat (ubah / hapus) —
 * padanan web dari tombol inline di Telegram (FR-1.4). Tap biasa tetap memicu
 * `onTap`. Memakai Pointer Events (jalan untuk sentuh & mouse-drag).
 */
export function SwipeRow({
  children,
  actions,
  onTap,
}: {
  children: React.ReactNode;
  actions: SwipeAction[];
  onTap?: () => void;
}) {
  const width = actions.length * ACTION_W;
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const active = useRef(false); // pointer sedang ditekan
  const locked = useRef(false); // sudah dipastikan geseran horizontal
  const startX = useRef(0);
  const startY = useRef(0);
  const base = useRef(0);
  const moved = useRef(false);

  function down(e: React.PointerEvent) {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    active.current = true;
    locked.current = false;
    moved.current = false;
    startX.current = e.clientX;
    startY.current = e.clientY;
  }
  function move(e: React.PointerEvent) {
    if (!active.current) return;
    const dxRaw = e.clientX - startX.current;
    const dyRaw = e.clientY - startY.current;
    if (!locked.current) {
      if (Math.abs(dxRaw) < 8 && Math.abs(dyRaw) < 8) return; // arah belum jelas
      if (Math.abs(dyRaw) > Math.abs(dxRaw)) {
        active.current = false; // niat scroll vertikal → serahkan ke browser
        return;
      }
      locked.current = true; // kunci horizontal, baru capture (tak ganggu scroll)
      moved.current = true;
      setDragging(true);
      (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
    }
    setDx(Math.max(-width, Math.min(0, base.current + dxRaw)));
  }
  function endDrag() {
    if (!active.current) return;
    active.current = false;
    if (!locked.current) return; // tak pernah jadi geseran horizontal
    locked.current = false;
    setDragging(false);
    base.current = dx < -width / 2 ? -width : 0;
    setDx(base.current);
  }
  function close() {
    base.current = 0;
    setDx(0);
  }
  function tap() {
    if (moved.current) return; // itu geseran, bukan tap
    if (base.current !== 0) {
      close(); // sedang terbuka → tutup dulu
      return;
    }
    onTap?.();
  }

  return (
    <div className="swipe">
      <div className="swipe-actions" aria-hidden={dx === 0}>
        {actions.map((a) => (
          <button
            key={a.label}
            className={a.kind === "del" ? "act-del" : "act-edit"}
            onClick={() => {
              close();
              a.onClick();
            }}
          >
            {a.label}
          </button>
        ))}
      </div>
      <div
        className={"swipe-fg" + (dragging ? " dragging" : "")}
        style={{ transform: `translateX(${dx}px)` }}
        role="button"
        tabIndex={0}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onClick={tap}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onTap?.();
          }
        }}
      >
        {children}
      </div>
    </div>
  );
}
