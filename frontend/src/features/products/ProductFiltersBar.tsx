import { LayoutGrid, List, Search } from "lucide-react";
import { EMPTY_FILTERS, type Category, type ProductFilters } from "../../types/product";

interface Props {
  filters: ProductFilters;
  categories: Category[];
  view: "table" | "grid";
  onChange: (patch: Partial<ProductFilters>) => void;
  onViewChange: (view: "table" | "grid") => void;
}

const field =
  "rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-700 focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20";

export default function ProductFiltersBar({ filters, categories, view, onChange, onViewChange }: Props) {
  const isFiltered = JSON.stringify(filters) !== JSON.stringify(EMPTY_FILTERS);

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative min-w-0 flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="search"
            aria-label="Search products"
            value={filters.search}
            onChange={(e) => onChange({ search: e.target.value })}
            placeholder="Search by SKU or product name..."
            className={`${field} w-full pl-9`}
          />
        </div>
        <div role="group" aria-label="View mode" className="flex shrink-0 overflow-hidden rounded-lg border border-gray-200">
          {(["table", "grid"] as const).map((mode) => (
            <button
              key={mode}
              type="button"
              aria-label={`${mode} view`}
              aria-pressed={view === mode}
              onClick={() => onViewChange(mode)}
              className={`px-3 py-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-600 ${
                view === mode ? "bg-indigo-50 text-indigo-600" : "bg-white text-gray-500 hover:bg-gray-50"
              }`}
            >
              {mode === "table" ? <List className="h-4 w-4" /> : <LayoutGrid className="h-4 w-4" />}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <select aria-label="Category" value={filters.category} onChange={(e) => onChange({ category: e.target.value })} className={field}>
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select aria-label="Status" value={filters.status} onChange={(e) => onChange({ status: e.target.value })} className={field}>
          <option value="">Any status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select aria-label="Stock level" value={filters.stockStatus} onChange={(e) => onChange({ stockStatus: e.target.value })} className={field}>
          <option value="">Any stock level</option>
          <option value="in_stock">In stock</option>
          <option value="low_stock">Low stock</option>
          <option value="out_of_stock">Out of stock</option>
        </select>
        <input type="number" min="0" aria-label="Minimum price" placeholder="Min $" value={filters.minPrice} onChange={(e) => onChange({ minPrice: e.target.value })} className={`${field} w-24`} />
        <input type="number" min="0" aria-label="Maximum price" placeholder="Max $" value={filters.maxPrice} onChange={(e) => onChange({ maxPrice: e.target.value })} className={`${field} w-24`} />
        <select aria-label="Sort by" value={filters.ordering} onChange={(e) => onChange({ ordering: e.target.value })} className={field}>
          <option value="-created_at">Newest first</option>
          <option value="name">Name A–Z</option>
          <option value="selling_price">Price: low to high</option>
          <option value="-selling_price">Price: high to low</option>
          <option value="stock">Stock: low to high</option>
        </select>
        {isFiltered && (
          <button type="button" onClick={() => onChange(EMPTY_FILTERS)} className="px-2 text-xs font-semibold text-indigo-600 hover:underline">
            Reset
          </button>
        )}
      </div>
    </div>
  );
}
