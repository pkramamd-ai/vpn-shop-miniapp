import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import WebApp from "@twa-dev/sdk";
import { api } from "../api";
import { t } from "../i18n";
import Button from "../components/Button";
import Card from "../components/Card";
import Spinner from "../components/Spinner";
import type { Subscription } from "../types";

const apps = [
  { name: "Happ", scheme: "happ://add/" },
  { name: "v2rayNG / v2rayN", scheme: "v2rayng://install-config?url=" },
  { name: "Streisand", scheme: "streisand://import/" },
  { name: "Hiddify", scheme: "hiddify://import/" },
  { name: "Clash", scheme: "clash://install-config?url=" },
];

export default function Connect() {
  const [sub, setSub] = useState<Subscription | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api
      .getSubscription()
      .then(setSub)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <Card><p>{t("error")}: {error}</p></Card>;
  if (!sub) return <Spinner />;
  if (!sub.subscriptionUrl)
    return (
      <Card>
        <p className="text-sm">{t("no_subscription_yet")}</p>
      </Card>
    );

  const url = sub.subscriptionUrl;
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      WebApp.showAlert(url);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <p className="mb-3 text-sm" style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
          {t("connect_desc")}
        </p>
        <div className="flex justify-center rounded-xl bg-white p-4">
          <QRCodeSVG value={url} size={200} />
        </div>
      </Card>
      <Button onClick={copy}>{copied ? t("btn_copied") : t("btn_copy")}</Button>
      <div className="flex flex-col gap-2">
        {apps.map((app) => (
          <Button
            key={app.name}
            variant="secondary"
            onClick={() =>
              WebApp.openLink(`${app.scheme}${encodeURIComponent(url)}`, {
                try_instant_view: false,
              })
            }
          >
            {t("open_in")} {app.name}
          </Button>
        ))}
      </div>
    </div>
  );
}
