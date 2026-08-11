import React, { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Check, Globe, Search, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { LANGUAGE_OPTIONS, LanguageCode, translate } from "../i18n";

type Props = {
  value: LanguageCode;
  onChange: (value: LanguageCode) => void;
};



export function LanguageSettings({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [pending, setPending] = useState<LanguageCode>(value);
  const [focusIndex, setFocusIndex] = useState(0);

  const searchRef = useRef<HTMLInputElement>(null);
  const optionRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const openRef = useRef(false);
  const pushedRef = useRef(false);

  const active = LANGUAGE_OPTIONS.find((o) => o.code === value) ?? LANGUAGE_OPTIONS[0];
  const t = (zh: string, en: string) => translate(value, zh, en);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return LANGUAGE_OPTIONS;
    return LANGUAGE_OPTIONS.filter(
      (o) =>
        o.nativeLabel.toLowerCase().includes(q) ||
        o.label.toLowerCase().includes(q) ||
        o.code.toLowerCase().includes(q)
    );
  }, [query]);

  useEffect(() => {
    if (focusIndex > filtered.length - 1) setFocusIndex(Math.max(0, filtered.length - 1));
  }, [filtered.length, focusIndex]);

  const doClose = (fromPopstate = false) => {
    if (!openRef.current) return;
    setOpen(false);
    openRef.current = false;
    if (!fromPopstate && pushedRef.current) {
      pushedRef.current = false;
      window.history.back();
    }
    triggerRef.current?.focus();
  };

  const doOpen = () => {
    setPending(value);
    setQuery("");
    setFocusIndex(0);
    setOpen(true);
    openRef.current = true;
    window.setTimeout(() => searchRef.current?.focus(), 60);
    if (!pushedRef.current) {
      window.history.pushState({ langModal: true }, "");
      pushedRef.current = true;
    }
  };

  const apply = () => {
    onChange(pending);
    doClose();
  };

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        doClose();
        return;
      }
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        const target = e.target as HTMLElement | null;
        if (!target || target.tagName === "INPUT") return;
        if (!target.closest('[role="listbox"]')) return;
        e.preventDefault();
        setFocusIndex((i) => {
          const next = e.key === "ArrowDown" ? i + 1 : i - 1;
          const clamped = Math.max(0, Math.min(filtered.length - 1, next));
          const el = optionRefs.current[clamped];
          if (el) {
            el.focus();
            el.scrollIntoView({ block: "nearest" });
          }
          return clamped;
        });
      }
    };
    const onPopState = () => {
      if (openRef.current) {
        pushedRef.current = false;
        setOpen(false);
        openRef.current = false;
        triggerRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("popstate", onPopState);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("popstate", onPopState);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, filtered.length]);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        onClick={doOpen}
        aria-label={t("语言设置", "Language settings")}
        aria-haspopup="dialog"
        className="flex items-center gap-2 rounded-full border border-[#E5E0DA] bg-white/70 px-3 py-1.5 text-sm text-[#3A3633] shadow-sm backdrop-blur transition hover:bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C98A5E]"
      >
        <Globe size={16} />
        <span className="font-medium">{active.shortLabel}</span>
      </button>

      {createPortal(
        <AnimatePresence>
          {open && (
            <motion.div
              className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-[2px] p-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onPointerDown={(e) => {
                if (e.target === e.currentTarget) doClose();
              }}
            >
            <motion.div
              role="dialog"
              aria-modal="true"
              aria-label={t("语言设置", "Language settings")}
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.96, opacity: 0 }}
              transition={{ type: "spring", damping: 28, stiffness: 320 }}
              className="flex max-h-[85vh] w-[92vw] max-w-md flex-col overflow-hidden rounded-2xl bg-[#FBF7F2] shadow-2xl"
            >
              {/* 抓手条：已移除，弹窗统一为居中卡片 */}

              {/* 头部 */}
              <div className="flex items-start justify-between px-5 pb-3 pt-1 sm:pt-5">
                <div className="pr-3">
                  <h2 className="text-lg font-semibold text-[#3A3633]">
                    {t("语言设置", "Language settings")}
                  </h2>
                  <p className="mt-0.5 text-xs text-[#8A837B]">
                    {t("选择应用界面使用的语言。", "Choose the language used by the app interface.")}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => doClose()}
                  aria-label={t("关闭", "Close")}
                  className="rounded-full p-2 text-[#8A837B] transition hover:bg-black/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C98A5E]"
                >
                  <X size={20} />
                </button>
              </div>

              {/* 搜索框 */}
              <div className="px-5 pb-3">
                <div className="flex items-center gap-2 rounded-xl border border-[#E5E0DA] bg-white px-3 py-2">
                  <Search size={16} className="shrink-0 text-[#8A837B]" />
                  <input
                    ref={searchRef}
                    type="text"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setFocusIndex(0);
                    }}
                    placeholder={t("搜索语言...", "Search language...")}
                    aria-label={t("搜索语言...", "Search language...")}
                    className="w-full bg-transparent text-sm text-[#3A3633] outline-none placeholder:text-[#A89F95]"
                  />
                  {query && (
                    <button
                      type="button"
                      onClick={() => {
                        setQuery("");
                        searchRef.current?.focus();
                      }}
                      aria-label={t("清除搜索", "Clear search")}
                      className="shrink-0 text-[#8A837B] transition hover:text-[#3A3633]"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>

              {/* 语言列表（可滚动） */}
              <div
                role="listbox"
                aria-label={t("语言", "Language")}
                className="min-h-0 flex-1 overflow-y-auto px-3 pb-2"
              >
                {filtered.length === 0 ? (
                  <div className="py-10 text-center text-sm text-[#8A837B]">
                    {t("没有相符的语言", "No matching languages")}
                  </div>
                ) : (
                  filtered.map((o, i) => {
                    const selected = o.code === value;
                    const isPending = o.code === pending;
                    return (
                      <button
                        key={o.code}
                        ref={(el) => {
                          optionRefs.current[i] = el;
                        }}
                        type="button"
                        role="option"
                        aria-selected={isPending}
                        onClick={() => {
                          setPending(o.code);
                          setFocusIndex(i);
                          optionRefs.current[i]?.focus();
                        }}
                        onFocus={() => setFocusIndex(i)}
                        className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C98A5E] ${
                          isPending ? "bg-[#EFE7DC]" : "hover:bg-black/5"
                        }`}
                      >
                        <span
                          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white"
                          style={{ backgroundColor: o.color }}
                        >
                          {o.shortLabel}
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-medium text-[#3A3633]">
                            {o.nativeLabel}
                          </span>
                          <span className="block truncate text-xs text-[#8A837B]">{o.label}</span>
                        </span>
                        {selected && <Check size={18} className="shrink-0 text-[#C98A5E]" />}
                      </button>
                    );
                  })
                )}
              </div>

              {/* 底部：取消 / 确认 */}
              <div className="flex gap-3 border-t border-[#E5E0DA] px-5 py-4">
                <button
                  type="button"
                  onClick={() => doClose()}
                  className="flex-1 rounded-xl border border-[#D9D2C9] px-4 py-3 text-sm font-medium text-[#3A3633] transition hover:bg-black/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C98A5E]"
                >
                  {t("取消", "Cancel")}
                </button>
                <button
                  type="button"
                  onClick={apply}
                  className="flex-1 rounded-xl bg-[#C98A5E] px-4 py-3 text-sm font-semibold text-white transition hover:brightness-105 active:brightness-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#A86A3E] focus-visible:ring-offset-2"
                >
                  {t("确认", "Confirm")}
                </button>
              </div>
            </motion.div>
            </motion.div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </>
  );
}
