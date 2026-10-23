import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import { ErrorState, SkeletonRows } from "../components/ui/States";
import { useToast } from "../components/ui/Toast";
import ProductForm from "../features/products/ProductForm";
import { ApiError } from "../services/api/client";
import { listCategories } from "../services/api/categories";
import { createProduct, getProduct, updateProduct } from "../services/api/products";
import type { Category, Product, ProductInput } from "../types/product";

export default function ProductFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const toast = useToast();

  const [categories, setCategories] = useState<Category[]>([]);
  const [product, setProduct] = useState<Product | undefined>();
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [serverErrors, setServerErrors] = useState<Partial<Record<keyof ProductInput, string>>>({});
  const [confirmLeave, setConfirmLeave] = useState(false);

  useEffect(() => {
    Promise.all([listCategories(), id ? getProduct(id) : Promise.resolve(undefined)])
      .then(([cats, prod]) => {
        setCategories(cats);
        setProduct(prod);
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(data: ProductInput) {
    setSubmitting(true);
    setServerErrors({});
    try {
      const saved = id ? await updateProduct(id, data) : await createProduct(data);
      toast.success(isEdit ? "Product updated." : "Product created.");
      navigate(`/products/${saved.id}`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 400) {
        const mapped: Partial<Record<keyof ProductInput, string>> = {};
        for (const [field, messages] of Object.entries(e.fieldErrors)) {
          mapped[field as keyof ProductInput] = Array.isArray(messages) ? messages.join(" ") : String(messages);
        }
        setServerErrors(mapped);
        toast.error("Please fix the highlighted fields.");
      } else {
        toast.error((e as Error).message);
      }
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancel(dirty: boolean) {
    if (dirty) setConfirmLeave(true);
    else navigate(-1);
  }

  if (loading) return <SkeletonRows rows={5} />;
  if (loadError) return <ErrorState message={loadError} onRetry={() => window.location.reload()} />;

  return (
    <>
      <div>
        <h1 className="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">{isEdit ? "Edit Product" : "Add New Product to Catalog"}</h1>
        <p className="mt-0.5 text-xs text-gray-500">{isEdit ? "Update pricing, category, and reorder settings." : "Create a new SKU in your catalog."}</p>
      </div>
      <ProductForm
        initial={product}
        categories={categories}
        serverErrors={serverErrors}
        submitting={submitting}
        submitLabel={isEdit ? "Save changes" : "Save Product SKU"}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
      <ConfirmDialog
        open={confirmLeave}
        title="Discard changes?"
        message="You have unsaved changes. If you leave now they will be lost."
        confirmLabel="Discard"
        onConfirm={() => navigate(-1)}
        onCancel={() => setConfirmLeave(false)}
      />
    </>
  );
}
