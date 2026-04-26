import WebApp from "@twa-dev/sdk";
import type {
  InvoiceResponse,
  PaymentMethod,
  ReferralStats,
  Subscription,
  Tariff,
} from "./types";

const API_BASE: string = (import.meta.env.VITE_API_BASE as string) ?? "";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (WebApp.initData) {
    headers.set("X-Telegram-Init-Data", WebApp.initData);
  }
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getSubscription: () => request<Subscription>("/api/subscription"),
  getTariffs: () => request<Tariff[]>("/api/tariffs"),
  getReferral: () => request<ReferralStats>("/api/referral"),
  createInvoice: (months: 1 | 3 | 6 | 12, method: PaymentMethod) =>
    request<InvoiceResponse>("/api/invoice", {
      method: "POST",
      body: JSON.stringify({ months, method }),
    }),
};
