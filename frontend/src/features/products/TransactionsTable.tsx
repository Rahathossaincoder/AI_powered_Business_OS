import type { InventoryTransaction } from "../../types/inventory";
import { formatDateTime, formatNumber } from "../../utils/format";
import { TypeBadge } from "./Badges";

const th = "px-3 py-2.5";

export default function TransactionsTable({ rows }: { rows: InventoryTransaction[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1050px] text-left text-xs">
        <caption className="sr-only">Inventory ledger</caption>
        <thead>
          <tr className="border-y border-gray-100 bg-gray-50/60 text-[11px] font-semibold uppercase text-gray-500">
            <th scope="col" className={th}>Date</th>
            <th scope="col" className={th}>Product</th>
            <th scope="col" className={th}>Branch</th>
            <th scope="col" className={th}>Type</th>
            <th scope="col" className={`${th} text-right`}>Change</th>
            <th scope="col" className={`${th} text-right`}>Before</th>
            <th scope="col" className={`${th} text-right`}>After</th>
            <th scope="col" className={th}>Reference</th>
            <th scope="col" className={th}>Reason</th>
            <th scope="col" className={th}>Created By</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 font-medium">
          {rows.map((t) => (
            <tr key={t.id} className="align-top hover:bg-gray-50/80">
              <td className="px-3 py-3 whitespace-nowrap text-gray-500">{formatDateTime(t.created_at)}</td>
              <td className="px-3 py-3">
                <div className="font-bold text-gray-900">{t.product_name}</div>
                <div className="font-mono text-[11px] text-gray-400">{t.sku}</div>
              </td>
              <td className="px-3 py-3 text-gray-700">{t.branch_code}</td>
              <td className="px-3 py-3"><TypeBadge type={t.transaction_type} /></td>
              <td className={`px-3 py-3 text-right font-bold ${t.quantity_change > 0 ? "text-emerald-600" : "text-rose-600"}`}>
                {t.quantity_change > 0 ? "+" : ""}{formatNumber(t.quantity_change)}
              </td>
              <td className="px-3 py-3 text-right text-gray-500">{formatNumber(t.quantity_before)}</td>
              <td className="px-3 py-3 text-right text-gray-900">{formatNumber(t.quantity_after)}</td>
              <td className="px-3 py-3 font-mono text-gray-500">{t.reference_type ? `${t.reference_type} ${t.reference_id}` : "-"}</td>
              <td className="px-3 py-3 text-gray-700">
                {t.reason || "-"}
                {t.note && <div className="mt-0.5 text-[11px] font-normal text-gray-400">{t.note}</div>}
              </td>
              <td className="px-3 py-3 text-gray-700">{t.created_by_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}