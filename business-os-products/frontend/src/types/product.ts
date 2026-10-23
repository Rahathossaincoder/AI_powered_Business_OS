export type StockStatus = "in_stock" | "low_stock" | "out_of_stock";

export interface Product {
  id: number;
  sku: string;
  name: string;
  description: string;
  unit: string;
  category: number;
  category_name: string;
  cost_price: string;
  selling_price: string;
  reorder_level: number;
  stock: number;
  stock_status: StockStatus;
  image: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductInput {
  sku: string;
  name: string;
  description: string;
  unit: string;
  category: number;
  cost_price: string;
  selling_price: string;
  reorder_level: number;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
  is_active: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ProductSummary {
  total: number;
  in_stock: number;
  low_stock: number;
  out_of_stock: number;
}

export interface ProductFilters {
  search: string;
  category: string;
  status: string;
  stockStatus: string;
  minPrice: string;
  maxPrice: string;
  ordering: string;
}

export const EMPTY_FILTERS: ProductFilters = {
  search: "",
  category: "",
  status: "",
  stockStatus: "",
  minPrice: "",
  maxPrice: "",
  ordering: "-created_at",
};
