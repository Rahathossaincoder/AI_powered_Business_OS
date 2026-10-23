import { useState, type FormEvent, type ReactNode } from "react";
import type { Category, Product, ProductInput } from "../../types/product";

type Errors = Partial<Record<keyof ProductInput, string>>;

interface Props {
  initial?: Product;
  categories: Category[];
  serverErrors: Errors;
  submitting: boolean;
  submitLabel: string;
  onSubmit: (data: ProductInput) => void;
  onCancel: (dirty: boolean) => void;
}

const inputClass = "w-full rounded-lg border border-gray-200 px-3 py-2 text-xs focus:border-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600/20";

function Field({ label, htmlFor, error, children }: { label: string; htmlFor: string; error?: string; children: ReactNode }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="mb-1 block font-semibold text-gray-900">
        {label}
      </label>
      {children}
      {error && (
        <p id={`${htmlFor}-error`} role="alert" className="mt-1 text-[11px] font-medium text-rose-600">
          {error}
        </p>
      )}
    </div>
  );
}

function validate(v: ProductInput): Errors {
  const errors: Errors = {};
  if (!v.name.trim()) errors.name = "Product name is required.";
  if (!v.sku.trim()) errors.sku = "SKU is required.";
  if (!v.category) errors.category = "Choose a category.";
  if (v.cost_price === "" || Number(v.cost_price) < 0) errors.cost_price = "Enter a cost price of 0 or more.";
  if (v.selling_price === "" || Number(v.selling_price) < 0) errors.selling_price = "Enter a selling price of 0 or more.";
  if (!Number.isInteger(v.reorder_level) || v.reorder_level < 0) errors.reorder_level = "Reorder level must be a whole number, 0 or more.";
  return errors;
}

export default function ProductForm({ initial, categories, serverErrors, submitting, submitLabel, onSubmit, onCancel }: Props) {
  const [values, setValues] = useState<ProductInput>({
    sku: initial?.sku ?? "",
    name: initial?.name ?? "",
    description: initial?.description ?? "",
    unit: initial?.unit ?? "pcs",
    category: initial?.category ?? 0,
    cost_price: initial?.cost_price ?? "",
    selling_price: initial?.selling_price ?? "",
    reorder_level: initial?.reorder_level ?? 0,
    is_active: initial?.is_active ?? true,
  });
  const [clientErrors, setClientErrors] = useState<Errors>({});
  const [dirty, setDirty] = useState(false);
  const errors: Errors = { ...serverErrors, ...clientErrors };

  function set<K extends keyof ProductInput>(key: K, value: ProductInput[K]) {
    setValues((current) => ({ ...current, [key]: value }));
    setClientErrors((current) => ({ ...current, [key]: undefined }));
    setDirty(true);
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const found = validate(values);
    setClientErrors(found);
    if (Object.keys(found).length === 0) onSubmit({ ...values, sku: values.sku.trim(), name: values.name.trim() });
  }

  const describe = (id: string, error?: string) => ({ id, "aria-invalid": !!error, "aria-describedby": error ? `${id}-error` : undefined });

  return (
    <form onSubmit={handleSubmit} noValidate className="max-w-2xl space-y-5 rounded-2xl border border-gray-200 bg-white p-4 text-xs shadow-xs sm:p-6">
      <Field label="Product Title" htmlFor="name" error={errors.name}>
        <input {...describe("name", errors.name)} value={values.name} onChange={(e) => set("name", e.target.value)} placeholder="e.g. High-Density Router X5" className={inputClass} />
      </Field>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="SKU Code" htmlFor="sku" error={errors.sku}>
          <input {...describe("sku", errors.sku)} value={values.sku} onChange={(e) => set("sku", e.target.value)} placeholder="SKU-5020-X" className={`${inputClass} font-mono uppercase`} />
        </Field>
        <Field label="Category" htmlFor="category" error={errors.category}>
          <select {...describe("category", errors.category)} value={values.category} onChange={(e) => set("category", Number(e.target.value))} className={`${inputClass} bg-white`}>
            <option value={0}>Select a category…</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </Field>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Cost Price ($)" htmlFor="cost_price" error={errors.cost_price}>
          <input {...describe("cost_price", errors.cost_price)} type="number" step="0.01" min="0" value={values.cost_price} onChange={(e) => set("cost_price", e.target.value)} placeholder="150.00" className={inputClass} />
        </Field>
        <Field label="Selling Price ($)" htmlFor="selling_price" error={errors.selling_price}>
          <input {...describe("selling_price", errors.selling_price)} type="number" step="0.01" min="0" value={values.selling_price} onChange={(e) => set("selling_price", e.target.value)} placeholder="299.00" className={inputClass} />
        </Field>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Unit" htmlFor="unit" error={errors.unit}>
          <input {...describe("unit", errors.unit)} value={values.unit} onChange={(e) => set("unit", e.target.value)} placeholder="pcs" className={inputClass} />
        </Field>
        <Field label="Reorder Level" htmlFor="reorder_level" error={errors.reorder_level}>
          <input {...describe("reorder_level", errors.reorder_level)} type="number" min="0" step="1" value={values.reorder_level} onChange={(e) => set("reorder_level", Number(e.target.value))} className={inputClass} />
        </Field>
      </div>

      <Field label="Description" htmlFor="description" error={errors.description}>
        <textarea {...describe("description", errors.description)} rows={3} value={values.description} onChange={(e) => set("description", e.target.value)} className={inputClass} />
      </Field>

      <label className="flex cursor-pointer items-center gap-2 font-medium text-gray-700">
        <input type="checkbox" checked={values.is_active} onChange={(e) => set("is_active", e.target.checked)} className="h-4 w-4 accent-indigo-600" />
        Active (available for sale)
      </label>

      <div className="flex flex-col-reverse gap-2 border-t border-gray-100 pt-4 sm:flex-row sm:justify-end">
        <button type="button" onClick={() => onCancel(dirty)} className="rounded-xl border border-gray-200 px-4 py-2.5 font-semibold text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
          Cancel
        </button>
        <button type="submit" disabled={submitting} className="rounded-xl bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 disabled:opacity-60">
          {submitting ? "Saving…" : submitLabel}
        </button>
      </div>
    </form>
  );
}
