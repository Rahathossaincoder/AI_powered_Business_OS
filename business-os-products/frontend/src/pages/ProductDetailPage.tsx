import { ArrowLeft, Pencil } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import StockBadge from "../components/ui/StockBadge";
import { ErrorState, SkeletonRows } from "../components/ui/States";
import { getProduct } from "../services/api/products";
import type { Product } from "../types/product";
import { formatDate, formatMoney } from "../utils/format";

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5 text-xs">
      <dt className="text-gray-500">{label}</dt>
      <dd className="text-right font-semibold text-gray-900">{children}</dd>
    </div>
  );
}

export default function ProductDetailPage() {
  const { id = "" } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    getProduct(id)
      .then(setProduct)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(load, [load]);

  if (loading) return <SkeletonRows rows={4} />;
  if (error || !product) return <ErrorState message={error || "Product not found."} onRetry={load} />;

  const margin = Number(product.selling_price) - Number(product.cost_price);
  const marginPct = Number(product.selling_price) > 0 ? (margin / Number(product.selling_price)) * 100 : 0;

  return (
    <>
      <Link to="/products" className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-900">
        <ArrowLeft className="h-4 w-4" />
        Back to catalog
      </Link>

      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">{product.name}</h1>
          <p className="mt-0.5 font-mono text-xs text-gray-500">{product.sku}</p>
        </div>
        <Link to={`/products/${product.id}/edit`} className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-50">
          <Pencil className="h-4 w-4" />
          Edit product
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <section className="rounded-2xl border border-gray-200 bg-white p-5 lg:col-span-2">
          <h2 className="mb-2 text-sm font-bold text-gray-900">Product information</h2>
          <dl className="divide-y divide-gray-100">
            <Row label="Category">{product.category_name}</Row>
            <Row label="Unit">{product.unit}</Row>
            <Row label="Status">{product.is_active ? "Active" : "Inactive"}</Row>
            <Row label="Created">{formatDate(product.created_at)}</Row>
            <Row label="Last updated">{formatDate(product.updated_at)}</Row>
          </dl>
          <h3 className="mt-4 text-xs font-bold text-gray-900">Description</h3>
          <p className="mt-1 whitespace-pre-line text-xs text-gray-600">{product.description || "No description provided."}</p>
        </section>

        <div className="space-y-4">
          <section className="rounded-2xl border border-gray-200 bg-white p-5">
            <h2 className="mb-2 text-sm font-bold text-gray-900">Pricing</h2>
            <dl className="divide-y divide-gray-100">
              <Row label="Cost price">{formatMoney(product.cost_price)}</Row>
              <Row label="Selling price">{formatMoney(product.selling_price)}</Row>
              <Row label="Margin">
                {formatMoney(margin)} ({marginPct.toFixed(1)}%)
              </Row>
            </dl>
          </section>
          <section className="rounded-2xl border border-gray-200 bg-white p-5">
            <h2 className="mb-2 text-sm font-bold text-gray-900">Inventory summary</h2>
            <dl className="divide-y divide-gray-100">
              <Row label="Current stock">
                <StockBadge status={product.stock_status} stock={product.stock} />
              </Row>
              <Row label="Reorder level">{product.reorder_level}</Row>
            </dl>
          </section>
        </div>
      </div>
    </>
  );
}
