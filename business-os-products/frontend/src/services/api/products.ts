import type { Paginated, Product, ProductFilters, ProductInput, ProductSummary } from "../../types/product";
import { request } from "./client";

export const PAGE_SIZE = 10;

export function listProducts(filters: ProductFilters, page: number): Promise<Paginated<Product>> {
  const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE), ordering: filters.ordering });
  if (filters.search) params.set("search", filters.search);
  if (filters.category) params.set("category", filters.category);
  if (filters.status) params.set("status", filters.status);
  if (filters.stockStatus) params.set("stock_status", filters.stockStatus);
  if (filters.minPrice) params.set("min_price", filters.minPrice);
  if (filters.maxPrice) params.set("max_price", filters.maxPrice);
  return request(`/products/?${params}`);
}

export const getProduct = (id: string) => request<Product>(`/products/${id}/`);
export const getProductSummary = () => request<ProductSummary>("/products/summary/");

export const createProduct = (data: ProductInput) =>
  request<Product>("/products/", { method: "POST", body: JSON.stringify(data) });

export const updateProduct = (id: string, data: ProductInput) =>
  request<Product>(`/products/${id}/`, { method: "PATCH", body: JSON.stringify(data) });

export const deactivateProduct = (id: number) => request<void>(`/products/${id}/`, { method: "DELETE" });
