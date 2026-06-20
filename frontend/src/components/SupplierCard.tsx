import type { ScoredSupplier } from "../lib/types";
import { t, type Lang } from "../lib/i18n";

interface Props {
  s: ScoredSupplier;
  lang: Lang;
  rank: number;
  region: string | null;
  inCompare: boolean;
  onToggleCompare: () => void;
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-brand";
  if (score >= 55) return "text-amber";
  return "text-muted";
}

export function SupplierCard({ s, lang, rank, region, inCompare, onToggleCompare }: Props) {
  const tr = t[lang];
  const contacts = [s.email, s.phone].filter(Boolean);
  const reason = s.reason || (rank === 0 ? tr.whyAuto(region) : null);

  return (
    <article className="card flex flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-white">{s.name}</h3>
          <p className="mt-0.5 text-xs text-muted">
            {[s.city, s.region].filter(Boolean).join(" · ") || "—"}
          </p>
        </div>
        <div className="text-right">
          <div className={`font-mono text-2xl font-bold ${scoreColor(s.score)}`}>
            {s.score}
          </div>
          <div className="text-[10px] uppercase tracking-wide text-muted">{tr.score}</div>
        </div>
      </div>

      {s.description && (
        <p className="mt-2 text-sm leading-snug text-text/90">{s.description}</p>
      )}

      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        {s.min_order && <Field label={tr.moq} value={s.min_order} />}
        {s.price_note && <Field label={tr.price} value={s.price_note} />}
        {s.delivery_terms && <Field label={tr.delivery} value={s.delivery_terms} />}
        {s.delivery_regions.length > 0 && (
          <Field label={tr.deliveryRegions} value={s.delivery_regions.join(", ")} />
        )}
      </dl>

      {s.certificates.length > 0 && (
        <div className="mt-3">
          <div className="mb-1 text-xs text-muted">{tr.certsLabel}</div>
          <div className="flex flex-wrap gap-1.5">
            {s.certificates.map((c) => (
              <span key={c} className="chip border-brand/40 text-brand">{c}</span>
            ))}
          </div>
        </div>
      )}

      {(contacts.length > 0 || s.website) && (
        <div className="mt-3 text-sm">
          <div className="mb-1 text-xs text-muted">{tr.contacts}</div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            {s.website && (
              <a
                href={s.website.startsWith("http") ? s.website : `https://${s.website}`}
                target="_blank"
                rel="noreferrer"
                className="text-brand2 hover:underline"
              >
                {s.website}
              </a>
            )}
            {s.email && <span className="text-text/90">{s.email}</span>}
            {s.phone && <span className="text-text/90">{s.phone}</span>}
          </div>
        </div>
      )}

      {reason && (
        <div className="mt-3 rounded-lg border border-brand/30 bg-brand/5 p-2.5 text-xs leading-snug text-text/90">
          <span className="font-semibold text-brand">{tr.why}: </span>
          {reason}
        </div>
      )}

      <div className="mt-auto flex items-center justify-between pt-4">
        {s.source_url ? (
          <a
            href={s.source_url}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-muted hover:text-text"
          >
            {tr.source} ↗
          </a>
        ) : (
          <span />
        )}
        <button
          onClick={onToggleCompare}
          className={`rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ${
            inCompare
              ? "border-brand2 bg-brand2/15 text-brand2"
              : "border-line text-muted hover:text-text"
          }`}
        >
          {inCompare ? tr.inCompare : tr.addCompare}
        </button>
      </div>
    </article>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-wide text-muted">{label}</dt>
      <dd className="text-text/90">{value}</dd>
    </div>
  );
}
