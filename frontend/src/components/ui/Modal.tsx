import { X } from "lucide-react";
import { useEffect, type ReactNode } from "react";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  locked?: boolean;
  children: ReactNode;
}

export default function Modal({ open, title, onClose, locked = false, children }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && !locked && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, locked, onClose]);

  if (!open) return null;

  return (
    <div
      onMouseDown={(e) => e.target === e.currentTarget && !locked && onClose()}
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 sm:items-center"
    >
      <div role="dialog" aria-modal="true" aria-labelledby="modal-title" className="w-full max-w-lg space-y-4 rounded-2xl bg-white p-5 shadow-2xl sm:p-6">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <h2 id="modal-title" className="text-base font-bold text-gray-900">
            {title}
          </h2>
          <button type="button" aria-label="Close" onClick={onClose} disabled={locked} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 disabled:opacity-40">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}