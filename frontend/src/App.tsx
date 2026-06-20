import { useEffect, useState } from "react";
import { search } from "./lib/api";
import type { ScoredSupplier, SearchResponse } from "./lib/types";
import { t, type Lang } from "./lib/i18n";
import { SupplierCard } from "./components/SupplierCard";
import { ComparisonTable } from "./components/ComparisonTable";

const PRESETS = [
  { ru: "Ингредиенты · Урал", en: "Ingredients · Ural", category: "ingredients", region: "УрФО" },
  { ru: "Упаковка · Москва", en: "Packaging · Moscow", category: "packaging", region: "Москва" },
  { ru: "Молочная · Татарстан", en: "Dairy · Tatarstan", category: "finished_products", region: "Татарстан" },
];

export default function App() {
  const [lang, setLang] = useState<Lang>(
    navigator.language.toLowerCase().startsWith("ru") ? "ru" : "en"
  );
  const tr = t[lang];

  const [category, setCategory] = useState("ingredients");
  const [region, setRegion] = useState("");
  const [needsCerts, setNeedsCerts] = useState(false);
  const [keyword, setKeyword] = useState("");

  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [compare, setCompare] = useState<ScoredSupplier[]>([]);

  useEffect(() => {
    document.title = tr.title;
    document.documentElement.lang = lang;
  }, [lang, tr.title]);

  async function runSearch(cat = category, reg = region) {
    setLoading(true);
    setError(null);
    try {
      const r = await search({
        category: cat,
        region: reg || undefined,
        filters: { needs_certificates: needsCerts, keyword: keyword || undefined },
        lang,
        limit: 12,
      });
      setRes(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  function toggleCompare(s: ScoredSupplier) {
    setCompare((prev) =>
      prev.find((x) => x.name === s.name)
        ? prev.filter((x) => x.name !== s.name)
        : prev.length < 4
        ? [...prev, s]
        : prev
    );
  }

  const sourceLabel: Record<string, string> = {
    live: tr.sourceLive,
    cache: tr.sourceCache,
    seed: tr.sourceSeed,
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-line/60 bg-ink/80 backdrop-blur">
        <div className="container-c flex h-14 items-center justify-between">
          <span className="font-mono text-sm font-semibold text-white">
            supplier<span className="text-brand">.finder</span>
          </span>
          <div className="flex items-center gap-1 rounded-full border border-line bg-panel2 p-0.5 text-xs">
            {(["ru", "en"] as Lang[]).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`rounded-full px-2.5 py-1 font-medium uppercase ${
                  lang === l ? "bg-brand text-white" : "text-muted hover:text-text"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="container-c py-8">
        <h1 className="text-2xl font-bold text-white sm:text-3xl">{tr.title}</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">{tr.subtitle}</p>

        {/* Search form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            runSearch();
          }}
          className="card mt-6 grid gap-4 p-5 sm:grid-cols-2 lg:grid-cols-4"
        >
          <label className="block">
            <span className="mb-1 block text-xs text-muted">{tr.category}</span>
            <input
              className="input"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder={tr.categoryPh}
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs text-muted">{tr.region}</span>
            <input
              className="input"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder={tr.regionPh}
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs text-muted">{tr.keyword}</span>
            <input
              className="input"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={tr.keywordPh}
            />
          </label>
          <div className="flex items-end gap-3">
            <label className="flex flex-1 items-center gap-2 text-sm text-text/90">
              <input
                type="checkbox"
                checked={needsCerts}
                onChange={(e) => setNeedsCerts(e.target.checked)}
                className="h-4 w-4 accent-brand"
              />
              {tr.certs}
            </label>
          </div>
          <div className="sm:col-span-2 lg:col-span-4">
            <button type="submit" className="btn" disabled={loading}>
              {loading ? tr.searching : tr.searchBtn}
            </button>
          </div>
        </form>

        {/* Presets */}
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-muted">{tr.presets}</span>
          {PRESETS.map((p) => (
            <button
              key={p.category + p.region}
              onClick={() => {
                setCategory(p.category);
                setRegion(p.region);
                runSearch(p.category, p.region);
              }}
              className="chip hover:border-brand2 hover:text-text"
            >
              {lang === "ru" ? p.ru : p.en}
            </button>
          ))}
        </div>

        {error && (
          <div className="mt-6 rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {res && (
          <>
            {res.warnings.map((w) => (
              <div
                key={w}
                className="mt-6 rounded-lg border border-amber/40 bg-amber/10 p-3 text-sm text-amber"
              >
                {w}
              </div>
            ))}

            {res.summary && (
              <div className="mt-6 card p-4">
                <div className="flex items-center gap-2">
                  <span className="chip border-brand2/40 text-brand2">
                    {sourceLabel[res.source]}
                  </span>
                </div>
                <p className="mt-2 text-sm text-text/90">{res.summary}</p>
              </div>
            )}

            {res.suppliers.length === 0 ? (
              <p className="mt-8 text-center text-muted">{tr.noResults}</p>
            ) : (
              <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {res.suppliers.map((s, i) => (
                  <SupplierCard
                    key={s.name}
                    s={s}
                    lang={lang}
                    rank={i}
                    region={res.region ?? null}
                    inCompare={!!compare.find((x) => x.name === s.name)}
                    onToggleCompare={() => toggleCompare(s)}
                  />
                ))}
              </div>
            )}

            <ComparisonTable items={compare} lang={lang} onClear={() => setCompare([])} />
          </>
        )}
      </main>

      <footer className="border-t border-line/60 py-6">
        <div className="container-c text-xs text-muted">
          Food Supplier Finder · FastAPI + React · web-search + LLM extraction (structured)
        </div>
      </footer>
    </div>
  );
}
