import type { InventoryItem } from "../../types/inventory";
import { formatDateTime, formatMoney, formatNumber } from "../../utils/format";
import { StatusBadge } from "./Badges";

interface Props {
  items: InventoryItem[];
  onAdjust: (item: InventoryItem) => void;
  onReorder: (item: InventoryItem) => void;
  onHistory: (item: InventoryItem) => void;
}

const th = "px-3 py-2.5";
const quantityColor = { in_stock: "text-gray-900", low_stock: "text-amber-600", out_of_stock: "text-rose-600" } as const;
const action = "rounded px-2 py-1 font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600";

export default function InventoryTable({ items, onAdjust, onReorder, onHistory }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1000px] text-left text-xs">
        <caption className="sr-only">Stock levels by product and branch</caption>
        <thead>
          <tr className="border-y border-gray-100 bg-gray-50/60 text-[11px] font-semibold uppercase text-gray-500">
            <th scope="col" className={th}>Product</th>
            <th scope="col" className={th}>Branch</th>
            <th scope="col" className={`${th} text-right`}>Quantity</th>
            <th scope="col" className={`${th} text-right`}>Reorder Level</th>
            <th scope="col" className={th}>Status</th>
            <th scope="col" className={`${th} text-right`}>Inventory Value</th>
            <th scope="col" className={th}>Last Updated</th>
            <th scope="col" className={`${th} text-right`}>Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 font-medium">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50/80">
              <td className="px-3 py-3">
                <div className="font-bold text-gray-900">{item.product_name}</div>
                <div className="font-mono text-[11px] text-gray-400">{item.sku}</div>
              </td>
              <td className="px-3 py-3 text-gray-700">{item.branch_code} {item.branch_name}</td>
              <td className={`px-3 py-3 text-right text-sm font-bold ${quantityColor[item.stock_status]}`}>{formatNumber(item.quantity)}</td>
              <td className="px-3 py-3 text-right text-gray-500">{formatNumber(item.reorder_level)}</td>
              <td className="px-3 py-3"><StatusBadge status={item.stock_status} /></td>
              <td className="px-3 py-3 text-right text-gray-900">{formatMoney(item.inventory_value)}</td>
              <td className="px-3 py-3 whitespace-nowrap text-gray-500">{formatDateTime(item.updated_at)}</td>
              <td className="px-3 py-3 text-right whitespace-nowrap">
                <button type="button" onClick={() => onAdjust(item)} className={`${action} text-indigo-600 hover:bg-indigo-50`}>Adjust</button>
                <button type="button" onClick={() => onReorder(item)} className={`${action} text-gray-600 hover:bg-gray-100`}>Reorder level</button>
                <button type="button" onClick={() => onHistory(item)} className={`${action} text-gray-600 hover:bg-gray-100`}>History</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}