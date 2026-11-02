import { Package } from "lucide-react";
import { Link } from "react-router-dom";
import StockBadge from "../../components/ui/StockBadge";
import type { Product } from "../../types/product";
import { formatMoney } from "../../utils/format";

export default function ProductGrid({ products }: { products: Product[] }) {
  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {products.map((p) => (
        <li key={p.id}>
          <Link to={`/products/${p.id}`} className="block space-y-3 rounded-xl border border-gray-200 p-4 transition-shadow hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
            <div className="flex items-start justify-between gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                <Package className="h-4 w-4" />
              </div>
              <StockBadge status={p.stock_status} stock={p.stock} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-900">{p.name}</h3>
              <p className="font-mono text-[11px] text-gray-400">{p.sku}</p>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="rounded bg-gray-100 px-2 py-0.5 text-[11px] text-gray-700">{p.category_name}</span>
              <span className="font-bold text-gray-900">{formatMoney(p.selling_price)}</span>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
