import type { CSSProperties, ReactNode } from "react";

export default function Card({
  children,
  style,
  className = "",
}: {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl p-4 shadow-sm ${className}`}
      style={{
        background: "var(--tg-theme-secondary-bg-color, #232e3c)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
