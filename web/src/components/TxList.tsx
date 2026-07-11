import { categoryColor } from "../lib/colors";
import { dateLabel, rupiah } from "../lib/format";
import type { Transaction } from "../lib/types";

export function TxList({
  items,
  onSelect,
}: {
  items: Transaction[];
  onSelect?: (tx: Transaction) => void;
}) {
  if (items.length === 0) {
    return <p className="hint" style={{ padding: "8px 2px" }}>Belum ada transaksi.</p>;
  }
  return (
    <div className="txlist">
      {items.map((tx) => {
        const income = tx.type === "income";
        const catName = tx.category?.name ?? (income ? "Pemasukan" : "Lainnya");
        return (
          <button key={tx.id} className="tx" onClick={() => onSelect?.(tx)}>
            <span className="dot" style={{ background: categoryColor(tx.category?.name) }} />
            <span className="body">
              <span className="desc">{tx.description || catName}</span>
              <span className="meta">
                {catName} · {dateLabel(tx.occurred_at)}
                {tx.source === "ocr" ? " · 📸" : ""}
              </span>
            </span>
            <span className={"amt" + (income ? " inc" : "")}>
              {income ? "+" : ""}
              {rupiah(tx.amount)}
            </span>
          </button>
        );
      })}
    </div>
  );
}
