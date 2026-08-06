import React, { useMemo, useState } from "react";
import { Check, ChevronDown, Globe } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { getLanguageText, LANGUAGE_OPTIONS, LanguageCode } from "../i18n";

type LanguageSettingsProps = {
  value: LanguageCode;
  onChange: (value: LanguageCode) => void;
};

export function LanguageSettings({ value, onChange }: LanguageSettingsProps) {
  const [open, setOpen] = useState(false);
  const activeLanguage = useMemo(
    () => LANGUAGE_OPTIONS.find((option) => option.code === value) || LANGUAGE_OPTIONS[0],
    [value]
  );

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        title={getLanguageText(value, "Language settings")}
        aria-label={getLanguageText(value, "Language settings")}
        className="p-2 rounded-lg bg-white border border-[#EAE3D9] text-[#8E8A85] hover:text-[#967A55] hover:border-[#C5A880] shadow-[0_1px_3px_rgba(0,0,0,0.01)] transition-all flex items-center gap-1.5"
      >
        <Globe className="w-4 h-4" />
        <span className="text-[10px] font-bold font-mono">{activeLanguage.shortLabel}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.14 }}
            className="absolute right-0 top-11 z-50 w-56 rounded-xl border border-[#EAE3D9] bg-white p-2 shadow-[0_12px_36px_rgba(44,42,41,0.12)]"
          >
            <div className="px-2 pb-2 pt-1 border-b border-[#F4EFEA]">
              <p className="text-[10px] font-bold uppercase tracking-wider text-[#8E8A85]">
                {getLanguageText(value, "Display language")}
              </p>
              <p className="mt-0.5 text-[9px] leading-relaxed text-[#8E8A85]">
                {getLanguageText(value, "Choose the language used by the app interface.")}
              </p>
            </div>

            <div className="pt-1">
              {LANGUAGE_OPTIONS.map((option) => {
                const selected = option.code === value;
                return (
                  <button
                    key={option.code}
                    type="button"
                    onClick={() => {
                      onChange(option.code);
                      setOpen(false);
                    }}
                    className={`w-full rounded-lg px-2.5 py-2 text-left transition-all flex items-center justify-between gap-2 ${
                      selected
                        ? "bg-[#FAF7F2] text-[#7A603E]"
                        : "text-[#615D5A] hover:bg-[#FAF8F5] hover:text-[#2C2A29]"
                    }`}
                  >
                    <span className="flex flex-col">
                      <span className="text-[11px] font-semibold">{option.nativeLabel}</span>
                      <span className="text-[9px] text-[#8E8A85]">{option.label}</span>
                    </span>
                    {selected && <Check className="w-3.5 h-3.5 text-[#967A55]" />}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
