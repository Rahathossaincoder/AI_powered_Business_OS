import type { TransactionType } from "../../types/inventory";
import type { StockStatus } from "../../types/product";

const STATUS: Record<StockStatus, { label: string; style: string }> = {
  in_stock: { label: "In Stock", style: "bg-emerald-50 text-emerald-600" },
  low_stock: { label: "Low Stock", style: "bg-amber-50 text-amber-600" },
  out_of_stock: { label: "Out of Stock", style: "bg-rose-50 text-rose-600" },
};

export function StatusBadge({ status }: { status: StockStatus }) {
  const { label, style } = STATUS[status];
  return <span className={`inline-block rounded-full px-2 py-0.5 text-[11px] font-bold ${style}`}>{label}</span>;
}

const TYPE_STYLE: Record<TransactionType, string> = {
  INITIAL_STOCK: "bg-indigo-50 text-indigo-600",
  PURCHASE: "bg-emerald-50 text-emerald-600",
  RETURN: "bg-teal-50 text-teal-600",
  SALE: "bg-sky-50 text-sky-600",
  ADJUSTMENT: "bg-amber-50 text-amber-600",
  DAMAGE: "bg-rose-50 text-rose-600",
  CORRECTION: "bg-gray-100 text-gray-600",
};

export function TypeBadge({ type }: { type: TransactionType }) {
  return <span className={`inline-block rounded px-2 py-0.5 font-mono text-[10px] font-bold ${TYPE_STYLE[type]}`}>{type}</span>;
}