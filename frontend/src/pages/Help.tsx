import WebApp from "@twa-dev/sdk";
import Button from "../components/Button";
import Card from "../components/Card";
import { t } from "../i18n";

const SUPPORT_URL: string = (import.meta.env.VITE_SUPPORT_URL as string) ?? "";

export default function Help() {
  return (
    <div className="flex flex-col gap-4">
      <Card>
        <h2 className="text-lg font-semibold">{t("help_title")}</h2>
        <p
          className="mt-2 text-sm"
          style={{ color: "var(--tg-theme-hint-color, #708499)" }}
        >
          {t("help_desc")}
        </p>
      </Card>
      {SUPPORT_URL && (
        <Button onClick={() => WebApp.openLink(SUPPORT_URL)}>
          {t("help_title")}
        </Button>
      )}
    </div>
  );
}
