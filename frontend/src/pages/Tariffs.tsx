import { useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { api } from "../api";
import { t } from "../i18n";
import Button from "../components/Button";
import Card from "../components/Card";
import Spinner from "../components/Spinner";
import type { PaymentMethod, Tariff } from "../types";

const monthsLabel: Record<Tariff["months"], string> = {
  1: "months_1",
  3: "months_3",
  6: "months_6",
  12: "months_12",
};

export default function Tariffs() {
  const [tariffs, setTariffs] = useState<Tariff[] | null>(null);
  const [selected, setSelected] = useState<Tariff | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .getTariffs()
      .then(setTariffs)
      .catch((e: Error) => setError(e.message));
  }, []);

  const onPay = async (method: PaymentMethod) => {
    if (!selected) return;
    setBusy(true);
    try {
      const inv = await api.createInvoice(selected.months, method);
      if (inv.isTelegramInvoice) {
        WebApp.openInvoice(inv.paymentUrl, (status) => {
          if (status === "paid") {
            WebApp.showAlert("Оплата прошла. Подписка активируется в течение минуты.");
          } else if (status === "failed") {
            WebApp.showAlert("Оплата не удалась.");
          }
        });
      } else {
        WebApp.openTelegramLink(inv.paymentUrl);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (error) return <Card><p>{t("error")}: {error}</p></Card>;
  if (!tariffs) return <Spinner />;

  if (selected) {
    return (
      <div className="flex flex-col gap-3">
        <Card>
          <p className="text-sm" style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
            {t(monthsLabel[selected.months] as never)}
          </p>
          <p className="mt-1 text-2xl font-bold">
            {selected.priceRub} {t("rub")}
          </p>
          <p className="text-sm" style={{ color: "var(--tg-theme-hint-color, #708499)" }}>
            {selected.priceStars} {t("stars")}
          </p>
        </Card>
        <Button onClick={() => onPay("stars")} disabled={busy}>
          {t("btn_pay_stars")}
        </Button>
        <Button variant="secondary" onClick={() => onPay("yookassa")} disabled={busy}>
          {t("btn_pay_card")}
        </Button>
        <Button variant="secondary" onClick={() => onPay("cryptobot")} disabled={busy}>
          {t("btn_pay_crypto")}
        </Button>
        <Button variant="secondary" onClick={() => setSelected(null)} disabled={busy}>
          ←
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {tariffs.map((tariff) => (
        <button
          key={tariff.months}
          onClick={() => setSelected(tariff)}
          className="w-full rounded-2xl p-4 text-left transition-opacity active:opacity-70"
          style={{ background: "var(--tg-theme-secondary-bg-color, #232e3c)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">{t(monthsLabel[tariff.months] as never)}</p>
              <p
                className="mt-1 text-xs"
                style={{ color: "var(--tg-theme-hint-color, #708499)" }}
              >
                {tariff.priceStars} {t("stars")}
              </p>
            </div>
            <p className="text-lg font-bold">
              {tariff.priceRub} {t("rub")}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
