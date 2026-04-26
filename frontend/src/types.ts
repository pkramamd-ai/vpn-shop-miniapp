export interface Subscription {
  status: "active" | "expired" | "trial" | "none";
  expireAt: string | null;
  daysLeft: number;
  trafficLimitBytes: number;
  trafficUsedBytes: number;
  subscriptionUrl: string | null;
}

export interface Tariff {
  months: 1 | 3 | 6 | 12;
  priceRub: number;
  priceStars: number;
}

export interface ReferralStats {
  link: string;
  invitedCount: number;
  bonusDaysEarned: number;
  bonusDaysPerInvite: number;
}

export interface InvoiceResponse {
  paymentUrl: string;
  invoiceId: string;
  isTelegramInvoice: boolean;
}

export type PaymentMethod = "stars" | "yookassa" | "cryptobot";
