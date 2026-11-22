import { useEffect, useState, type FormEvent } from "react";
import Modal from "../../components/ui/Modal";
import { createInventory, listProductOptions } from "../../services/api/inventory";
import type { Branch, InventoryItem } from "../../types/inventory";
import type { Product } from "../../types/product";
import { fieldMessages } from "../../utils/errors";

interface Props {
  open: boolean;
  branches: Branch[];
  onClose: () => void;
  onCreated: (item: InventoryItem) => void;
}

const input = "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20";

function Form({ branches, onClose, onCreated }: Omit<Props, "open">) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loadError, setLoadError] = useState("");
  const [branch, setBranch] = useState(String((branches.find((b) => b.is_main_branch) ?? branches[0])?.id ?? ""));
  const [product, setProduct] = useState("");
  const [quantity, setQuantity] = useState("0");
  const [reorder, setReorder] = useState("10");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    listProductOptions().then(setProducts).catch((e: Error) => setLoadError(e.message));
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const found: Record<string, string> = {};
    if (!branch) found.branch = "Choose a branch.";
    if (!product) found.product = "Choose a product.";
    if (!/^\d+$/.test(quantity)) found.quantity = "Enter a whole number, 0 or more.";
    if (!/^\d+$/.test(reorder)) found.reorder_level = "Enter a whole number, 0 or more.";
    setErrors(found);
    if (Object.keys(found).length) return;

    setSubmitting(true);
    try {
      const item = await createInventory({ branch: Number(branch), product: Number(product), quantity: Number(quantity), reorder_level: Number(reorder) });
      onCreated(item);
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
      {loadError && <p role="alert" className="text-rose-600">Could not load products: {loadError}</p>}
      <div>
        <label htmlFor="add-branch" className="mb-1 block font-semibold text-gray-900">Branch</label>
        <select id="add-branch" value={branch} onChange={(e) => setBranch(e.target.value)} className={input}>
          {branches.map((b) => (
            <option key={b.id} value={b.id}>{b.code}: {b.name}</option>
          ))}
        </select>
        {error("branch")}
      </div>
      <div>
        <label htmlFor="add-product" className="mb-1 block font-semibold text-gray-900">Product</label>
        <select id="add-product" value={product} onChange={(e) => setProduct(e.target.value)} className={input}>
          <option value="">Select a product...</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
          ))}
        </select>
        {error("product")}
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor="add-qty" className="mb-1 block font-semibold text-gray-900">Opening quantity</label>
          <input id="add-qty" inputMode="numeric" value={quantity} onChange={(e) => setQuantity(e.target.value)} className={input} />
          {error("quantity")}
        </div>
        <div>
          <label htmlFor="add-reorder" className="mb-1 block font-semibold text-gray-900">Reorder level</label>
          <input id="add-reorder" inputMode="numeric" value={reorder} onChange={(e) => setReorder(e.target.value)} className={input} />
          {error("reorder_level")}
        </div>
      </div>
      <p className="text-[11px] text-gray-500">Opening stock above 0 is saved to the ledger as INITIAL_STOCK.</p>
      {error("form")}
      <div className="flex flex-col-reverse gap-2 pt-1 sm:flex-row sm:justify-end">
        <button type="button" onClick={onClose} className="rounded-xl border border-gray-200 px-4 py-2.5 font-semibold text-gray-700 hover:bg-gray-50">Cancel</button>
        <button type="submit" disabled={submitting} className="rounded-xl bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
          {submitting ? "Saving..." : "Create stock record"}
        </button>
      </div>
    </form>
  );
}

export default function AddInventoryModal(props: Props) {
  return (
    <Modal open={props.open} title="Add Inventory Record" onClose={props.onClose}>
      <Form branches={props.branches} onClose={props.onClose} onCreated={props.onCreated} />
    </Modal>
  );
}