import { useEffect, useMemo, useState } from "react";
import { t, type Lang } from "../lib/i18n";
import {
  listPresets,
  savePreset,
  deletePreset,
  type MessagePreset,
} from "../lib/api";
import type { ScoredSupplier } from "../lib/types";

type Field = MessagePreset["fields"][number];

function defaultFields(lang: Lang): Field[] {
  return lang === "ru"
    ? [
        { key: "поставщик", label: "Поставщик", value: "", required: false },
        { key: "товар", label: "Товар", value: "", required: true },
        { key: "объём", label: "Нужный объём", value: "", required: false },
        { key: "компания", label: "Моя компания", value: "", required: false },
      ]
    : [
        { key: "supplier", label: "Supplier", value: "", required: false },
        { key: "item", label: "Item", value: "", required: true },
        { key: "volume", label: "Volume needed", value: "", required: false },
        { key: "company", label: "My company", value: "", required: false },
      ];
}

function defaultTemplate(lang: Lang): string {
  return lang === "ru"
    ? "Здравствуйте, {поставщик}!\n\nПодскажите, пожалуйста, есть ли у вас {товар}? " +
        "Интересует объём {объём}.\n\nС уважением, {компания}."
    : "Hello, {supplier}!\n\nDo you have {item} available? We're interested in {volume}.\n\nBest regards, {company}.";
}

/** Substitute {key} tokens; drop sentences whose only filled token is missing
 * is overkill — instead just blank missing tokens and tidy double spaces. */
function render(template: string, fields: Field[]): string {
  let out = template;
  for (const f of fields) {
    out = out.replaceAll(`{${f.key}}`, f.value || "");
  }
  return out.replace(/[ \t]{2,}/g, " ").replace(/ +\n/g, "\n").trim();
}

interface Props {
  lang: Lang;
  /** When opened from a saved supplier, prefill the "supplier" field. */
  prefillSupplier?: ScoredSupplier | null;
}

export function MessageBuilder({ lang, prefillSupplier }: Props) {
  const tr = t[lang];
  const [fields, setFields] = useState<Field[]>(() => defaultFields(lang));
  const [template, setTemplate] = useState<string>(() => defaultTemplate(lang));
  const [presets, setPresets] = useState<MessagePreset[]>([]);
  const [presetName, setPresetName] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    listPresets().then(setPresets).catch(() => {});
  }, []);

  // Prefill the supplier-name field when launched from a saved card.
  useEffect(() => {
    if (!prefillSupplier) return;
    setFields((prev) =>
      prev.map((f) =>
        f.key === "поставщик" || f.key === "supplier"
          ? { ...f, value: prefillSupplier.name }
          : f
      )
    );
  }, [prefillSupplier]);

  const message = useMemo(() => render(template, fields), [template, fields]);

  function setField(i: number, patch: Partial<Field>) {
    setFields((prev) => prev.map((f, idx) => (idx === i ? { ...f, ...patch } : f)));
  }
  function addField() {
    setFields((prev) => [
      ...prev,
      { key: `поле${prev.length + 1}`, label: "", value: "", required: false },
    ]);
  }
  function removeField(i: number) {
    setFields((prev) => prev.filter((_, idx) => idx !== i));
  }

  async function onSavePreset() {
    if (!presetName.trim()) return;
    const p: MessagePreset = { name: presetName.trim(), fields, template };
    await savePreset(p);
    setPresets(await listPresets());
    setPresetName("");
  }
  function loadPreset(p: MessagePreset) {
    setFields(p.fields);
    setTemplate(p.template);
  }
  async function removePreset(name: string) {
    await deletePreset(name);
    setPresets(await listPresets());
  }

  function copy() {
    navigator.clipboard.writeText(message).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <section className="card p-5">
      <h2 className="text-lg font-bold text-white">{tr.msgBuilder}</h2>
      <p className="mt-1 text-xs text-muted">{tr.msgHint}</p>

      <div className="mt-4 grid gap-5 lg:grid-cols-2">
        {/* Left: field constructor + template */}
        <div>
          <div className="space-y-2">
            {fields.map((f, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  className="input w-24 font-mono text-xs"
                  value={f.key}
                  onChange={(e) => setField(i, { key: e.target.value })}
                  placeholder={tr.fieldKey}
                />
                <input
                  className="input flex-1"
                  value={f.value}
                  onChange={(e) => setField(i, { value: e.target.value })}
                  placeholder={f.label || tr.fieldValue}
                />
                <label className="flex items-center gap-1 text-[11px] text-muted">
                  <input
                    type="checkbox"
                    className="h-3.5 w-3.5 accent-brand"
                    checked={f.required}
                    onChange={(e) => setField(i, { required: e.target.checked })}
                  />
                  {tr.required}
                </label>
                <button
                  onClick={() => removeField(i)}
                  className="text-muted hover:text-red-400"
                  aria-label={tr.remove}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <button onClick={addField} className="mt-2 text-xs text-brand2 hover:underline">
            {tr.addField}
          </button>

          <label className="mt-4 block">
            <span className="mb-1 block text-xs text-muted">{tr.template}</span>
            <textarea
              className="input h-28 resize-y font-mono text-xs"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
            />
          </label>

          {/* Presets */}
          <div className="mt-4 flex items-center gap-2">
            <input
              className="input flex-1"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              placeholder={tr.presetName}
            />
            <button onClick={onSavePreset} className="btn whitespace-nowrap">
              {tr.savePreset}
            </button>
          </div>
          {presets.length > 0 && (
            <div className="mt-3">
              <div className="mb-1 text-xs text-muted">{tr.myPresets}</div>
              <div className="flex flex-wrap gap-2">
                {presets.map((p) => (
                  <span key={p.name} className="chip gap-2">
                    <button onClick={() => loadPreset(p)} className="hover:text-brand2">
                      {p.name}
                    </button>
                    <button
                      onClick={() => removePreset(p.name)}
                      className="text-muted hover:text-red-400"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: live preview */}
        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs text-muted">{tr.preview}</span>
            <button onClick={copy} className="text-xs font-medium text-brand2 hover:underline">
              {copied ? tr.copied : tr.copy}
            </button>
          </div>
          <pre className="card min-h-[12rem] whitespace-pre-wrap p-4 font-sans text-sm text-text/90">
            {message}
          </pre>
        </div>
      </div>
    </section>
  );
}
