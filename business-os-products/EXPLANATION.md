# Products Catalog — setup and line-by-line explanation

Stack: Django + Django REST Framework (backend), React + TypeScript + Vite + Tailwind CSS (frontend).
Line numbers below refer to the files exactly as delivered in this folder.

---

## 0. What I checked in your uploads

- `db.sqlite3`: `categories` and `products` tables already exist, so `catalog/models.py` mirrors those columns exactly (same names, same unique constraints). `inventory` has a `quantity` per branch and product; stock is summed from there.
- `products.html`: the page layout, stat cards, table columns, search/category filter, and the add-product modal were used as the visual spec.
- `business_os_database_er_documentation.txt`: followed these rules: tenant isolation by `organization_id`, backend decides the tenant, `UNIQUE(organization_id, sku)`, stock is not stored on Product.
- `business-os-tailwind-codex-commands.txt` (Command 06 and 25): products list with search, category/status/price filters, grid/table toggle, pagination; detail page; create/edit with validation, error states, success toast, cancel confirmation; endpoints `GET/POST /api/products/`, `GET/PATCH/DELETE /api/products/:id/`, `GET /api/categories/`. Tailwind-only styling, no UI library.

## 1. How the pieces connect (read this first)

```
Browser (React)                         Django
ProductsPage  ->  services/api/products.ts  ->  GET /api/products/?search=..&page=2
                                                   |
                                         catalog/urls.py (router)
                                                   |
                                         catalog/views.py ProductViewSet
                                           - tenant.py finds the user's organization
                                           - base_queryset(): only that org's products + stock total
                                           - get_queryset(): applies filters from the URL
                                                   |
                                         catalog/serializers.py ProductSerializer
                                           - turns rows into JSON (and validates incoming JSON)
                                                   |
                                         catalog/models.py -> products / categories / inventory tables
```

Three rules the backend enforces that the frontend can never override:
1. The organization always comes from the logged-in user's Employee record, never from the request body.
2. SKU is unique per organization and is stored upper-case.
3. A product can only use a category from the same organization.

## 2. Setup

### Backend (add to your existing Django project)
1. `pip install djangorestframework django-cors-headers`
2. Copy `backend/catalog/{serializers,views,urls,tenant,pagination,admin,tests}.py` into your existing `catalog/` app.
   `models.py` is included for reference. Your repo already has catalog models and migrations, so compare first and keep yours if the fields match.
3. Merge `backend/settings_snippet.py` into your `settings.py` (apps, middleware, CORS, REST_FRAMEWORK).
4. In your root `urls.py` add `path("api/", include("catalog.urls"))`.
5. Check two assumptions I could not verify (I only had your database, not your Python code):
   - `tenant.py` line 7: `apps.get_model("users", "Employee")`. Change `"users"` if Employee lives in another app.
   - `views.py` line 8 and 39–41: `from inventory.models import Inventory`, with a `product` foreign key and a `quantity` field.
6. Run `python manage.py makemigrations --check`. If it asks for changes, adjust models to match your existing migration rather than creating a new one.
7. Create an Organization, a User, an Employee linking them, and a few Categories (Django admin works).
8. `python manage.py test catalog` (the tests assume your Employee has `organization` and `user` fields).

### Frontend
1. `cd frontend && npm install`
2. Copy `.env.example` to `.env.local` and set `VITE_DEV_BASIC_AUTH=youremail@x.com:yourpassword` for local testing only. Remove it once the login teammate's token flow is in (the client already sends `Bearer <access_token>` from `localStorage` when present).
3. Start Django (`python manage.py runserver`), then `npm run dev`, then open http://localhost:5173/products. Vite proxies `/api` to Django, so no CORS problems in dev.

## 3. What was verified, and what was not

