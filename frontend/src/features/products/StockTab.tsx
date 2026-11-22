import { Plus, Search } from "lucide-react";
import { useEffect, useState } from "react";
import Pagination from "../../components/ui/Pagination";
import { EmptyState, ErrorState, SkeletonRows } from "../../components/ui/States";
import { useDebounce } from "../../hooks/useDebounce";
import { INVENTORY_PAGE_SIZE, listInventory } from "../../services/api/inventory";
import { EMPTY_STOCK_FILTERS, type Branch, type InventoryItem, type StockFilters } from "../../types/inventory";
import type { Paginated } from "../../types/product";
import InventoryTable from "./InventoryTable";

interface Props {
  branches: Branch[];
  reloadKey: number;
  onAdd: () => void;
  onAdjust: (item: InventoryItem) => void;
  onReorder: (item: InventoryItem) => void;
  onHistory: (item: InventoryItem) => void;
}

const field = "rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-700 focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20";

export default function StockTab({ branches, reloadKey, onAdd, onAdjust, onReorder, onHistory }: Props) {
  const [filters, setFilters] = useState<StockFilters>(EMPTY_STOCK_FILTERS);
  const debounced = useDebounce(filters, 400);
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Paginated<InventoryItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    listInventory(debounced, page)
      .then((result) => !ignore && setData(result))
      .catch((e: Error) => !ignore && setError(e.message))
      .finally(() => !ignore && setLoading(false));
    return () => {
      ignore = true;
    };
  }, [debounced, page, reloadKey, retry]);

  function change(patch: Partial<StockFilters>) {
    setFilters((current) => ({ ...current, ...patch }));
    setPage(1);
  }

  const isFiltered = JSON.stringify(filters) !== JSON.stringify(EMPTY_STOCK_FILTERS);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative min-w-0 flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="search"
            aria-label="Search stock"
            value={filters.search}
            onChange={(e) => change({ search: e.target.value })}
            placeholder="Filter by SKU, product, or branch..."
            className={`${field} w-full pl-9`}
          />
        </div>
        <select aria-label="Branch" value={filters.branch} onChange={(e) => change({ branch: e.target.value })} className={field}>
          <option value="">All branches</option>
          {branches.map((b) => (
            <option key={b.id} value={b.id}>{b.code} {b.name}</option>
          ))}
        </select>
        <select aria-label="Stock level" value={filters.stockStatus} onChange={(e) => change({ stockStatus: e.target.value })} className={field}>
          <option value="">Any stock level</option>
          <option value="in_stock">In Stock</option>
          <option value="low_stock">Low Stock</option>
          <option value="out_of_stock">Out of Stock</option>
        </select>
        <select aria-label="Sort by" value={filters.ordering} onChange={(e) => change({ ordering: e.target.value })} className={field}>
          <option value="-updated_at">Recently updated</option>
          <option value="product__name">Product A-Z</option>
          <option value="quantity">Quantity: low to high</option>
          <option value="-inventory_value">Value: high to low</option>
        </select>
        {isFiltered && (
          <button type="button" onClick={() => change(EMPTY_STOCK_FILTERS)} className="px-2 text-xs font-semibold text-indigo-600 hover:underline">
            Reset
          </button>
        )}
      </div>

      {loading && <SkeletonRows />}
      {!loading && error && <ErrorState message={error} onRetry={() => setRetry((k) => k + 1)} />}
      {!loading && !error && data && data.count === 0 && (
        isFiltered ? (
          <EmptyState title="No stock records match your filters" description="Try a different search or reset the filters." />
        ) : (
          <EmptyState
            title="No stock records yet"
            description="Add a record to start tracking how many units each branch holds."
            action={
              <button type="button" onClick={onAdd} className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-700">
                <Plus className="h-4 w-4" />
                Add inventory record
              </button>
            }
          />
        )
      )}
      {!loading && !error && data && data.count > 0 && (
        <>
          <InventoryTable items={data.results} onAdjust={onAdjust} onReorder={onReorder} onHistory={onHistory} />
          <Pagination page={page} pageSize={INVENTORY_PAGE_SIZE} count={data.count} onChange={setPage} />
        </>
      )}
    </div>
  );
}