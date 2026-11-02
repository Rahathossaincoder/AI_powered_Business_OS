import { useEffect } from "react";

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  busy?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({ open, title, message, confirmLabel, busy = false, onConfirm, onCancel }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div role="dialog" aria-modal="true" aria-labelledby="confirm-title" className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-6 shadow-2xl">
        <h2 id="confirm-title" className="text-base font-bold text-gray-900">
          {title}
        </h2>
        <p className="text-xs text-gray-600">{message}</p>
        <div className="flex justify-end gap-2 text-xs font-semibold">
          <button type="button" onClick={onCancel} className="rounded-lg border border-gray-200 px-3 py-2 text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
            Cancel
          </button>
          <button type="button" disabled={busy} onClick={onConfirm} className="rounded-lg bg-rose-600 px-3 py-2 text-white hover:bg-rose-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-600 disabled:opacity-60">
            {busy ? "Working…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
