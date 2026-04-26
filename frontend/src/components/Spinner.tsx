export default function Spinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div
        className="spin h-8 w-8 rounded-full border-2 border-current border-t-transparent"
        style={{ color: "var(--tg-theme-button-color, #2ea6ff)" }}
      />
    </div>
  );
}
