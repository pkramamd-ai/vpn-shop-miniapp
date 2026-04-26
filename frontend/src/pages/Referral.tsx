import { useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { api } from "../api";
import { t } from "../i18n";
import Button from "../components/Button";
import Card from "../components/Card";
import Spinner from "../components/Spinner";
import type { ReferralStats } from "../types";

export default function Referral() {
  const [data, setData] = useState<ReferralStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api
      .getReferral()
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <Card><p>{t("error")}: {error}</p></Card>;
  if (!data) return <Spinner />;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(data.link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      WebApp.showAlert(data.link);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <h2 className="text-lg font-semibold">{t("referral_title")}</h2>
        <p
          className="mt-2 text-sm"
          style={{ color: "var(--tg-theme-hint-color, #708499)" }}
        >
          {t("referral_desc")}
        </p>
      </Card>
      <Card>
        <p className="font-mono break-all text-xs">{data.link}</p>
      </Card>
      <Button onClick={copy}>{copied ? t("btn_copied") : t("btn_copy")}</Button>
      <Card>
        <div className="flex justify-between py-1 text-sm">
          <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
            {t("referral_invited")}
          </span>
          <span>{data.invitedCount}</span>
        </div>
        <div className="flex justify-between py-1 text-sm">
          <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
            {t("referral_earned")}
          </span>
          <span>{data.bonusDaysEarned}</span>
        </div>
        <div className="flex justify-between py-1 text-sm">
          <span style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
            {t("referral_per_invite")}
          </span>
          <span>{data.bonusDaysPerInvite}</span>
        </div>
      </Card>
    </div>
  );
}
