import type { Paginated, Product } from "../../types/product";
import type {
  AdjustmentInput, AdjustmentResult, Branch, InventoryInput, InventoryItem, InventorySummary,
  InventoryTransaction, LedgerFilters, StockFilters,
} from "../../types/inventory";
import { request } from "./client";

export const INVENTORY_PAGE_SIZE = 10;

export function listInventory(filters: StockFilters, page: number, pageSize = INVENTORY_PAGE_SIZE): Promise<Paginated<InventoryItem>> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), ordering: filters.ordering });
  if (filters.search) params.set("search", filters.search);
  if (filters.branch) params.set("branch", filters.branch);
  if (filters.stockStatus) params.set("stock_status", filters.stockStatus);
  return request(`/inventory/?${params}`);
}

export const getInventorySummary = (branch = "") =>
  request<InventorySummary>(`/inventory/summary/${branch ? `?branch=${branch}` : ""}`);

export const createInventory = (data: InventoryInput) =>
  request<InventoryItem>("/inventory/", { method: "POST", body: JSON.stringify(data) });

export const updateReorderLevel = (id: number, reorder_level: number) =>
  request<InventoryItem>(`/inventory/${id}/`, { method: "PATCH", body: JSON.stringify({ reorder_level }) });

export const adjustStock = (data: AdjustmentInput) =>
  request<AdjustmentResult>("/inventory/adjust/", { method: "POST", body: JSON.stringify(data) });

export function listTransactions(filters: LedgerFilters, page: number): Promise<Paginated<InventoryTransaction>> {
  const params = new URLSearchParams({ page: String(page), page_size: String(INVENTORY_PAGE_SIZE) });
  if (filters.search) params.set("search", filters.search);
  if (filters.branch) params.set("branch", filters.branch);
  if (filters.type) params.set("transaction_type", filters.type);
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  if (filters.inventory) params.set("inventory", filters.inventory);
  return request(`/inventory-transactions/?${params}`);
}

export async function listBranches(): Promise<Branch[]> {
  const data = await request<Paginated<Branch>>("/branches/?page_size=100");
  return data.results;
}

export async function listProductOptions(): Promise<Product[]> {
  const data = await request<Paginated<Product>>("/products/?page_size=100&status=active&ordering=name");
  return data.results;
}