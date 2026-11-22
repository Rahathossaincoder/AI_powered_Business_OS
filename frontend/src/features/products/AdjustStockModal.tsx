import { useEffect, useState, type FormEvent } from "react";
import Modal from "../../components/ui/Modal";
import { adjustStock, listInventory } from "../../services/api/inventory";
import { EMPTY_STOCK_FILTERS, TRANSACTION_TYPES, type AdjustmentResult, type Branch, type InventoryItem, type TransactionType } from "../../types/inventory";
import { fieldMessages } from "../../utils/errors";
import { formatNumber } from "../../utils/format";

interface Props {
  open: boolean;
  branches: Branch[];
  target: InventoryItem | null;
  onClose: () => void;
  onDone: (result: AdjustmentResult) => void;
}

const input = "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20 disabled:bg-gray-50 disabled:text-gray-500";

function Form({ branches, target, onClose, onDone }: Omit<Props, "open">) {
  const [branch, setBranch] = useState(target ? String(target.branch) : String((branches.find((b) => b.is_main_branch) ?? branches[0])?.id ?? ""));
  const [options, setOptions] = useState<InventoryItem[]>([]);
  const [inventoryId, setInventoryId] = useState(target ? String(target.id) : "");
  const [type, setType] = useState<TransactionType>("PURCHASE");
  const [direction, setDirection] = useState<"increase" | "decrease">("increase");
  const [qty, setQty] = useState("");
  const [reason, setReason] = useState("");
  const [note, setNote] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (target || !branch) return;
    let ignore = false;
    listInventory({ ...EMPTY_STOCK_FILTERS, branch, ordering: "product__name" }, 1, 100)
      .then((page) => !ignore && setOptions(page.results))
      .catch(() => !ignore && setOptions([]));
    return () => {
      ignore = true;
    };
  }, [branch, target]);

  const selected = target ?? options.find((o) => String(o.id) === inventoryId) ?? null;
  const info = TRANSACTION_TYPES.find((t) => t.value === type)!;
  const sign = info.direction === "in" ? 1 : info.direction === "out" ? -1 : direction === "increase" ? 1 : -1;
  const amount = /^\d+$/.test(qty) ? Number(qty) : 0;
  const change = sign * amount;
  const after = selected ? selected.quantity + change : null;

  function set(name: string, apply: () => void) {
    apply();
    setErrors((current) => ({ ...current, [name]: "" }));
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    const found: Record<string, string> = {};
    if (!selected) found.inventory = "Choose the product to adjust.";
    if (amount <= 0) found.quantity_change = "Enter a whole number greater than 0.";
    else if (selected && after !== null && after < 0) found.quantity_change = `Not enough stock: only ${selected.quantity} available.`;
    if (!reason.trim()) found.reason = "Give a short reason.";
    else if (reason.trim().length > 100) found.reason = "Keep the reason under 100 characters.";
    if (!confirm) found.confirm = "Tick the box to confirm.";
    setErrors(found);
    if (Object.keys(found).length || !selected) return;

    setSubmitting(true);
    try {
      onDone(await adjustStock({ inventory: selected.id, transaction_type: type, quantity_change: change, reason: reason.trim(), note: note.trim() }));
    } catch (err) {
      const mapped = fieldMessages(err);
      setErrors(Object.keys(mapped).length ? mapped : { form: (err as Error).message });
    } finally {
      setSubmitting(false);
    }
  }

  const error = (name: string) => errors[name] && <p role="alert" className="mt-1 text-[11px] font-medium text-rose-600">{errors[name]}</p>;

  return (
    <form onSubmit={submit} noValidate className="space-y-4 text-xs">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor="adj-branch" className="mb-1 block font-semibold text-gray-900">Branch</label>
          <select id="adj-branch" disabled={!!target} value={branch} onChange={(e) => { setBranch(e.target.value); setInventoryId(""); setOptions([]); }} className={input}>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>{b.code}: {b.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="adj-product" className="mb-1 block font-semibold text-gray-900">Product</label>
          {target ? (
            <input id="adj-product" disabled value={`${target.product_name} (${target.sku})`} className={input} />
          ) : (
            <select id="adj-product" value={inventoryId} onChange={(e) => set("inventory", () => setInventoryId(e.target.value))} aria-invalid={!!errors.inventory} className={input}>
              <option value="">Select a product...</option>
              {options.map((o) => (
                <option key={o.id} value={o.id}>{o.product_name} ({o.sku})</option>
              ))}
            </select>
          )}
          {error("inventory")}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor="adj-type" className="mb-1 block font-semibold text-gray-900">Transaction type</label>
          <select id="adj-type" value={type} onChange={(e) => set("transaction_type", () => setType(e.target.value as TransactionType))} className={input}>
            {TRANSACTION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          {error("transaction_type")}
        </div>
        {info.direction === "either" ? (
          <div>
            <label htmlFor="adj-direction" className="mb-1 block font-semibold text-gray-900">Direction</label>
            <select id="adj-direction" value={direction} onChange={(e) => setDirection(e.target.value as "increase" | "decrease")} className={input}>
              <option value="increase">Increase stock (+)</option>
              <option value="decrease">Decrease stock (-)</option>
            </select>
          </div>
        ) : (
          <div>
            <span className="mb-1 block font-semibold text-gray-900">Direction</span>
            <p className="rounded-lg bg-gray-50 px-3 py-2 text-gray-600">{info.direction === "in" ? "Adds stock (+)" : "Removes stock (-)"}</p>
          </div>
        )}
      </div>
      <p className="-mt-2 text-[11px] text-gray-500">{info.hint}</p>

      <div>
        <label htmlFor="adj-qty" className="mb-1 block font-semibold text-gray-900">Quantity</label>
        <input id="adj-qty" inputMode="numeric" value={qty} onChange={(e) => set("quantity_change", () => setQty(e.target.value))} placeholder="e.g. 10" aria-invalid={!!errors.quantity_change} className={input} />
        {error("quantity_change")}
        {selected && amount > 0 && after !== null && (
          <p className={`mt-1.5 text-[11px] font-semibold ${after < 0 ? "text-rose-600" : "text-gray-600"}`}>
            Stock will change from {formatNumber(selected.quantity)} to {formatNumber(after)} ({change > 0 ? "+" : ""}{formatNumber(change)}).
          </p>
        )}
      </div>

      <div>
        <label htmlFor="adj-reason" className="mb-1 block font-semibold text-gray-900">Reason</label>
        <input id="adj-reason" value={reason} onChange={(e) => set("reason", () => setReason(e.target.value))} maxLength={100} placeholder="e.g. Shipment received from central supplier" aria-invalid={!!errors.reason} className={input} />
        {error("reason")}
      </div>
      <div>
        <label htmlFor="adj-note" className="mb-1 block font-semibold text-gray-900">Note (optional)</label>
        <textarea id="adj-note" rows={2} value={note} onChange={(e) => setNote(e.target.value)} className={input} />
      </div>

      <label className="flex cursor-pointer items-start gap-2 text-gray-700">
        <input type="checkbox" checked={confirm} onChange={(e) => set("confirm", () => setConfirm(e.target.checked))} className="mt-0.5 h-4 w-4 accent-indigo-600" />
        I confirm this changes stock and will be saved permanently in the ledger.
      </label>
      {error("confirm")}
      {error("form")}

      <div className="flex flex-col-reverse gap-2 pt-1 sm:flex-row sm:justify-end">
        <button type="button" onClick={onClose} className="rounded-xl border border-gray-200 px-4 py-2.5 font-semibold text-gray-700 hover:bg-gray-50">Cancel</button>
        <button type="submit" disabled={submitting} className="rounded-xl bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
          {submitting ? "Recording..." : "Record transaction"}
        </button>
      </div>
    </form>
  );
}

export default function AdjustStockModal(props: Props) {
  return (
    <Modal open={props.open} title="Stock Adjustment" onClose={props.onClose}>
      <Form branches={props.branches} target={props.target} onClose={props.onClose} onDone={props.onDone} />
    </Modal>
  );
}