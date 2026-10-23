export class ApiError extends Error {
  status: number;
  fieldErrors: Record<string, string[]>;

  constructor(status: number, message: string, fieldErrors: Record<string, string[]> = {}) {
    super(message);
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("access_token");
  if (token) return { Authorization: `Bearer ${token}` };
  const basic = import.meta.env.VITE_DEV_BASIC_AUTH as string | undefined;
  if (basic) return { Authorization: `Basic ${btoa(basic)}` };
  return {};
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...authHeaders(), ...options.headers },
  });

  if (response.status === 204) return undefined as T;

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const fieldErrors = response.status === 400 && body && typeof body === "object" ? body : {};
    const message = body?.detail ?? "Something went wrong. Please try again.";
    throw new ApiError(response.status, message, fieldErrors);
  }
  return body as T;
}
