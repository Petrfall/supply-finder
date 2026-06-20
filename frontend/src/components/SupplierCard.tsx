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

// Max points per signal — mirrors WEIGHTS in backend/app/scoring.py.
const MAX_WEIGHTS: Record<string, number> = {
  region_match: 30,
  category_match: 15,
  has_contacts: 15,
  certificates: 15,
  min_order: 10,
  price_known: 8,
  delivery_terms: 7,
};
const ORDER = Object.keys(MAX_WEIGHTS);

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
          <div className="flex items-center justify-end gap-1">
            <span className="text-[10px] uppercase tracking-wide text-muted">
              {tr.score}
            </span>
            <ScoreInfo s={s} lang={lang} />
          </div>
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

/** "i" badge that reveals the score breakdown on hover/focus. */
function ScoreInfo({ s, lang }: { s: ScoredSupplier; lang: Lang }) {
  const tr = t[lang];
  const labels = tr.breakdownLabels;
  return (
    <span className="group relative inline-flex">
      <button
        type="button"
        aria-label={tr.breakdown}
        className="flex h-4 w-4 items-center justify-center rounded-full border border-line text-[10px] font-bold text-muted hover:border-brand2 hover:text-brand2"
      >
        i
      </button>
      <div className="invisible absolute right-0 top-5 z-20 w-60 rounded-lg border border-line bg-panel2 p-3 text-left opacity-0 shadow-xl transition-opacity group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100">
        <div className="mb-2 text-xs font-semibold text-white">{tr.breakdown}</div>
        <ul className="space-y-1.5">
          {ORDER.map((key) => {
            const got = s.score_breakdown[key] ?? 0;
            const max = MAX_WEIGHTS[key];
            const pct = max ? (got / max) * 100 : 0;
            return (
              <li key={key} className="text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-muted">{labels[key] ?? key}</span>
                  <span className="font-mono text-text/90">
                    {got} {tr.ofMax} {max}
                  </span>
                </div>
                <div className="mt-0.5 h-1 w-full overflow-hidden rounded bg-line">
                  <div
                    className={pct >= 60 ? "h-full bg-brand" : pct > 0 ? "h-full bg-amber" : "h-full"}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
        <div className="mt-2 border-t border-line/60 pt-2 text-[11px] text-muted">
          {tr.confidence}: {Math.round(s.confidence * 100)}%
        </div>
      </div>
    </span>
  );
}
