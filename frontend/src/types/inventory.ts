import type { StockStatus } from "./product";

export type TransactionType =
  | "INITIAL_STOCK"
  | "PURCHASE"
  | "SALE"
  | "RETURN"
  | "ADJUSTMENT"
  | "DAMAGE"
  | "CORRECTION";

export interface Branch {
  id: number;
  code: string;
  name: string;
  is_main_branch: boolean;
}

export interface InventoryItem {
  id: number;
  branch: number;
  branch_code: string;
  branch_name: string;
  product: number;
  product_name: string;
  sku: string;
  unit: string;
  category_name: string;
  quantity: number;
  reorder_level: number;
  stock_status: StockStatus;
  unit_cost: string;
  inventory_value: string;
  updated_at: string;
}

export interface InventoryInput {
  branch: number;
  product: number;
  quantity: number;
  reorder_level: number;
}

export interface BranchSummary {
  id: number;
  code: string;
  name: string;
  units: number;
  skus: number;
  low_stock: number;
  out_of_stock: number;
}

export interface InventorySummary {
  total_inventory_value: string;
  total_products: number;
  total_units: number;
  low_stock: number;
  out_of_stock: number;
  branches: BranchSummary[];
}

export interface InventoryTransaction {
  id: number;
  created_at: string;
  inventory: number;
  product: number;
  product_name: string;
  sku: string;
  branch: number;
  branch_code: string;
  branch_name: string;
  transaction_type: TransactionType;
  quantity_change: number;
  quantity_before: number;
  quantity_after: number;
  reference_type: string;
  reference_id: string;
  reason: string;
  note: string;
  created_by_name: string;
}

export interface AdjustmentInput {
  inventory: number;
  transaction_type: TransactionType;
  quantity_change: number;
  reason: string;
  note: string;
}

export interface AdjustmentResult {
  transaction: InventoryTransaction;
  inventory: InventoryItem;
}

export interface StockFilters {
  search: string;
  branch: string;
  stockStatus: string;
  ordering: string;
}

export const EMPTY_STOCK_FILTERS: StockFilters = { search: "", branch: "", stockStatus: "", ordering: "-updated_at" };

export interface LedgerFilters {
  search: string;
  branch: string;
  type: string;
  dateFrom: string;
  dateTo: string;
  inventory: string;
}

export const EMPTY_LEDGER_FILTERS: LedgerFilters = { search: "", branch: "", type: "", dateFrom: "", dateTo: "", inventory: "" };

/** direction: "in" always adds stock, "out" always removes it, "either" lets the user choose. Mirrors the backend rules. */
export const TRANSACTION_TYPES: { value: TransactionType; label: string; direction: "in" | "out" | "either"; hint: string }[] = [
  { value: "PURCHASE", label: "Purchase (restock)", direction: "in", hint: "Stock received from a supplier." },
  { value: "RETURN", label: "Return", direction: "in", hint: "Stock returned by a customer." },
  { value: "INITIAL_STOCK", label: "Initial stock", direction: "in", hint: "Opening quantity counted for this branch." },
  { value: "SALE", label: "Sale", direction: "out", hint: "Stock sold outside the order flow." },
  { value: "DAMAGE", label: "Damage", direction: "out", hint: "Stock lost, broken or expired." },
  { value: "ADJUSTMENT", label: "Adjustment", direction: "either", hint: "A manual change after a stock count." },
  { value: "CORRECTION", label: "Correction", direction: "either", hint: "Fixes an earlier data-entry mistake." },
];