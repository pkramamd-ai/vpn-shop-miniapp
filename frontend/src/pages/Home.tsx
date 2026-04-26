import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { t } from "../i18n";
import Button from "../components/Button";
import Card from "../components/Card";
import Spinner from "../components/Spinner";
import type { Subscription } from "../types";

function formatBytes(bytes: number): string {
  if (bytes === 0) return t("traffic_unlimited");
  const gb = bytes / 1024 ** 3;
  return `${gb.toFixed(1)} GB`;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString();
}

export default function Home() {
  const [sub, setSub] = useState<Subscription | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getSubscription()
      .then(setSub)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <Card>
        <p className="text-sm">{t("error")}: {error}</p>
        <div className="mt-3">
          <Button onClick={() => window.location.reload()}>{t("retry")}</Button>
        </div>
      </Card>
    );
  }

  if (!sub) return <Spinner />;

  const trafficPct = sub.trafficLimitBytes
    ? Math.min(100, (sub.trafficUsedBytes / sub.trafficLimitBytes) * 100)
    : 0;

  const statusLabel =
    sub.status === "active"
      ? t("sub_active")
      : sub.status === "trial"
        ? t("sub_trial")
        : sub.status === "expired"
          ? t("sub_expired")
          : t("sub_none");

  const statusColor =
    sub.status === "active" || sub.status === "trial"
      ? "#3ad172"
      : sub.status === "expired"
        ? "#ff5c5c"
        : "var(--tg-theme-hint-color, #708499)";

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <div className="mb-2 flex items-center gap-2">
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: statusColor }}
          />
          <span className="text-sm font-semibold" style={{ color: statusColor }}>
            {statusLabel}
          </span>
        </div>
        {sub.status !== "none" && (
          <>
            <div className="flex justify-between py-1 text-sm">
              <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
                {t("expires_at")}
              </span>
              <span>{formatDate(sub.expireAt)}</span>
            </div>
            <div className="flex justify-between py-1 text-sm">
              <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
                {t("days_left")}
              </span>
              <span>{sub.daysLeft}</span>
            </div>
            <div className="mt-2">
              <div className="mb-1 flex justify-between text-sm">
                <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
                  {t("traffic")}
                </span>
                <span>
                  {formatBytes(sub.trafficUsedBytes)} /{" "}
                  {formatBytes(sub.trafficLimitBytes)}
                </span>
              </div>
              {sub.trafficLimitBytes > 0 && (
                <div
                  className="h-2 overflow-hidden rounded-full"
                  style={{
                    background: "var(--tg-theme-bg-color, #17212b)",
                  }}
                >
                  <div
                    className="h-full"
                    style={{
                      width: `${trafficPct}%`,
                      background:
                        "var(--tg-theme-button-color, #2ea6ff)",
                    }}
                  />
                </div>
              )}
            </div>
          </>
        )}
      </Card>

      <Link to="/tariffs" className="block">
        <Button>
          {sub.status === "none" || sub.status === "expired"
            ? t("btn_buy")
            : t("btn_renew")}
        </Button>
      </Link>

      {(sub.status === "active" || sub.status === "trial") && (
        <Link to="/connect" className="block">
          <Button variant="secondary">{t("connect_title")}</Button>
        </Link>
      )}
    </div>
  );
}
