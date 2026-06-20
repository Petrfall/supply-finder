import type { ScoredSupplier } from "../lib/types";
import { t, type Lang } from "../lib/i18n";

interface Props {
  items: ScoredSupplier[];
  lang: Lang;
  onClear: () => void;
}

export function ComparisonTable({ items, lang, onClear }: Props) {
  const tr = t[lang];
  if (items.length < 2) return null;

  const rows: { label: string; get: (s: ScoredSupplier) => string }[] = [
    { label: tr.score, get: (s) => String(s.score) },
    { label: tr.region, get: (s) => [s.city, s.region].filter(Boolean).join(", ") || "—" },
    { label: tr.moq, get: (s) => s.min_order || "—" },
    { label: tr.price, get: (s) => s.price_note || "—" },
    { label: tr.certsLabel, get: (s) => (s.certificates.length ? s.certificates.join(", ") : "—") },
    { label: tr.delivery, get: (s) => s.delivery_terms || "—" },
    { label: tr.contacts, get: (s) => [s.email, s.phone].filter(Boolean).join(" / ") || "—" },
  ];

  return (
    <section className="card mt-8 overflow-x-auto p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">{tr.comparisonTitle}</h2>
        <button onClick={onClear} className="text-xs text-muted hover:text-text">
          {tr.clearCompare}
        </button>
      </div>
      <table className="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr>
            <th className="border-b border-line py-2 pr-4 text-left font-medium text-muted">
              {tr.field}
            </th>
            {items.map((s) => (
              <th
                key={s.name}
                className="border-b border-line px-3 py-2 text-left font-bold text-white"
              >
                {s.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td className="border-b border-line/60 py-2 pr-4 text-muted">{row.label}</td>
              {items.map((s) => (
                <td key={s.name} className="border-b border-line/60 px-3 py-2 text-text/90">
                  {row.get(s)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
