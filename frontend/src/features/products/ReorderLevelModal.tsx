import { useState, type FormEvent } from "react";
import Modal from "../../components/ui/Modal";
import { updateReorderLevel } from "../../services/api/inventory";
import type { InventoryItem } from "../../types/inventory";
import { fieldMessages } from "../../utils/errors";

interface Props {
  item: InventoryItem | null;
  onClose: () => void;
  onSaved: (item: InventoryItem) => void;
}

function Form({ item, onClose, onSaved }: { item: InventoryItem; onClose: () => void; onSaved: (item: InventoryItem) => void }) {
  const [value, setValue] = useState(String(item.reorder_level));
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!/^\d+$/.test(value)) return setError("Enter a whole number, 0 or more.");
    setSaving(true);
    try {
      onSaved(await updateReorderLevel(item.id, Number(value)));
    } catch (err) {
      setError(fieldMessages(err).reorder_level ?? (err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} noValidate className="space-y-4 text-xs">
      <p className="text-gray-600">
        <span className="font-bold text-gray-900">{item.product_name}</span> at {item.branch_code}. Current stock: {item.quantity}.
        The item shows as Low Stock when quantity is at or below this level.
      </p>
      <div>
        <label htmlFor="reorder-level" className="mb-1 block font-semibold text-gray-900">Reorder level</label>
        <input id="reorder-level" inputMode="numeric" value={value} onChange={(e) => { setValue(e.target.value); setError(""); }} aria-invalid={!!error} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-xs focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20" />
        {error && <p role="alert" className="mt-1 text-[11px] font-medium text-rose-600">{error}</p>}
      </div>
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <button type="button" onClick={onClose} className="rounded-xl border border-gray-200 px-4 py-2.5 font-semibold text-gray-700 hover:bg-gray-50">Cancel</button>
        <button type="submit" disabled={saving} className="rounded-xl bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">{saving ? "Saving..." : "Save reorder level"}</button>
      </div>
    </form>
  );
}

export default function ReorderLevelModal({ item, onClose, onSaved }: Props) {
  return (
    <Modal open={item !== null} title="Change Reorder Level" onClose={onClose}>
      {item && <Form key={item.id} item={item} onClose={onClose} onSaved={onSaved} />}
    </Modal>
  );
}