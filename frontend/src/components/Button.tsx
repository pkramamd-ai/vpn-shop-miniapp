import type { ButtonHTMLAttributes } from "react";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export default function Button({
  variant = "primary",
  className = "",
  ...rest
}: Props) {
  const colors =
    variant === "primary"
      ? {
          background: "var(--tg-theme-button-color, #2ea6ff)",
          color: "var(--tg-theme-button-text-color, #fff)",
        }
      : {
          background: "var(--tg-theme-bg-color, #17212b)",
          color: "var(--tg-theme-text-color, #fff)",
          border: "1px solid var(--tg-theme-section-separator-color, #2c3e50)",
        };
  return (
    <button
      {...rest}
      className={`w-full rounded-xl px-4 py-3 text-sm font-semibold transition-opacity active:opacity-70 disabled:opacity-50 ${className}`}
      style={colors}
    />
  );
}
