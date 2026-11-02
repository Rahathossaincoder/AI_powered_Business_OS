import { Link } from "react-router-dom";
import StockBadge from "../../components/ui/StockBadge";
import type { Product } from "../../types/product";
import { formatMoney } from "../../utils/format";

interface Props {
  products: Product[];
  onDeactivate: (product: Product) => void;
}

const th = "px-3 py-2.5";

export default function ProductTable({ products, onDeactivate }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[900px] text-left text-xs">
        <caption className="sr-only">Products</caption>
        <thead>
          <tr className="border-y border-gray-100 bg-gray-50/60 text-[11px] font-semibold uppercase text-gray-500">
            <th scope="col" className={th}>Product</th>
            <th scope="col" className={th}>SKU</th>
            <th scope="col" className={th}>Category</th>
            <th scope="col" className={`${th} text-right`}>Cost Price</th>
            <th scope="col" className={`${th} text-right`}>Selling Price</th>
            <th scope="col" className={th}>Stock</th>
            <th scope="col" className={`${th} text-right`}>Reorder Level</th>
            <th scope="col" className={th}>Status</th>
            <th scope="col" className={`${th} text-right`}>Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 font-medium">
          {products.map((p) => (
            <tr key={p.id} className="hover:bg-gray-50/80">
              <td className="px-3 py-3">
                <Link to={`/products/${p.id}`} className="font-bold text-gray-900 hover:text-indigo-600 hover:underline">
                  {p.name}
                </Link>
              </td>
              <td className="px-3 py-3 font-mono text-gray-500">{p.sku}</td>
              <td className="px-3 py-3">
                <span className="rounded bg-gray-100 px-2 py-0.5 text-[11px] text-gray-700">{p.category_name}</span>
              </td>
              <td className="px-3 py-3 text-right text-gray-600">{formatMoney(p.cost_price)}</td>
              <td className="px-3 py-3 text-right font-bold text-gray-900">{formatMoney(p.selling_price)}</td>
              <td className="px-3 py-3"><StockBadge status={p.stock_status} stock={p.stock} /></td>
              <td className="px-3 py-3 text-right text-gray-600">{p.reorder_level}</td>
              <td className="px-3 py-3">
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${p.is_active ? "bg-emerald-50 text-emerald-600" : "bg-gray-100 text-gray-500"}`}>
                  {p.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td className="px-3 py-3 text-right whitespace-nowrap">
                <Link to={`/products/${p.id}/edit`} className="rounded px-2.5 py-1 font-semibold text-indigo-600 hover:bg-indigo-50">Edit</Link>
                {p.is_active && (
                  <button type="button" onClick={() => onDeactivate(p)} className="rounded px-2.5 py-1 font-semibold text-rose-600 hover:bg-rose-50">
                    Deactivate
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
