import { ArrowLeftRight, Plus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useToast } from "../components/ui/Toast";
import AddInventoryModal from "../features/products/AddInventoryModal";
import AdjustStockModal from "../features/products/AdjustStockModal";
import BranchCards from "../features/products/BranchCards";
import LedgerTab from "../features/products/LedgerTab";
import ReorderLevelModal from "../features/products/ReorderLevelModal";
import StockTab from "../features/products/StockTab";
import { getInventorySummary, listBranches } from "../services/api/inventory";
import { EMPTY_LEDGER_FILTERS, type Branch, type InventoryItem, type InventorySummary, type LedgerFilters } from "../types/inventory";
import { formatMoney, formatNumber } from "../utils/format";

type Tab = "stock" | "ledger";

export default function InventoryPage() {
  const toast = useToast();
  const [tab, setTab] = useState<Tab>("stock");
  const [branches, setBranches] = useState<Branch[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [ledgerFilters, setLedgerFilters] = useState<LedgerFilters>(EMPTY_LEDGER_FILTERS);
  const [focusLabel, setFocusLabel] = useState("");
  const [addOpen, setAddOpen] = useState(false);
  const [adjustOpen, setAdjustOpen] = useState(false);
  const [adjustTarget, setAdjustTarget] = useState<InventoryItem | null>(null);
  const [reorderTarget, setReorderTarget] = useState<InventoryItem | null>(null);

  useEffect(() => {
    listBranches().then(setBranches).catch(() => toast.error("Could not load branches."));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    getInventorySummary().then(setSummary).catch(() => setSummary(null));
  }, [reloadKey]);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  function openAdjust(item: InventoryItem | null) {
    setAdjustTarget(item);
    setAdjustOpen(true);
  }

  function showHistory(item: InventoryItem) {
    setLedgerFilters({ ...EMPTY_LEDGER_FILTERS, inventory: String(item.id) });
    setFocusLabel(`${item.product_name} at ${item.branch_code}`);
    setTab("ledger");
  }

  const kpis = [
    { label: "Total Inventory Value", value: summary ? formatMoney(summary.total_inventory_value) : "-", color: "text-gray-900" },
    { label: "Total Products", value: summary ? formatNumber(summary.total_products) : "-", color: "text-gray-900" },
    { label: "Low Stock", value: summary ? formatNumber(summary.low_stock) : "-", color: "text-amber-600" },
    { label: "Out of Stock", value: summary ? formatNumber(summary.out_of_stock) : "-", color: "text-rose-600" },
  ];

  const tabClass = (active: boolean) =>
    `border-b-2 px-1 pb-2.5 text-xs font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 ${
      active ? "border-indigo-600 text-indigo-600" : "border-transparent text-gray-500 hover:text-gray-900"
    }`;

  return (
    <>
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">Inventory &amp; Warehouses</h1>
          <p className="mt-0.5 text-xs text-gray-500">Stock by branch, and the ledger that records every change.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          <button type="button" onClick={() => setAddOpen(true)} className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2">
            <Plus className="h-4 w-4" />
            Add Inventory Record
          </button>
          <button type="button" onClick={() => openAdjust(null)} className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
            <ArrowLeftRight className="h-4 w-4" />
            Stock Adjustment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-xl border border-gray-200 bg-white p-4 shadow-xs">
            <div className="text-xs text-gray-500">{k.label}</div>
            <div className={`mt-1 text-xl font-bold ${k.color}`}>{k.value}</div>
          </div>
        ))}
      </div>

      <BranchCards branches={summary?.branches ?? []} />

      <section className="space-y-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-xs sm:p-6">
        <div role="tablist" aria-label="Inventory views" className="flex gap-6 border-b border-gray-100">
          <button type="button" role="tab" aria-selected={tab === "stock"} onClick={() => setTab("stock")} className={tabClass(tab === "stock")}>
            Stock Levels
          </button>
          <button type="button" role="tab" aria-selected={tab === "ledger"} onClick={() => setTab("ledger")} className={tabClass(tab === "ledger")}>
            Transaction Ledger
          </button>
        </div>

        {tab === "stock" ? (
          <StockTab branches={branches} reloadKey={reloadKey} onAdd={() => setAddOpen(true)} onAdjust={openAdjust} onReorder={setReorderTarget} onHistory={showHistory} />
        ) : (
          <LedgerTab branches={branches} reloadKey={reloadKey} filters={ledgerFilters} focusLabel={focusLabel} onFiltersChange={setLedgerFilters} />
        )}
      </section>

      <AddInventoryModal
        open={addOpen}
        branches={branches}
        onClose={() => setAddOpen(false)}
        onCreated={(item) => {
          setAddOpen(false);
          toast.success(`${item.product_name} added at ${item.branch_code}.`);
          refresh();
        }}
      />
      <AdjustStockModal
        open={adjustOpen}
        branches={branches}
        target={adjustTarget}
        onClose={() => setAdjustOpen(false)}
        onDone={({ transaction, inventory }) => {
          setAdjustOpen(false);
          toast.success(`${transaction.transaction_type} recorded. ${inventory.product_name} is now ${formatNumber(inventory.quantity)} at ${inventory.branch_code}.`);
          refresh();
        }}
      />
      <ReorderLevelModal
        item={reorderTarget}
        onClose={() => setReorderTarget(null)}
        onSaved={(item) => {
          setReorderTarget(null);
          toast.success(`Reorder level for ${item.product_name} is now ${item.reorder_level}.`);
          refresh();
        }}
      />
    </>
  );
}