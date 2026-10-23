import { Plus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import Pagination from "../components/ui/Pagination";
import { EmptyState, ErrorState, SkeletonRows } from "../components/ui/States";
import { useToast } from "../components/ui/Toast";
import ProductFiltersBar from "../features/products/ProductFiltersBar";
import ProductGrid from "../features/products/ProductGrid";
import ProductTable from "../features/products/ProductTable";
import { useDebounce } from "../hooks/useDebounce";
import { listCategories } from "../services/api/categories";
import { deactivateProduct, getProductSummary, listProducts, PAGE_SIZE } from "../services/api/products";
import { EMPTY_FILTERS, type Category, type Paginated, type Product, type ProductFilters, type ProductSummary } from "../types/product";

export default function ProductsPage() {
  const toast = useToast();
  const [filters, setFilters] = useState<ProductFilters>(EMPTY_FILTERS);
  const debouncedFilters = useDebounce(filters, 400);
  const [page, setPage] = useState(1);
  const [view, setView] = useState<"table" | "grid">("table");
  const [data, setData] = useState<Paginated<Product> | null>(null);
  const [summary, setSummary] = useState<ProductSummary | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [target, setTarget] = useState<Product | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    listCategories().then(setCategories).catch(() => toast.error("Could not load categories."));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    getProductSummary().then(setSummary).catch(() => setSummary(null));
  }, [reloadKey]);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    listProducts(debouncedFilters, page)
      .then((result) => !ignore && setData(result))
      .catch((e: Error) => !ignore && setError(e.message))
      .finally(() => !ignore && setLoading(false));
    return () => {
      ignore = true;
    };
  }, [debouncedFilters, page, reloadKey]);

  const updateFilters = useCallback((patch: Partial<ProductFilters>) => {
    setFilters((current) => ({ ...current, ...patch }));
    setPage(1);
  }, []);

  async function confirmDeactivate() {
    if (!target) return;
    setBusy(true);
    try {
      await deactivateProduct(target.id);
      toast.success(`${target.name} was deactivated.`);
      setTarget(null);
      setReloadKey((k) => k + 1);
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const stats = [
    { label: "Total Products", value: summary?.total, color: "text-gray-900" },
    { label: "In Stock", value: summary?.in_stock, color: "text-emerald-600" },
    { label: "Low Stock Warning", value: summary?.low_stock, color: "text-amber-600" },
    { label: "Out of Stock", value: summary?.out_of_stock, color: "text-rose-600" },
  ];
  const hasFilters = JSON.stringify(filters) !== JSON.stringify(EMPTY_FILTERS);

  return (
    <>
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">Products Catalog</h1>
          <p className="mt-0.5 text-xs text-gray-500">Manage SKUs, product pricing, category assignments, and stock status.</p>
        </div>
        <Link to="/products/new" className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2">
          <Plus className="h-4 w-4" />
          Add New Product SKU
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="rounded-xl border border-gray-200 bg-white p-4 shadow-xs">
            <div className="text-xs text-gray-500">{s.label}</div>
            <div className={`mt-1 text-xl font-bold ${s.color}`}>{s.value ?? "–"}</div>
          </div>
        ))}
      </div>

      <section className="space-y-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-xs sm:p-6">
        <ProductFiltersBar filters={filters} categories={categories} view={view} onChange={updateFilters} onViewChange={setView} />

        {loading && <SkeletonRows />}
        {!loading && error && <ErrorState message={error} onRetry={() => setReloadKey((k) => k + 1)} />}
        {!loading && !error && data && data.count === 0 && (
          hasFilters ? (
            <EmptyState title="No products match your filters" description="Try a different search or reset the filters." />
          ) : (
            <EmptyState
              title="No products yet"
              description="Create your first product to start building your catalog."
              action={<Link to="/products/new" className="mt-2 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-700">Create your first product</Link>}
            />
          )
        )}
        {!loading && !error && data && data.count > 0 && (
          <>
            {view === "table" ? <ProductTable products={data.results} onDeactivate={setTarget} /> : <ProductGrid products={data.results} />}
            <Pagination page={page} pageSize={PAGE_SIZE} count={data.count} onChange={setPage} />
          </>
        )}
      </section>

      <ConfirmDialog
        open={target !== null}
        title="Deactivate product?"
        message={`${target?.name ?? "This product"} will be hidden from sales but its history stays intact. You can reactivate it later by editing it.`}
        confirmLabel="Deactivate"
        busy={busy}
        onConfirm={confirmDeactivate}
        onCancel={() => setTarget(null)}
      />
    </>
  );
}
