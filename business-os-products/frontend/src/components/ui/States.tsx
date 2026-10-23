import { AlertTriangle, PackageOpen } from "lucide-react";
import type { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 py-14 text-center">
      <PackageOpen className="h-8 w-8 text-gray-300" />
      <h3 className="text-sm font-bold text-gray-900">{title}</h3>
      <p className="max-w-xs text-xs text-gray-500">{description}</p>
      {action}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center gap-2 py-14 text-center">
      <AlertTriangle className="h-8 w-8 text-rose-400" />
      <h3 className="text-sm font-bold text-gray-900">Couldn’t load data</h3>
      <p className="max-w-xs text-xs text-gray-500">{message}</p>
      <button type="button" onClick={onRetry} className="mt-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
        Try again
      </button>
    </div>
  );
}

export function SkeletonRows({ rows = 6 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-label="Loading" className="space-y-2 py-2">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="h-12 animate-pulse rounded-lg bg-gray-100" />
      ))}
    </div>
  );
}
