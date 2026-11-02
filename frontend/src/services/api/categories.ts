import type { Category, Paginated } from "../../types/product";
import { request } from "./client";

export async function listCategories(): Promise<Category[]> {
  const data = await request<Paginated<Category>>("/categories/?page_size=100");
  return data.results;
}
