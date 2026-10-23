import type { StockStatus } from "../../types/product";

const STYLES: Record<StockStatus, string> = {
  in_stock: "bg-emerald-50 text-emerald-600",
  low_stock: "bg-amber-50 text-amber-600",
  out_of_stock: "bg-rose-50 text-rose-600",
};

export default function StockBadge({ status, stock }: { status: StockStatus; stock: number }) {
  const label = status === "out_of_stock" ? "Out of stock" : status === "low_stock" ? `${stock} left` : `${stock} in stock`;
  return <span className={`inline-block rounded-full px-2 py-0.5 text-[11px] font-bold ${STYLES[status]}`}>{label}</span>;
}
