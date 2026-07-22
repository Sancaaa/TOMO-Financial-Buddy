import { categoryColor } from "../lib/colors";
import { dateLabel, rupiah } from "../lib/format";
import { useDeleteTransaction } from "../lib/queries";
import { Icon, categoryIcon } from "./Icon";
import { SwipeRow, type SwipeAction } from "./SwipeRow";
import type { Transaction } from "../lib/types";

export function TxList({
  items,
  onSelect,
}: {
  items: Transaction[];
  onSelect?: (tx: Transaction) => void;
}) {
  const del = useDeleteTransaction();

  if (items.length === 0) {
    return <p className="hint" style={{ padding: "8px 2px" }}>Belum ada transaksi.</p>;
  }

  return (
    <div className="txlist">
      {items.map((tx) => {
        const actions: SwipeAction[] = [
          { label: "Ubah", kind: "edit", onClick: () => onSelect?.(tx) },
          { label: "Hapus", kind: "del", onClick: () => del.mutate(tx.id) },
        ];

        let content;
        if (tx.type === "transfer") {
          content = (
            <div className="tx">
              <span className="cat-badge" style={{ "--c": "var(--ink-muted)" } as React.CSSProperties}>
                <Icon name="swap" size={19} />
              </span>
              <span className="body">
                <span className="desc">
                  {tx.account?.name ?? "?"} → {tx.dest_account?.name ?? "?"}
                </span>
                <span className="meta">Transfer · {dateLabel(tx.occurred_at)}</span>
              </span>
              <span className="amt">{rupiah(tx.amount)}</span>
            </div>
          );
        } else {
          const income = tx.type === "income";
          const catName = tx.category?.name ?? (income ? "Pemasukan" : "Lainnya");
          const color = income ? "var(--leaf-dark)" : categoryColor(tx.category?.name);
          content = (
            <div className="tx">
              <span className="cat-badge" style={{ "--c": color } as React.CSSProperties}>
                <Icon name={categoryIcon(tx.category?.icon, tx.category?.name)} size={19} />
              </span>
              <span className="body">
                <span className="desc ico-txt">
                  {tx.description || catName}
                  {tx.source === "ocr" && <Icon name="camera" size={13} />}
                </span>
                <span className="meta">
                  {catName} · {dateLabel(tx.occurred_at)}
                </span>
              </span>
              <span className={"amt " + (income ? "inc" : "exp")}>
                {income ? "+" : ""}
                {rupiah(tx.amount)}
              </span>
            </div>
          );
        }

        return (
          <SwipeRow key={tx.id} actions={actions} onTap={() => onSelect?.(tx)}>
            {content}
          </SwipeRow>
        );
      })}
    </div>
  );
}
