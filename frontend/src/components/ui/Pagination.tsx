import { ChevronLeft, ChevronRight } from "lucide-react";

interface Props {
  page: number;
  pageSize: number;
  count: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, pageSize, count, onChange }: Props) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  const from = count === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, count);
  const buttonClass =
    "inline-flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <nav aria-label="Pagination" className="flex flex-col items-center justify-between gap-3 pt-2 text-xs text-gray-500 sm:flex-row">
      <p>
        Showing {from}–{to} of {count}
      </p>
      <div className="flex items-center gap-2">
        <button type="button" aria-label="Previous page" disabled={page <= 1} onClick={() => onChange(page - 1)} className={buttonClass}>
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="font-medium text-gray-700">
          Page {page} of {totalPages}
        </span>
        <button type="button" aria-label="Next page" disabled={page >= totalPages} onClick={() => onChange(page + 1)} className={buttonClass}>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </nav>
  );
}
