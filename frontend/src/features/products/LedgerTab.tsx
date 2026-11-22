import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import Pagination from "../../components/ui/Pagination";
import { EmptyState, ErrorState, SkeletonRows } from "../../components/ui/States";
import { useDebounce } from "../../hooks/useDebounce";
import { INVENTORY_PAGE_SIZE, listTransactions } from "../../services/api/inventory";
import { EMPTY_LEDGER_FILTERS, TRANSACTION_TYPES, type Branch, type InventoryTransaction, type LedgerFilters } from "../../types/inventory";
import type { Paginated } from "../../types/product";
import TransactionsTable from "./TransactionsTable";

interface Props {
  branches: Branch[];
  reloadKey: number;
  filters: LedgerFilters;
  focusLabel: string;
  onFiltersChange: (filters: LedgerFilters) => void;
}

const field = "rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-700 focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20";

export default function LedgerTab({ branches, reloadKey, filters, focusLabel, onFiltersChange }: Props) {
  const debounced = useDebounce(filters, 400);
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Paginated<InventoryTransaction> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    listTransactions(debounced, page)
      .then((result) => !ignore && setData(result))
      .catch((e: Error) => !ignore && setError(e.message))
      .finally(() => !ignore && setLoading(false));
    return () => {
      ignore = true;
    };
  }, [debounced, page, reloadKey, retry]);

  function change(patch: Partial<LedgerFilters>) {
    onFiltersChange({ ...filters, ...patch });
    setPage(1);
  }

  const isFiltered = JSON.stringify(filters) !== JSON.stringify(EMPTY_LEDGER_FILTERS);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input type="search" aria-label="Search ledger" value={filters.search} onChange={(e) => change({ search: e.target.value })} placeholder="Search product, SKU, reason or reference..." className={`${field} w-full pl-9`} />
        </div>
        <select aria-label="Branch" value={filters.branch} onChange={(e) => change({ branch: e.target.value })} className={field}>
          <option value="">All branches</option>
          {branches.map((b) => (
            <option key={b.id} value={b.id}>{b.code} {b.name}</option>
          ))}
        </select>
        <select aria-label="Transaction type" value={filters.type} onChange={(e) => change({ type: e.target.value })} className={field}>
          <option value="">All types</option>
          {TRANSACTION_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.value}</option>
          ))}
        </select>
        <label className="flex items-center gap-1.5 text-xs text-gray-500">
          From
          <input type="date" value={filters.dateFrom} onChange={(e) => change({ dateFrom: e.target.value })} className={field} />
        </label>
        <label className="flex items-center gap-1.5 text-xs text-gray-500">
          To
          <input type="date" value={filters.dateTo} onChange={(e) => change({ dateTo: e.target.value })} className={field} />
        </label>
        {isFiltered && (
          <button type="button" onClick={() => change(EMPTY_LEDGER_FILTERS)} className="px-2 text-xs font-semibold text-indigo-600 hover:underline">
            Reset
          </button>
        )}
      </div>

      {filters.inventory && (
        <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
          Showing history for {focusLabel || `record #${filters.inventory}`}
          <button type="button" aria-label="Show all history" onClick={() => change({ inventory: "" })} className="rounded-full p-0.5 hover:bg-indigo-100">
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {loading && <SkeletonRows />}
      {!loading && error && <ErrorState message={error} onRetry={() => setRetry((k) => k + 1)} />}
      {!loading && !error && data && data.count === 0 && (
        <EmptyState
          title={isFiltered ? "No transactions match your filters" : "The ledger is empty"}
          description={isFiltered ? "Try a different search or reset the filters." : "Every stock change is recorded here automatically."}
        />
      )}
      {!loading && !error && data && data.count > 0 && (
        <>
          <TransactionsTable rows={data.results} />
          <Pagination page={page} pageSize={INVENTORY_PAGE_SIZE} count={data.count} onChange={setPage} />
        </>
      )}
    </div>
  );
}