Verified:
- 11 backend tests pass: create, SKU uppercasing and uniqueness, cross-tenant category rejected, client-supplied `organization` ignored, negative price rejected, stock status and summary counts, search/price/stock filters, tenant isolation (other org's product returns 404), update, soft delete, login required, categories.
- A live HTTP check with curl (Basic auth) created and listed a product.
- `npm run build` (TypeScript strict + Vite production build) succeeds.

Not verified:
- The tests ran against stand-in `core`, `users`, `inventory` apps that I wrote to match your table names, not your real ones.
- I did not open the UI in a browser.

Deliberately left out of update 1 (depends on other modules or your decision):
- Image upload (the `image` column is exposed but the form has no upload field).
- Product detail "sales summary", "recent inventory transactions", "recent orders" (need Orders/Inventory endpoints from teammates).
- Permission checks (`products.create` etc.). Right now any logged-in employee of the organization can use the API.
- Audit log entries on create/update/deactivate.
- Currency is hard-coded USD in `utils/format.ts`.
- `DELETE` deactivates (`is_active = False`) instead of deleting the row, so order history and inventory ledger stay intact.

---

## 4. Backend, line by line

### `catalog/models.py`
| Lines | What they do |
|---|---|
| 1 | Import Django's `models` module. |
| 4 | `Category` class = one table (`categories`). Each attribute is a column. |
| 5 | Primary key named `category_id` (matches your DB column; Django would otherwise create `id`). |
| 6–8 | `organization`: foreign key to Organization. `CASCADE` = deleting an organization deletes its categories. `related_name="categories"` lets you write `org.categories.all()`. |
| 9–11 | `parent`: foreign key to the same table (`"self"`) for nested categories. `null/blank` = a top-level category has no parent. `SET_NULL` = deleting a parent makes children top-level instead of deleting them. |
| 12–13 | `name` text (max 150) and `slug` (URL-safe version of the name). |
| 14 | `description`, `blank=True` so it can be empty. |
| 15 | `image` stores a path/URL, nullable (matches your column). |
| 16 | `is_active` defaults to True. |
| 17–18 | `created_at` set once on insert (`auto_now_add`), `updated_at` refreshed on every save (`auto_now`). |
| 20–26 | `Meta`: `db_table` pins the real table name; `UniqueConstraint(organization, slug)` = a slug can repeat across organizations but not inside one. The constraint name matches your existing DB. |
| 28–29 | `__str__`: text shown in Django admin and the shell. |
| 32 | `Product` class (`products` table). |
| 33 | Primary key `product_id`. |
| 34–36 | `organization` foreign key (tenant owner). |
| 37 | `category` foreign key. `PROTECT` = you cannot delete a category that still has products. |
| 38–40 | `sku` (max 100), `name` (max 255), `description`. |
| 41 | `unit` with default `"pcs"`. |
| 42–43 | `cost_price`, `selling_price`: `DecimalField` (12 digits, 2 after the point). Money must be Decimal, never float. |
| 44 | `reorder_level`: whole number ≥ 0; below this the product counts as low stock. |
| 45–48 | `image`, `is_active`, timestamps (same as Category). |
| 50–56 | `Meta`: table name and `UNIQUE(organization, sku)` from the ER document. |
| 58–59 | `__str__` returns e.g. `SKU-8841-A - Quantum Edge AI Server v4`. |

There is intentionally no `stock` column: per the ER document, stock lives in Inventory.

### `catalog/tenant.py`
| Lines | What they do |
|---|---|
| 1 | `apps` lets us look up a model by name string, which avoids importing Employee directly. |
| 2 | `PermissionDenied` = DRF exception that becomes HTTP 403. |
| 5–6 | Function that answers "which organization is this request for?" Docstring states the rule. |
| 7 | Loads the `Employee` model from the `users` app. |
| 8–10 | Finds the Employee row linked to the logged-in user (`request.user`); `select_related("organization")` fetches the organization in the same query; `.first()` returns it or `None`. |
| 11–12 | No employee record means the account has no organization, so return 403. |
| 13 | Return the organization object. |
| 16–17 | Mixin class (reusable behavior added to any ViewSet). |
| 19–23 | `organization` property: looks it up once per request and caches it on `self._organization`, so we hit the database once, not on every use. |
| 25–28 | Adds the organization to the serializer's `context`, so serializer validation can check "does this category belong to my organization?". |

### `catalog/pagination.py`
| Lines | What they do |
|---|---|
| 1 | Import DRF's page-number pagination. |
| 4 | Our subclass. |
| 5 | Default 10 items per page. |
| 6 | Lets the client pass `?page_size=100` (the category dropdown uses this). |
| 7 | Hard cap of 100 so nobody can request 1,000,000 rows. |

### `catalog/serializers.py`
A serializer converts model rows to JSON and validates incoming JSON.

| Lines | What they do |
|---|---|
| 1 | `slugify` turns "Soft Drinks" into `soft-drinks`. |
| 2 | DRF serializers module. |
| 4 | Import our models. |
| 7 | `CategorySerializer`, built from the Category model. |
| 8 | Exposes `pk` to the frontend as `id` (our PK is called `category_id`). Read-only. |
| 9 | `slug` is optional on input; we generate it from the name when missing. |
| 11–14 | `Meta`: which model, which fields appear in JSON, and which are never accepted from the client (timestamps). |
| 16–22 | `validate_parent` runs automatically for the `parent` field. Rejects a parent from another organization (line 18–19) and a category being its own parent (20–21), else returns it. |
| 24–34 | `validate` runs after all fields pass. Line 25 gets the organization. 26 gets the name (new value, or the existing one on update). 27 picks the slug: given slug, else existing slug, else generated from name. 28–30 look for another category in this organization with the same slug, excluding itself when editing. 31–32 if found, return a 400 error attached to the `name` field. 33 stores the final slug. 34 returns the cleaned data. |
| 37 | `ProductSerializer`. |
| 38 | `id` alias for `product_id`. |
| 39 | `category_name`: reads `category.name` so the table can show the name without a second request. |
| 40–41 | `stock` and `stock_status` are read-only. They are not model columns; the view adds them with a database annotation. |
| 42–43 | Redeclare the two price fields with `min_value=0`, so negative prices are rejected with a clear error. |
| 45–54 | `Meta`: model, the JSON fields in order, and read-only timestamps. `category` here is the category ID that the form sends. |
| 56–63 | `validate_sku`: 57 trims spaces and uppercases (so `sku-1` and `SKU-1` cannot both exist). 58 looks for the same SKU in this organization. 59–60 excludes the product being edited. 61–62 raises "SKU already exists". 63 returns the cleaned SKU. |
| 65–68 | `validate_category`: blocks using another organization's category (prevents cross-tenant data leaks through a guessed ID). |

### `catalog/views.py`
| Lines | What they do |
|---|---|
| 1 | ORM tools: `Case/When` (if/else in SQL), `Count`, `F` (refer to another column), `IntegerField`, `OuterRef` + `Subquery` (query inside a query), `Q` (conditions), `Sum`, `Value` (constant). |
| 2 | `Coalesce(x, 0)`: use 0 when x is NULL (a product with no inventory row). |
| 3–6 | DRF: `viewsets`, `@action` for custom endpoints, search/ordering filters, `Response`. |
| 8 | Import the Inventory model to read stock. |
| 10–13 | Our own models, pagination, serializers, tenant mixin. |
| 16 | `CategoryViewSet`: gives list/create/retrieve/update/delete for categories from one class. |
| 17–20 | Which serializer, pagination class, search filter, and that `?search=` looks at `name`. |
| 22–23 | `get_queryset` = which rows this endpoint may touch: only this organization's categories, sorted by name. This is the tenant isolation. |
| 25–26 | On create, the organization is set by the backend. |
| 29 | `ProductViewSet`: full CRUD for products. |
| 30–31 | Serializer and pagination. |
| 32–33 | Enables `?search=` (matches name or SKU, case-insensitive) and `?ordering=`. |
| 34 | Which columns the client may sort by. |
| 35 | Default sort: newest first. |
| 37 | `base_queryset`: every product of this organization plus computed stock. Used by list, detail, summary, and the post-save reload. |
| 38–43 | Subquery: for the outer product, sum `quantity` over all its Inventory rows (all branches). |
| 44–46 | Start from this organization's products and join the category in one query (`select_related`, avoids one extra query per row). |
| 47 | Adds `stock` = that sum, or 0 if none. |
| 48–54 | Adds `stock_status`: stock ≤ 0 means `out_of_stock`; stock ≤ the product's `reorder_level` means `low_stock`; otherwise `in_stock`. Computed in SQL so we can filter and count by it. |
| 57–59 | `get_queryset` (used by list/detail): start from the base, read URL parameters. |
| 60–61 | `?category=3` filter. |
| 62–65 | `?status=active` / `inactive`. |
| 66–67 | `?stock_status=low_stock`. |
| 68–71 | `?min_price=` / `?max_price=` on selling price. |
| 72 | Return the filtered rows. Search, ordering and pagination are then applied by DRF. |
| 74–75 | After saving, re-fetch the product through `base_queryset` so the response includes `stock` and `stock_status`. |
| 77–79 | Create: `save(organization=...)` injects the tenant (overrides anything the client sent), then reload. |
| 81–83 | Update: save, then reload. |
| 85–87 | Delete: instead of removing the row, set `is_active = False`. `update_fields` writes only those columns. |
| 89–98 | `@action(detail=False)` adds `GET /api/products/summary/`: one query returning total / in-stock / low-stock / out-of-stock counts for the four stat cards. |

### `catalog/urls.py`
| Lines | What they do |
|---|---|
| 1 | DRF router: auto-generates the URLs. |
| 3 | Import the viewsets. |
| 5 | Create the router. |
| 6–7 | Register `products` and `categories`. This creates `GET/POST /products/`, `GET/PUT/PATCH/DELETE /products/<id>/`, `GET /products/summary/`, and the same for categories. `basename` is the internal URL name prefix. |
| 9 | Expose the URL list; your root `urls.py` mounts it under `api/`. |

### `catalog/admin.py`
Lines 6–9 and 12–16 register Category and Product in Django admin with list columns (`list_display`), side filters (`list_filter`) and a search box (`search_fields`), useful for seeding data.

### `pagination` of results in JSON
A list response looks like `{"count": 42, "next": ..., "previous": ..., "results": [ ... ]}`. The frontend type `Paginated<T>` mirrors that shape.

---

## 5. Frontend, line by line

Quick React vocabulary used below:
- Component: a function that returns JSX (HTML-like markup).
- Props: the function's inputs.
- `useState`: remembers a value between renders; calling the setter re-renders.
- `useEffect`: runs code after render (here: fetch data) and re-runs when its dependency list changes.
- Controlled input: `value` comes from state and `onChange` updates it.

### `index.html`
| Lines | What they do |
|---|---|
| 1–7 | Standard HTML head; line 5 makes the page responsive on phones; line 6 sets the tab title. |
| 8 | Page background and text colour via Tailwind classes. |
| 9 | Empty `div#root`: React mounts the whole app here. |
| 10 | Loads `main.tsx` as an ES module. |

### `vite.config.ts`
| Lines | What they do |
|---|---|
| 1–3 | Import the Tailwind plugin, React plugin, and `defineConfig`. |
| 5–10 | Export config. 6: enable React and Tailwind. 7–9: in dev, any request starting with `/api` is forwarded to Django on port 8000, so the browser sees one origin. |

### `src/main.tsx`
| Lines | What they do |
|---|---|
| 1–6 | Imports: React strict mode, the DOM renderer, the router, the app, the toast provider, and `index.css` (which only contains the Tailwind import). |
| 8 | Find `#root` and render into it. |
| 9 | `StrictMode` warns about unsafe patterns in development. |
| 10 | `BrowserRouter` enables URL-based pages. |
| 11–13 | `ToastProvider` wraps the app so any page can show toasts. |

### `src/index.css`
One line, `@import "tailwindcss";`, which turns on Tailwind. No custom CSS.

### `src/App.tsx`
| Lines | What they do |
|---|---|
| 1–5 | Imports. |
| 7 | App component. |
| 9 | `Routes` picks the first route matching the URL. |
| 10 | A parent route that renders `AppLayout` (sidebar) around every child page. |
| 11 | `/` redirects to `/products`. |
| 12–15 | The four product URLs from your command file: list, new, detail (`:id` is a URL parameter), edit. |
| 16 | Anything else shows "Page not found". |

### `src/types/product.ts`
TypeScript shapes so the compiler catches typos.
| Lines | What they do |
|---|---|
| 1 | The three stock states. |
| 3–20 | `Product`: exactly what the API returns. Prices are `string` because DRF sends decimals as strings (`"3499.00"`), which avoids float rounding. |
| 22–32 | `ProductInput`: what the form sends (no id, stock or timestamps). |
| 34–40 | `Category`. |
| 42–47 | `Paginated<T>`: generic wrapper for any paginated list. |
| 49–54 | `ProductSummary`: the four stat-card numbers. |
| 56–64 | `ProductFilters`: all filter/sort values held on the page (strings, because inputs give strings). |
| 66–74 | `EMPTY_FILTERS`: default values; also used to detect "are any filters active?". |

### `src/services/api/client.ts`
| Lines | What they do |
|---|---|
| 1–10 | `ApiError`: an Error that also carries the HTTP `status` and per-field messages from Django, so forms can show them. |
| 12–18 | `authHeaders`: sends `Bearer <token>` if the login flow stored one; otherwise a dev-only Basic header from `VITE_DEV_BASIC_AUTH`; otherwise nothing. |
| 20 | `request<T>`: the single place every API call goes through. |
| 21–24 | Calls `fetch` on `/api<path>`, sets JSON content type, merges auth and any custom headers. |
| 26 | `204 No Content` (delete) has no body, so return early. |
| 28 | Parse JSON; if the body is not JSON, `null`. |
| 29–33 | On failure: for HTTP 400, DRF's field error object becomes `fieldErrors`; `detail` becomes the message; throw `ApiError`. |
| 34 | Success: return the data. |

### `src/services/api/products.ts`
| Lines | What they do |
|---|---|
| 1–2 | Imports types and `request`. |
| 4 | Page size used by both the API call and the pagination component. |
| 6–15 | `listProducts`: builds the query string. 7 always sends page, page size, ordering. 8–13 add each filter only if it has a value. 14 calls `GET /api/products/?...`. |
| 17 | Get one product by id. |
| 18 | Get the stat-card counts. |
| 20–21 | Create: POST with the form data as JSON. |
| 23–24 | Update: PATCH with the form data. |
| 26 | Deactivate: DELETE. |

### `src/services/api/categories.ts`
Lines 4–7: fetch up to 100 categories and return just the `results` array (used by the filter dropdown and the form's category select).

### `src/hooks/useDebounce.ts`
| Lines | What they do |
|---|---|
| 3 | Generic hook: takes a value and a delay (default 400 ms). |
| 4 | Holds the delayed copy of the value. |
| 6–9 | Each time the value changes, start a timer that updates the delayed copy. The returned function (line 8) cancels the previous timer, so only the last keystroke triggers the update. |
| 11 | Return the delayed value. This stops a request on every keystroke. |

### `src/utils/format.ts`
Lines 1–3 format a number or numeric string as USD currency; lines 5–7 format an ISO date like `Oct 17, 2026`.

### `src/components/ui/Toast.tsx`
| Lines | What they do |
|---|---|
| 1–2 | Imports icons and React context tools. |
| 4–13 | Types for one toast and for the API (`success`, `error`). |
| 15 | Creates a context: a way to share a value with every child component without passing props. |
| 17–18 | Provider component; state holds the visible toasts. |
| 20–24 | `push`: makes a unique id (21), appends the toast (22), removes it after 4 seconds (23). `useCallback` keeps the function stable. |
| 26–29 | The `api` object other components get. |
| 31–47 | Renders children plus a fixed bottom-right stack. `aria-live="polite"` makes screen readers announce new toasts. Lines 35–45 render each toast; the colour depends on type (38–40) and the icon too (42). |
| 51–55 | `useToast()`: hook components call to get the API; throws a clear error if used outside the provider. |

### `src/components/ui/Pagination.tsx`
| Lines | What they do |
|---|---|
| 3–8 | Props: current page, page size, total count, change callback. |
| 11 | Total pages (at least 1). |
| 12–13 | "Showing from–to": e.g. 11–20. |
| 14–15 | Shared Tailwind classes for the two arrow buttons. |
| 17–34 | `nav` with the text (19–21) and Previous (23–25) / Next (29–31) buttons. Each button is disabled at the ends and has an `aria-label` for screen readers. |

### `src/components/ui/StockBadge.tsx`
| Lines | What they do |
|---|---|
| 3–7 | Colour classes per status (green / amber / red). |
| 9 | Component takes status and stock number. |
| 10 | Label: "Out of stock", "3 left", or "142 in stock". |
| 11 | Renders the coloured pill. |

### `src/components/ui/ConfirmDialog.tsx`
| Lines | What they do |
|---|---|
| 3–11 | Props: open flag, texts, busy flag, confirm/cancel handlers. |
| 14–19 | While open, listen for the Escape key to cancel; remove the listener when closed. |
| 21 | Render nothing when closed. |
| 24 | Dark full-screen overlay, content centred. |
| 25 | `role="dialog" aria-modal` + `aria-labelledby` = accessible dialog. |
| 26–29 | Title and message. |
| 31–33 | Cancel button. |
| 34–36 | Confirm button; disabled and shows "Working…" while the request runs. |

### `src/components/ui/States.tsx`
| Lines | What they do |
|---|---|
| 4–13 | `EmptyState`: icon, title, description, optional action button. |
| 15–26 | `ErrorState`: `role="alert"`, message, and a "Try again" button calling `onRetry`. |
| 28–36 | `SkeletonRows`: grey pulsing bars shown while loading (`animate-pulse`). |

### `src/layouts/AppLayout.tsx`
Minimal shell so the pages run on their own. Replace it with your team's shell when merging.
| Lines | What they do |
|---|---|
| 5–9 | Sidebar links list. |
| 12 | `open` = is the mobile drawer open. |
| 15 | Page wrapper: column on mobile, row on desktop (`md:flex-row`). |
| 16–21 | Mobile-only top bar (`md:hidden`) with the hamburger button. |
| 23 | Dark backdrop while the drawer is open; clicking it closes the drawer. |
| 25–29 | Sidebar: on mobile it is fixed and slides in/out with a translate; from `md` up it is static and always visible. |
| 30–38 | Logo and a mobile-only close button. |
| 39–55 | Navigation: `NavLink` knows if it is the current page (`isActive`) and styles it differently (45–49); clicking closes the drawer. |
| 58–60 | `main` holds the current page; `Outlet` is where the child route renders. |

### `src/features/products/ProductFiltersBar.tsx`
| Lines | What they do |
|---|---|
| 4–10 | Props: filter values, categories, view mode, and two callbacks. |
| 12–13 | Shared input styling. |
| 16 | True when any filter differs from the defaults (shows the Reset button). |
| 20–31 | Search box with icon. Controlled by `filters.search`; each change reports a partial update. |
| 32–47 | Table/grid toggle: two buttons made from an array; `aria-pressed` tells assistive tech which is active; the active one is highlighted. |
| 51–58 | Category select; first option "All Categories" has value `""` (no filter). |
| 59–63 | Active/inactive select. |
| 64–69 | Stock-level select. |
| 70–71 | Min/Max price number inputs. |
| 72–78 | Sort select (sends values like `-selling_price`; the leading `-` means descending). |
| 79–83 | Reset button, shown only when filtered. |

### `src/features/products/ProductTable.tsx`
| Lines | What they do |
|---|---|
| 6–9 | Props: rows and a deactivate callback. |
| 11 | Shared header-cell class. |
| 15 | Wrapper allows horizontal scrolling on small screens. |
| 16–17 | Table with minimum width so columns do not squash; `caption` is screen-reader only. |
| 19–29 | Header row with the nine columns from your spec; `scope="col"` helps screen readers. |
| 32–33 | One row per product, keyed by id. |
| 34–38 | Product name links to the detail page. |
| 39 | SKU in monospace. |
| 40–42 | Category chip. |
| 43–44 | Cost and selling price, right-aligned and formatted. |
| 45 | Stock badge. |
| 46 | Reorder level. |
| 47–51 | Active/Inactive pill. |
| 52–59 | Edit link; Deactivate button only for active products. |

### `src/features/products/ProductGrid.tsx`
| Lines | What they do |
|---|---|
| 9 | Responsive grid: 1 column on phones, 2 from `sm`, 3 from `xl`. |
| 10–11 | One list item per product. |
| 12 | Whole card is a link to the detail page, with hover shadow and a keyboard focus ring. |
| 13–18 | Icon square and stock badge. |
| 19–22 | Name and SKU. |
| 23–26 | Category chip and price. |

### `src/features/products/ProductForm.tsx`
| Lines | What they do |
|---|---|
| 4 | `Errors` type: an optional message for each form field. |
| 6–14 | Props: existing product (edit mode), categories, errors from the server, submitting flag, button text, submit/cancel handlers. |
| 16 | Shared input class. |
| 18–32 | `Field`: label + input + error message. `htmlFor` links label to input; the error has `role="alert"` and an id the input references. |
| 34–43 | `validate`: returns an error message per invalid field (name/SKU required, category chosen, prices ≥ 0, reorder level a whole number ≥ 0). |
| 46–56 | Form values state, initialised from the existing product or empty defaults. |
| 57 | Errors found by client-side validation. |
| 58 | `dirty`: has the user changed anything (drives the cancel confirmation). |
| 59 | Merge server and client errors; client ones win. |
| 61–65 | `set`: updates one field (62), clears that field's error (63), marks dirty (64). The generic `K` keeps value types correct per field. |
| 67–72 | Submit: stop the browser reload (68), validate (69), show errors (70), if none, send trimmed values to the parent (71). |
| 74 | Helper that gives each input `id`, `aria-invalid` and `aria-describedby`. |
| 77 | Form element; `noValidate` turns off browser popups so our messages show. |
| 78–80 | Product title. |
| 82–94 | SKU and category side by side (stack on mobile). The `0` option is the "Select a category" placeholder. |
| 96–103 | Cost and selling price. |
| 105–112 | Unit and reorder level. |
| 114–116 | Description textarea. |
| 118–121 | Active checkbox. |
| 123–130 | Cancel and Save buttons; Save is disabled and says "Saving…" while submitting. |

### `src/pages/ProductsPage.tsx`
| Lines | What they do |
|---|---|
| 1–14 | Imports. |
| 17 | `toast` for messages. |
| 18–19 | `filters` is what the user is typing; `debouncedFilters` is the same value 400 ms after they stop. Only the debounced one triggers requests. |
| 20–21 | Current page and table/grid view. |
| 22–24 | Data from the server: the page of products, the summary counts, the categories. |
| 25–26 | Loading and error state. |
| 27 | `reloadKey`: increment it to force a refetch. |
| 28–29 | Product awaiting deactivation confirmation; `busy` while that request runs. |
| 31–33 | On first load, fetch categories. |
| 35–37 | Fetch the stat-card counts on load and whenever `reloadKey` changes. |
| 39–50 | Fetch the product list whenever filters, page or `reloadKey` change. `ignore` (40, 47–49) discards a slow older response if a newer request has started, preventing stale data. Lines 41–42 show loading and clear errors; 43–46 call the API and set data/error/loading. |
| 52–55 | `updateFilters`: merges a filter change and returns to page 1 (otherwise you might sit on page 5 of a smaller result). |
| 57–70 | Deactivate: calls the API (61), shows a toast (62), closes the dialog (63), refreshes (64), shows an error toast on failure (66), always ends busy (68). |
| 72–77 | Config for the four stat cards. |
| 78 | Whether any filter is active (chooses which empty message to show). |
| 82–91 | Header with title text and the "Add New Product SKU" link to `/products/new`. |
| 93–100 | Four stat cards (`–` while the numbers load). |
| 102–103 | White panel containing the filter bar. |
| 105 | Loading skeleton. |
| 106 | Error with retry. |
| 107–117 | Empty states: "No products match your filters" vs "No products yet" with a create button. |
| 118–123 | Table or grid (120) plus pagination (121). |
| 126–134 | The confirmation dialog, open when `target` is set. |

### `src/pages/ProductDetailPage.tsx`
| Lines | What they do |
|---|---|
| 10–17 | `Row`: label on the left, value on the right (a `dt`/`dd` pair for accessibility). |
| 20 | Read `:id` from the URL. |
| 21–23 | State: product, error, loading. |
| 25–32 | `load`: fetch the product, handling loading and errors. |
| 34 | Run `load` on page open or when `id` changes. |
| 36–37 | Loading skeleton; error/not found state. |
| 39–40 | Margin = selling − cost; margin % = margin ÷ selling price (guarded against dividing by 0). |
| 44–47 | Back link. |
| 49–58 | Title, SKU and Edit button. |
| 60 | Layout: one column on mobile, three columns on large screens. |
| 61–72 | Product information card (category, unit, status, dates, description). |
| 75–84 | Pricing card with margin. |
| 85–93 | Inventory summary: stock badge and reorder level. |

### `src/pages/ProductFormPage.tsx`
Used for both `/products/new` and `/products/:id/edit`.
| Lines | What they do |
|---|---|
| 13–14 | `id` exists only on the edit URL, so `isEdit` tells the modes apart. |
| 15–16 | `navigate` changes the page; `toast`. |
| 18–24 | State: categories, product being edited, loading/error, submitting, server field errors, leave-confirmation. |
| 26–34 | Load categories, and the product too if editing, in parallel (`Promise.all`). |
| 36–57 | Submit: lock the form (37), clear old errors (38), create or update (40), success toast (41), go to the detail page (42). In the `catch`, a 400 response is converted into per-field messages (44–50) so each message appears under its input; any other error shows a toast (52). `finally` unlocks the form (55). |
| 59–62 | Cancel: ask for confirmation only if the user changed something. |
| 64–65 | Loading / load-error states. |
| 69–72 | Page title changes between add and edit. |
| 73–81 | The form component. |
| 82–89 | "Discard changes?" dialog. |

---

## 6. Tailwind class glossary (the classes used above)

| Class | Meaning |
|---|---|
| `flex`, `flex-col`, `flex-row` | Flexbox container; direction. |
| `items-center`, `justify-between`, `justify-center`, `justify-end` | Align items on the cross axis; spread, centre or push content on the main axis. |
| `grid grid-cols-N` | CSS grid with N columns. |
| `gap-N`, `space-y-N` | Spacing between children (N × 0.25rem). |
| `p-N`, `px-N`, `py-N`, `mt-N`, `mb-N` | Padding / margin. |
| `w-N`, `h-N`, `w-full`, `max-w-*`, `min-w-[900px]`, `min-w-0`, `flex-1`, `shrink-0` | Sizes; `flex-1` fills remaining space, `min-w-0` lets flex children shrink, `shrink-0` prevents shrinking. |
| `rounded-lg/xl/2xl/full` | Corner radius. |
| `border`, `border-gray-200`, `border-y`, `divide-y` | Borders; `divide-y` adds lines between children. |
| `bg-white`, `bg-indigo-600`, `bg-black/50` | Background colours (`/50` = 50% opacity). |
| `text-xs`, `text-sm`, `text-xl`, `font-bold`, `font-mono`, `uppercase`, `tracking-tight` | Typography. |
| `text-gray-500`, `text-rose-600`, … | Text colours. |
| `shadow-xs/lg/2xl` | Shadows. |
| `fixed`, `sticky`, `absolute`, `relative`, `inset-0`, `top-0`, `z-50` | Positioning and stacking order. |
| `overflow-x-auto` | Horizontal scroll when content is wider. |
| `hidden`, `md:hidden` | Hide always / hide from the `md` breakpoint up. |
| `sm:`, `md:`, `lg:`, `xl:` | Apply the class from 640 / 768 / 1024 / 1280 px wide upward (mobile-first). |
| `hover:`, `focus:`, `focus-visible:`, `disabled:` | State variants (mouse over, focused, keyboard focus, disabled). |
| `transition-*`, `duration-300`, `-translate-x-full` | Animation (drawer slide). |
| `animate-pulse` | Pulsing skeleton effect. |
| `sr-only` | Visible to screen readers only. |
| `whitespace-nowrap`, `whitespace-pre-line` | Prevent wrapping / respect line breaks. |
| `accent-indigo-600` | Checkbox colour. |
| `[…]` values like `z-[60]`, `text-[11px]` | One-off arbitrary values. |
