import type { BranchSummary } from "../../types/inventory";
import { formatNumber } from "../../utils/format";

function health(branch: BranchSummary): { label: string; style: string; note: string } {
  const attention = branch.low_stock + branch.out_of_stock;
  if (branch.out_of_stock > 0) return { label: "Stock-out", style: "bg-rose-50 text-rose-600", note: `${attention} SKUs need reorder` };
  if (branch.low_stock > 0) return { label: "Low Stock Alert", style: "bg-amber-50 text-amber-600", note: `${attention} SKUs need reorder` };
  return { label: "Optimal", style: "bg-emerald-50 text-emerald-600", note: `${branch.skus} SKUs tracked` };
}

export default function BranchCards({ branches }: { branches: BranchSummary[] }) {
  if (branches.length === 0) return null;
  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {branches.map((b) => {
        const h = health(b);
        return (
          <li key={b.id} className="space-y-2 rounded-xl border border-gray-200 bg-white p-4 shadow-xs sm:p-5">
            <div className="flex items-center justify-between gap-2 text-xs text-gray-500">
              <span className="truncate font-semibold text-gray-900">
                {b.code}: {b.name}
              </span>
              <span className={`shrink-0 rounded px-2 py-0.5 text-[10px] font-bold ${h.style}`}>{h.label}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatNumber(b.units)} Units</div>
            <div className="text-[11px] text-gray-400">{h.note}</div>
          </li>
        );
      })}
    </ul>
  );
}