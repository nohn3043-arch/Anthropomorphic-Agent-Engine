import React, { useState, useEffect, useRef } from "react";
import { 
  Brain, Heart, Activity, ShieldAlert, Zap, Moon, RefreshCw, Clock, 
  Plus, Trash2, Download, AlertTriangle, CheckCircle2, TrendingUp, 
  User, Sparkles, Lock, Settings, HelpCircle, Info, ChevronRight, Play,
  Send, Users, X, Edit3, Check, Minus, Paperclip, Upload, FileText, Sun,
  Image as ImageIcon, Loader2
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import JSZip from "jszip";
import FluidRadar from "./components/FluidRadar";
import { SPLEngine, PsychologicalVector, NarrativeMapper } from "./lib/SPLEngine";
import { renderLanguageStyle, DEFAULT_LANGUAGE_STYLE, type LanguageStyleConfig } from "./lib/LanguageStyleEngine";
import { LanguageSettings } from "./components/LanguageSettings";
import { LanguageCode, getFluidText, getPresetText, normalizeLanguage, translate } from "./i18n";

// Supported AI providers (2026-08 latest mainstream models)
export type ApiProvider =
  | "openai"
  | "claude"
  | "gemini"
  | "deepseek"
  | "glm"
  | "kimi"
  | "qwen"
  | "doubao"
  | "grok"
  | "llama"
  | "nvidia"
  | "local";

export interface AgentPreset {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  descriptionEn: string;
  isCustom?: boolean;
  engineState: {
    psychological_resilience?: number;
    self_esteem?: number;
    energy?: number;
    fluid?: Record<string, number>;
    fluid_baseline?: Record<string, number>;
    fluid_target?: Record<string, number>;
    mood?: Record<string, number>;
    max_trust?: number;
  };
}

// 聊天附件（图片 / 文档等，支持多种格式）
export interface ChatAttachment {
  id: string;
  kind: "image" | "file";
  name: string;
  mime: string;
  size: number;
  dataUrl?: string; // 图片压缩后的 base64 data URL
  text?: string;    // 文档抽取出的正文
}

type ChatMessage = { id: string; role: "user" | "assistant"; content: string; timestamp: string; attachments?: ChatAttachment[] };

const BUILTIN_PRESETS: AgentPreset[] = [
  {
    id: "preset_default",
    name: "默认平衡心智",
    nameEn: "Default Balanced Mind",
    description: "一个心理机能平衡的健康底色，具备中等的心理韧性和自尊恢复率，能合理消解日常心理威胁。",
    descriptionEn: "A healthy psychological background, featuring balanced mental resilience and steady self-esteem recovery. Copes well with typical daily triggers.",
    engineState: {
      psychological_resilience: 0.5,
      self_esteem: 0.5,
      energy: 100,
      max_trust: 1.0,
      fluid_baseline: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1, "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0
      },
      fluid: {
        "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0, "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0
      }
    }
  },
  {
    id: "preset_sensitive",
    name: "高敏感自卑者",
    nameEn: "Highly Sensitive Soul",
    description: "自尊基础脆弱，心理韧性极低。对批评和威胁极度敏感，日常恐惧、愧疚、羞耻处于高位，极难建立对他人的完全信任。",
    descriptionEn: "Fragile self-esteem and very low resilience. Highly sensitive to criticism and threats. Baseline fear, guilt, and shame are elevated.",
    engineState: {
      psychological_resilience: 0.25,
      self_esteem: 0.2,
      energy: 85,
      max_trust: 0.6,
      fluid_baseline: {
        "喜悦": 0.05, "愤怒": 0.1, "恐惧": 0.5, "信任": 0.2, "疏离": 0.5, "张力": 0.4, "愧疚": 0.3, "羞耻": 0.4
      },
      fluid: {
        "喜悦": 0.05, "愤怒": 0.1, "恐惧": 0.5, "信任": 0.2, "疏离": 0.5, "张力": 0.4, "愧疚": 0.3, "羞耻": 0.4
      }
    }
  },
  {
    id: "preset_narcissist",
    name: "自恋防御体",
    nameEn: "Narcissistic Defender",
    description: "拥有膨胀的高自尊与强烈的自我合理化负荷。遇到批评会瞬间将其过滤，或直接外射为强烈的外部愤怒，绝不向内产生愧疚或羞耻。",
    descriptionEn: "Inflated self-esteem backed by powerful defense rationalizations. Blocks criticism or redirects it instantly as externalized anger.",
    engineState: {
      psychological_resilience: 0.65,
      self_esteem: 0.85,
      energy: 100,
      max_trust: 0.8,
      fluid_baseline: {
        "喜悦": 0.4, "愤怒": 0.0, "恐惧": 0.05, "信任": 0.3, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0
      },
      fluid: {
        "喜悦": 0.4, "愤怒": 0.0, "恐惧": 0.05, "信任": 0.3, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0
      }
    }
  },
  {
    id: "preset_distant",
    name: "冷漠避世者",
    nameEn: "Cold & Distant Mind",
    description: "极高疏离，极低信任基线。外界的刺激很难引起内心波动（低张力），采取情感退缩来防御现实威胁，难以建立长期深层羁绊。",
    descriptionEn: "Extremely high alienation with low baseline trust. Retreats emotionally to block threats. Rare emotional spikes, but maintains severe distance.",
    engineState: {
      psychological_resilience: 0.4,
      self_esteem: 0.4,
      energy: 90,
      max_trust: 0.3,
      fluid_baseline: {
        "喜悦": 0.1, "愤怒": 0.05, "恐惧": 0.1, "信任": 0.05, "疏离": 0.8, "张力": 0.05, "愧疚": 0.0, "羞耻": 0.05
      },
      fluid: {
        "喜悦": 0.1, "愤怒": 0.05, "恐惧": 0.1, "信任": 0.05, "疏离": 0.8, "张力": 0.05, "愧疚": 0.0, "羞耻": 0.05
      }
    }
  }
];

export default function App() {
  // Initialize the SPL Psychological Engine and load saved state from LocalStorage if present.
  const [snapshot, setSnapshot] = useState(() => {
    const engine = new SPLEngine();
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_engine_state");
      if (saved) {
        engine.deserialize(saved);
      }
    }
    return {
      engine,
      snap: engine.snapshot()
    };
  });

  // Track active interactive tab (Dashboard vs Chat vs Developer tools)
  const [activeTab, setActiveTab] = useState<"dashboard" | "chat" | "dev_tools">("chat");
  const [showApiConfig, setShowApiConfig] = useState(false);
  const [showRawPrompt, setShowRawPrompt] = useState(false);

  // ===== 深色模式（持久化到 localStorage，初始从 <html> 上的 .dark 类读取）=====
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return document.documentElement.classList.contains("dark");
    }
    return false;
  });
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) root.classList.add("dark");
    else root.classList.remove("dark");
    try { localStorage.setItem("spl_dark_mode", isDark ? "1" : "0"); } catch {}
  }, [isDark]);
  const toggleDark = () => setIsDark((v) => !v);

  // First-run tutorial (3 steps, skippable). null = dismissed / already seen.
  const [tutorialStep, setTutorialStep] = useState<number | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("spl_tutorial_done") ? null : 1;
    }
    return null;
  });
  const dismissTutorial = () => {
    if (typeof window !== "undefined") localStorage.setItem("spl_tutorial_done", "1");
    setTutorialStep(null);
  };

  // Pre-defined and custom agents states
  const [customAgents, setCustomAgents] = useState<AgentPreset[]>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_custom_agents");
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  });

  const [activeAgentId, setActiveAgentId] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("spl_active_agent_id") || "preset_default";
    }
    return "preset_default";
  });

  // 语言风格配置（按智能体ID存储于 localStorage；View 层：状态 → 语言指令）
  const [languageStyles, setLanguageStyles] = useState<Record<string, LanguageStyleConfig>>(() => {
    try {
      const saved = localStorage.getItem("spl_language_styles");
      return saved ? (JSON.parse(saved) as Record<string, LanguageStyleConfig>) : {};
    } catch { return {}; }
  });
  const activeLanguageStyle: LanguageStyleConfig = languageStyles[String(activeAgentId ?? "")] || DEFAULT_LANGUAGE_STYLE;
  const updateLanguageStyle = (patch: Partial<LanguageStyleConfig>) => {
    setLanguageStyles((prev) => {
      const key = String(activeAgentId ?? "");
      const merged = { ...prev, [key]: { ...(prev[key] || DEFAULT_LANGUAGE_STYLE), ...patch } };
      localStorage.setItem("spl_language_styles", JSON.stringify(merged));
      return merged;
    });
  };
  const languageStylePromptSection = () => {
    try { return "\n\n" + renderLanguageStyle(snapshot.snap, activeLanguageStyle); } catch { return ""; }
  };

  // State to manage the expandable JSON input section
  const [isImporting, setIsImporting] = useState(false);
  const [jsonInput, setJsonInput] = useState(() => {
    return JSON.stringify({
      name: "傲娇大小姐 (Tsundere)",
      nameEn: "Tsundere Queen",
      description: "自尊极高，天然伴随极高张力与极度疏离。对外部刺激经常采用防御层过滤，极难产生信任，但一旦被逗乐（喜悦上升）会展现极高亲和性反差。",
      descriptionEn: "Highly sensitive self-esteem paired with high baseline tension and alienation. Highly defensive and tsundere-like, but spikes in joy yield cute affiliation.",
      engineState: {
        psychological_resilience: 0.35,
        self_esteem: 0.8,
        energy: 95,
        max_trust: 0.5,
        fluid_baseline: {
          "喜悦": 0.05,
          "愤怒": 0.2,
          "恐惧": 0.1,
          "信任": 0.1,
          "疏离": 0.7,
          "张力": 0.6,
          "愧疚": 0.0,
          "羞耻": 0.1
        },
        fluid: {
          "喜悦": 0.05,
          "愤怒": 0.2,
          "恐惧": 0.1,
          "信任": 0.1,
          "疏离": 0.7,
          "张力": 0.6,
          "愧疚": 0.0,
          "羞耻": 0.1
        }
      }
    }, null, 2);
  });

  // Agent List Modal states
  const [isAgentListOpen, setIsAgentListOpen] = useState(false);
  const [editingAgentId, setEditingAgentId] = useState<string | null>(null);
  const [editingJson, setEditingJson] = useState("");

  // Draggable agent panel state
  const agentPanelRef = useRef<HTMLDivElement>(null);
  const dragOffsetRef = useRef({ x: 0, y: 0 });
  const dragCleanupRef = useRef<(() => void) | null>(null);
  const [agentPanelPos, setAgentPanelPos] = useState<{ x: number; y: number } | null>(null);
  const [agentPanelMinimized, setAgentPanelMinimized] = useState(false);

  const handlePanelDragStart = (e: React.MouseEvent | React.TouchEvent) => {
    // Don't drag if clicked on a button inside header
    const target = e.target as HTMLElement;
    if (target.closest("button")) return;

    const clientX = "touches" in e ? e.touches[0].clientX : e.clientX;
    const clientY = "touches" in e ? e.touches[0].clientY : e.clientY;
    const rect = agentPanelRef.current?.getBoundingClientRect();
    if (!rect) return;

    // First-time drag: capture current rendered position as origin
    if (agentPanelPos === null) {
      setAgentPanelPos({ x: rect.left, y: rect.top });
    }
    dragOffsetRef.current = { x: clientX - rect.left, y: clientY - rect.top };

    const onMove = (ev: MouseEvent | TouchEvent) => {
      const cx = "touches" in ev
        ? (ev as TouchEvent).touches[0].clientX
        : (ev as MouseEvent).clientX;
      const cy = "touches" in ev
        ? (ev as TouchEvent).touches[0].clientY
        : (ev as MouseEvent).clientY;
      const newX = cx - dragOffsetRef.current.x;
      const newY = cy - dragOffsetRef.current.y;
      const panelW = agentPanelRef.current?.offsetWidth || 320;
      const panelH = agentPanelRef.current?.offsetHeight || 200;
      const maxX = window.innerWidth - Math.min(panelW, 120);
      const maxY = window.innerHeight - Math.min(panelH, 60);
      const clampedX = Math.max(0, Math.min(newX, maxX));
      const clampedY = Math.max(0, Math.min(newY, maxY));
      // 直接操作 DOM，避免 React 重渲染导致的拖拽卡顿
      const el = agentPanelRef.current;
      if (el) {
        el.style.left = `${clampedX}px`;
        el.style.top = `${clampedY}px`;
      }
    };
    const cleanup = () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
      document.removeEventListener("touchmove", onMove);
      document.removeEventListener("touchend", onUp);
      if (dragCleanupRef.current === cleanup) {
        dragCleanupRef.current = null;
      }
    };
    const onUp = () => {
      // 拖拽结束后同步最终位置到 React state
      const el = agentPanelRef.current;
      if (el) {
        const left = parseFloat(el.style.left) || 0;
        const top = parseFloat(el.style.top) || 0;
        setAgentPanelPos({ x: left, y: top });
      }
      cleanup();
    };
    dragCleanupRef.current = cleanup;
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
    document.addEventListener("touchmove", onMove);
    document.addEventListener("touchend", onUp);
  };

  // Core i18n language state
  const [lang, setLang] = useState<LanguageCode>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_lang");
      return normalizeLanguage(saved);
    }
    return "zh-CN";
  });

  // API Config and Chat states
  const [apiProvider, setApiProvider] = useState<ApiProvider>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("spl_api_provider") as any) || "local";
    }
    return "local";
  });
  const [apiKey, setApiKey] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("spl_api_key") || "";
    }
    return "";
  });
  const [apiModel, setApiModel] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("spl_api_model") || "";
    }
    return "";
  });
  const [apiBaseUrl, setApiBaseUrl] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("spl_api_base_url") || "";
    }
    return "";
  });

  // Conversation style preferences (auto-adjust API params + system prompt)
  const [prefStyle, setPrefStyle] = useState<"creative" | "balanced" | "strict">(() => {
    if (typeof window !== "undefined") {
      const v = localStorage.getItem("spl_pref_style");
      if (v === "creative" || v === "strict" || v === "balanced") return v;
    }
    return "balanced";
  });
  const [prefLength, setPrefLength] = useState<"short" | "medium" | "long">(() => {
    if (typeof window !== "undefined") {
      const v = localStorage.getItem("spl_pref_length");
      if (v === "short" || v === "long" || v === "medium") return v;
    }
    return "medium";
  });
  const [prefTone, setPrefTone] = useState<"gentle" | "rational" | "humorous">(() => {
    if (typeof window !== "undefined") {
      const v = localStorage.getItem("spl_pref_tone");
      if (v === "gentle" || v === "rational" || v === "humorous") return v;
    }
    return "gentle";
  });

  // Map user preferences to concrete API parameters
  const getPrefConfig = () => {
    const temperature = prefStyle === "creative" ? 0.95 : prefStyle === "strict" ? 0.3 : 0.7;
    const maxTokens = prefLength === "short" ? 512 : prefLength === "long" ? 8192 : 2048;
    return { temperature, maxTokens };
  };

  // Build the style preference section injected into the system prompt
  const getPrefPromptSection = () => {
    const style = prefStyle === "creative"
      ? "imaginative and exploratory, freely branching ideas and associations"
      : prefStyle === "strict"
        ? "logical, precise and grounded, minimizing speculation"
        : "balanced between creativity and rigor";
    const length = prefLength === "short"
      ? "reply briefly, usually 1-2 short sentences"
      : prefLength === "long"
        ? "reply in detail, expanding with depth and concrete examples"
        : "reply in moderate length, usually 1-3 short paragraphs";
    const tone = prefTone === "gentle"
      ? "warm, gentle and soothing"
      : prefTone === "humorous"
        ? "playful, witty and humorous when appropriate"
        : "calm, rational and clear-headed";
    return `\n\n[USER STYLE PREFERENCES — apply to your replies]\n- Style: ${style}.\n- Length: ${length}.\n- Tone: ${tone}.`;
  };

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_chat_messages");
      if (saved) {
        const parsed = JSON.parse(saved) as ChatMessage[];
        // 迁移旧版本硬编码双语欢迎语 → 新版本单语欢迎语
        const welcome = parsed.find((m) => m.id === "welcome");
        if (welcome && welcome.content.includes("\n\nHello")) {
          welcome.content = translate(lang, "您好，我是由 SPL 心理流体推理引擎 V8.0 驱动的智能人格。我的语气、同理心与思考深度将完全受到我当前实时心理状态（能量、自尊、心境、创伤等）的约束与塑造。请随意与我对话，或者测试我的心理反应。", "Hello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My tone, empathy, and depth of thought are completely shaped and constrained by my real-time psychological states. Feel free to talk to me or test my cognitive responses.");
        }
        return parsed;
      }
    }
    return [
      {
        id: "welcome",
        role: "assistant",
        content: translate(lang, "您好，我是由 SPL 心理流体推理引擎 V8.0 驱动的智能人格。我的语气、同理心与思考深度将完全受到我当前实时心理状态（能量、自尊、心境、创伤等）的约束与塑造。请随意与我对话，或者测试我的心理反应。", "Hello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My tone, empathy, and depth of thought are completely shaped and constrained by my real-time psychological states. Feel free to talk to me or test my cognitive responses."),
        timestamp: new Date().toLocaleTimeString()
      }
    ];
  });
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // 聊天框附件（文件/图片，支持多种格式）
  const [chatAttachments, setChatAttachments] = useState<ChatAttachment[]>([]);
  const chatFileInputRef = useRef<HTMLInputElement>(null);

  // AI 智能导入角色（Word/Excel/TXT/Markdown → 大模型识别 → JSON → 新 agent）
  const [isAiImporting, setIsAiImporting] = useState(false);
  const aiImportInputRef = useRef<HTMLInputElement>(null);

  // Sync translation toggle back to localstorage
  useEffect(() => {
    localStorage.setItem("spl_lang", lang);
  }, [lang]);

  // Sync messages
  useEffect(() => {
    localStorage.setItem("spl_chat_messages", JSON.stringify(chatMessages));
  }, [chatMessages]);

  // Translate helper function
  const t = (zh: string, en: string) => translate(lang, zh, en);
  const isSimplifiedChinese = lang === "zh-CN";
  const getAgentDisplay = (preset: AgentPreset) => getPresetText(lang, preset);
  const getAgentName = (preset: AgentPreset) => getAgentDisplay(preset).name;
  const getAgentDescription = (preset: AgentPreset) => getAgentDisplay(preset).description;

  // Default provider configs
  const getDefaultConfig = (provider: ApiProvider) => {
    switch (provider) {
      case "openai":
        return { model: "gpt-5.5", url: "https://api.openai.com/v1" };
      case "claude":
        return { model: "claude-sonnet-5", url: "https://api.anthropic.com/v1" };
      case "gemini":
        return { model: "gemini-3.6-flash", url: "https://generativelanguage.googleapis.com" };
      case "deepseek":
        return { model: "deepseek-v4-flash", url: "https://api.deepseek.com" };
      case "glm":
        return { model: "glm-5.3", url: "https://open.bigmodel.cn/api/paas/v4" };
      case "kimi":
        return { model: "kimi-k2.6", url: "https://api.moonshot.cn/v1" };
      case "qwen":
        return { model: "qwen3.8-max", url: "https://dashscope.aliyuncs.com/compatible-mode/v1" };
      case "doubao":
        return { model: "doubao-seed-2.1-pro", url: "https://ark.cn-beijing.volces.com/api/v3" };
      case "grok":
        return { model: "grok-4", url: "https://api.x.ai/v1" };
      case "llama":
        return { model: "meta-llama/Llama-4-70B-Chat", url: "https://api.together.xyz/v1" };
      case "nvidia":
        return { model: "nvidia/llama-3.1-nemotron-70b-instruct", url: "https://integrate.api.nvidia.com/v1" };
      case "local":
        return { model: "qwen3", url: "http://localhost:11434/v1" };
    }
  };

  // Custom vector inputs
  const [customThreat, setCustomThreat] = useState(0);
  const [customBelonging, setCustomBelonging] = useState(0);
  const [customAutonomy, setCustomAutonomy] = useState(0);
  const [customFatigue, setCustomFatigue] = useState(0);
  const [customShame, setCustomShame] = useState(0);
  const [customEventId, setCustomEventId] = useState("");

  // Custom expectation inputs
  const [expEventId, setExpEventId] = useState("");
  const [expValence, setExpValence] = useState(0.5); // Hope (+0.5) to Fear (-0.5)
  const [expConfidence, setExpConfidence] = useState(0.5);

  // Time acceleration factor
  const [idleSeconds, setIdleSeconds] = useState(60);

  // Sleep hours selector
  const [sleepHours, setSleepHours] = useState(8);

  // Custom notifications / event triggers log for the UI
  const [notifications, setNotifications] = useState<Array<{ id: string; text: string; type: string; time: string }>>([]);

  // Active help modal for core fluid details
  const [selectedFluidHelp, setSelectedFluidHelp] = useState<string | null>(null);

  // Sync snapshot and trigger LocalStorage save on change
  const updateEngineState = (callback?: (engine: SPLEngine) => void) => {
    setSnapshot((prev) => {
      const engine = prev.engine;
      if (callback) {
        callback(engine);
      }
      // Force continuous time update slightly to reconcile states
      engine._advanceTime();
      localStorage.setItem("spl_engine_state", engine.serialize());
      return {
        engine,
        snap: engine.snapshot()
      };
    });
  };

  // Add event alert to notifications panel
  const addNotification = (text: string, type: "info" | "warning" | "error" | "success" = "info") => {
    setNotifications((prev) => [
      {
        id: Math.random().toString(36).substring(7),
        text,
        type,
        time: new Date().toLocaleTimeString()
      },
      ...prev.slice(0, 19) // Keep last 20
    ]);
  };

  // Periodic automatic clock tick (advances continuous decay/forgetting processes)
  useEffect(() => {
    const interval = setInterval(() => {
      updateEngineState();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Listen to bursts or trauma events within the engine and push notifications
  const lastBurstCount = useRef(snapshot.snap.burst_events?.length || 0);
  useEffect(() => {
    const currentBursts = snapshot.snap.burst_events || [];
    if (currentBursts.length > lastBurstCount.current) {
      const newBursts = currentBursts.slice(lastBurstCount.current);
      newBursts.forEach((b: any) => {
        let typeStr: "warning" | "error" | "info" = "warning";
        if (b.type === "avalanche") typeStr = "error";
        if (b.type === "suppression") typeStr = "error";
        addNotification(`⚠️ [${t("爆发", "Burst")}] ${b.detail}`, typeStr);
      });
      lastBurstCount.current = currentBursts.length;
    }
  }, [snapshot.snap.burst_events]);

  // Handle stimulus triggers
  const handleTriggerEvent = (eventName: string, label: string) => {
    updateEngineState((engine) => {
      engine.processEvent(eventName, 1.0);
    });
    addNotification(`⚡️ ${t("触发事件", "Trigger event")}: ${label}`, "success");
  };

  // Handle Custom Vector Injection
  const handleInjectCustomVector = () => {
    const vec: PsychologicalVector = {};
    if (customThreat !== 0) vec.threat = customThreat;
    if (customBelonging !== 0) vec.belonging = customBelonging;
    if (customAutonomy !== 0) vec.autonomy = customAutonomy;
    if (customFatigue !== 0) vec.fatigue = customFatigue;
    if (customShame !== 0) vec.shame_trigger = customShame;

    updateEngineState((engine) => {
      engine.processVector(vec, 1.0, customEventId);
    });

    addNotification(
      `🧪 ${t("注入自定义内感受向量", "Inject custom interoceptive vector")}: [T:${customThreat.toFixed(1)} B:${customBelonging.toFixed(1)} A:${customAutonomy.toFixed(1)} F:${customFatigue.toFixed(1)} S:${customShame.toFixed(1)}] ${customEventId ? `(EventID: "${customEventId}")` : ""}`,
      "info"
    );

    // Reset sliders
    setCustomThreat(0);
    setCustomBelonging(0);
    setCustomAutonomy(0);
    setCustomFatigue(0);
    setCustomShame(0);
    setCustomEventId("");
  };

  // Handle Setting Expectation
  const handleSetExpectation = (e: React.FormEvent) => {
    e.preventDefault();
    if (!expEventId.trim()) {
      addNotification(`❌ ${t("预期事件 ID 不能为空", "Expectation event ID cannot be empty")}`, "error");
      return;
    }

    updateEngineState((engine) => {
      engine.expect(expEventId, expValence, expConfidence);
    });

    addNotification(
      `🔮 ${t("设定未来预期", "Set future expectation")}: "${expEventId}" (${t("效价", "Valence")}: ${expValence > 0 ? `${t("期待 +", "Expecting +")}${expValence}` : `${t("担忧", "Worrying")} ${expValence}`}, ${t("确信度", "Confidence")}: ${Math.round(expConfidence * 100)}%)`,
      "info"
    );

    setExpEventId("");
  };

  // Handle Sleep
  const handleSleepSimulation = () => {
    updateEngineState((engine) => {
      engine.sleep(sleepHours);
    });
    addNotification(`💤 ${t("模拟睡眠", "Simulate sleep")} ${sleepHours} ${t("小时", "hours")}：${t("进行 REM 梦境情绪重构、创伤修复与恐惧消退", "Run REM dream emotional reconstruction, trauma repair and fear extinction")}`, "success");
  };

  // Handle Idle/Fast forward
  const handleIdleSimulation = (seconds: number) => {
    updateEngineState((engine) => {
      engine.idle(seconds);
    });
    const unit = seconds >= 3600 ? `${(seconds / 3600).toFixed(1)} ${t("小时", "hours")}` : seconds >= 60 ? `${(seconds / 60).toFixed(1)} ${t("分钟", "minutes")}` : `${seconds} ${t("秒", "seconds")}`;
    addNotification(`⏳ ${t("顺延时间流逝", "Time elapsed")} ${unit} (${t("模拟艾宾浩斯遗忘与情绪流体弛豫", "Simulate Ebbinghaus forgetting and emotional fluid relaxation")})`, "info");
  };

  // Get unified list of builtin and custom user-designed agents
  const getAgentsList = (): AgentPreset[] => {
    return [...BUILTIN_PRESETS, ...customAgents];
  };

  const getActiveAgent = (): AgentPreset => {
    const list = getAgentsList();
    return list.find(a => a.id === activeAgentId) || list[0];
  };

  // Re-instantiate the engine with selected preset baselines and clear memories/traumas
  const loadAgentPreset = (preset: AgentPreset) => {
    const engine = new SPLEngine();
    
    const s = preset.engineState;
    if (s.psychological_resilience !== undefined) engine.psychological_resilience = s.psychological_resilience;
    if (s.self_esteem !== undefined) engine.self_esteem = s.self_esteem;
    if (s.energy !== undefined) engine.energy = s.energy;
    if (s.max_trust !== undefined) engine.max_trust = s.max_trust;
    
    if (s.fluid) {
      engine.fluid = { ...engine.fluid, ...s.fluid };
    }
    if (s.fluid_baseline) {
      engine.fluid_baseline = { ...engine.fluid_baseline, ...s.fluid_baseline };
    }
    if (s.fluid_target) {
      engine.fluid_target = { ...engine.fluid_target, ...s.fluid_target };
    }
    if (s.mood) {
      engine.mood = { ...engine.mood, ...s.mood };
    }

    // Save state and set active ID to localstorage
    localStorage.setItem("spl_engine_state", engine.serialize());
    localStorage.setItem("spl_active_agent_id", preset.id);
    
    setSnapshot({
      engine,
      snap: engine.snapshot()
    });
    
    setActiveAgentId(preset.id);
    addNotification(
      `🎭 ${t("心理人格已切换为", "Psychological agent switched to")}: ${getAgentName(preset)}`,
      "success"
    );
  };

  // Delete a user-designed custom agent
  const handleDeleteCustomAgent = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(t("确定要删除这个自定义人格吗？", "Are you sure you want to delete this custom personality?"))) {
      const updated = customAgents.filter(a => a.id !== id);
      setCustomAgents(updated);
      localStorage.setItem("spl_custom_agents", JSON.stringify(updated));
      
      // If we deleted the active one, load the default balanced mind
      if (activeAgentId === id) {
        loadAgentPreset(BUILTIN_PRESETS[0]);
      } else {
        addNotification(`🗑️ ${t("自定义人格已删除", "Custom personality deleted")}`, "info");
      }
    }
  };

  // Parse and import a user-supplied JSON config as a custom agent
  const handleImportJson = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(jsonInput);
      if (!parsed.name || !parsed.nameEn || !parsed.description || !parsed.descriptionEn) {
        throw new Error("Missing required fields: 'name', 'nameEn', 'description', or 'descriptionEn'.");
      }
      if (!parsed.engineState) {
        throw new Error("Missing 'engineState' object containing preset values.");
      }
      
      const newPreset: AgentPreset = {
        id: "custom_" + Date.now(),
        name: parsed.name,
        nameEn: parsed.nameEn,
        description: parsed.description,
        descriptionEn: parsed.descriptionEn,
        isCustom: true,
        engineState: parsed.engineState
      };

      const updated = [...customAgents, newPreset];
      setCustomAgents(updated);
      localStorage.setItem("spl_custom_agents", JSON.stringify(updated));
      
      loadAgentPreset(newPreset);
      setIsImporting(false);
      addNotification(
        t("📥 成功导入并激活自定义人格！", "📥 Custom personality successfully imported and activated!"), 
        "success"
      );
    } catch (err: any) {
      alert(`❌ ${t("JSON 解析/校验错误", "JSON Parse/Validation Error")}: ${err.message}`);
    }
  };

  // ========== 文件 / 图片 / 附件工具 ==========
  const readFileAsDataUrl = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });

  const readFileAsText = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file, "utf-8");
    });

  // 压缩图片（限制长边 + 转码），避免 localStorage 体积爆炸
  const downscaleImage = (dataUrl: string, maxEdge = 1280, quality = 0.8): Promise<string> =>
    new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const scale = Math.min(1, maxEdge / Math.max(img.width, img.height));
        const w = Math.max(1, Math.round(img.width * scale));
        const h = Math.max(1, Math.round(img.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        if (!ctx) { resolve(dataUrl); return; }
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL(dataUrl.startsWith("data:image/png") ? "image/png" : "image/jpeg", quality));
      };
      img.onerror = () => resolve(dataUrl);
      img.src = dataUrl;
    });

  // 解析 .docx（基于 jszip 读取 word/document.xml 中的文本节点）
  const extractDocxText = async (file: File): Promise<string> => {
    const zip = await JSZip.loadAsync(await file.arrayBuffer());
    const xml = await zip.file("word/document.xml")?.async("string");
    if (!xml) throw new Error("无法解析 docx（缺少 document.xml）");
    const texts: string[] = [];
    const regex = /<w:t[^>]*>([\s\S]*?)<\/w:t>/g;
    let m: RegExpExecArray | null;
    while ((m = regex.exec(xml)) !== null) {
      texts.push(m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'"));
    }
    return texts.join("\n");
  };

  // 解析 .xlsx（基于 jszip 读取 sharedStrings + worksheets 表格文本）
  const extractXlsxText = async (file: File): Promise<string> => {
    const zip = await JSZip.loadAsync(await file.arrayBuffer());
    const sharedStrs: string[] = [];
    const sharedXml = await zip.file("xl/sharedStrings.xml")?.async("string");
    if (sharedXml) {
      const siRegex = /<si>[\s\S]*?<t[^>]*>([\s\S]*?)<\/t>[\s\S]*?<\/si>/g;
      let m: RegExpExecArray | null;
      while ((m = siRegex.exec(sharedXml)) !== null) {
        sharedStrs.push(m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'"));
      }
    }
    const sheetFiles = Object.keys(zip.files)
      .filter((f) => f.startsWith("xl/worksheets/sheet") && f.endsWith(".xml"))
      .sort();
    const rows: string[] = [];
    for (const sf of sheetFiles) {
      const xml = await zip.file(sf)?.async("string");
      if (!xml) continue;
      const rowRegex = /<row[^>]*>([\s\S]*?)<\/row>/g;
      let rm: RegExpExecArray | null;
      while ((rm = rowRegex.exec(xml)) !== null) {
        const cells: string[] = [];
        const cRegex = /<c\b([^>]*)>([\s\S]*?)<\/c>/g;
        let cm: RegExpExecArray | null;
        while ((cm = cRegex.exec(rm[1])) !== null) {
          const tag = cm[1] || "";
          const inner = cm[2] || "";
          const tAttr = (tag.match(/\bt="([^"]*)"/) || [])[1] || "";
          let val = "";
          if (tAttr === "s") {
            const idx = parseInt((inner.match(/<v>(\d+)<\/v>/) || [])[1] || "0", 10);
            val = sharedStrs[idx] ?? "";
          } else if (tAttr === "inlineStr") {
            const mt = inner.match(/<t[^>]*>([\s\S]*?)<\/t>/);
            val = mt ? mt[1] : "";
          } else {
            val = (inner.match(/<v>([\s\S]*?)<\/v>/) || [])[1] || "";
          }
          val = val.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'");
          cells.push(val);
        }
        rows.push(cells.join("\t"));
      }
    }
    return rows.join("\n");
  };

  // 解析 .pptx（基于 jszip 读取 ppt/slides/slideN.xml 中的 <a:t> 文本节点）
  const extractPptxText = async (file: File): Promise<string> => {
    const zip = await JSZip.loadAsync(await file.arrayBuffer());
    const slideFiles = Object.keys(zip.files)
      .filter((f) => /^ppt\/slides\/slide\d+\.xml$/.test(f))
      .sort((a, b) => parseInt((a.match(/slide(\d+)\.xml$/) || [])[1] || "0", 10) - parseInt((b.match(/slide(\d+)\.xml$/) || [])[1] || "0", 10));
    const out: string[] = [];
    for (const sf of slideFiles) {
      const xml = await zip.file(sf)?.async("string");
      if (!xml) continue;
      const texts: string[] = [];
      const regex = /<a:t>([\s\S]*?)<\/a:t>/g;
      let m: RegExpExecArray | null;
      while ((m = regex.exec(xml)) !== null) {
        texts.push(m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'"));
      }
      if (texts.length) out.push(texts.join(" "));
    }
    return out.join("\n");
  };
  // 从任意文件构建 ChatAttachment（图片压缩、文档抽取正文、其余仅保留文件名）
  const buildAttachmentFromFile = async (file: File): Promise<ChatAttachment> => {
    const base: ChatAttachment = {
      id: Math.random().toString(36).substring(7),
      kind: "file",
      name: file.name,
      mime: file.type || "application/octet-stream",
      size: file.size
    };
    const fname = file.name.toLowerCase();
    if (file.type.startsWith("image/") || /\.(png|jpe?g|gif|webp|bmp|avif)$/.test(fname)) {
      const raw = await readFileAsDataUrl(file);
      const dataUrl = await downscaleImage(raw);
      const isPng = dataUrl.startsWith("data:image/png");
      return { ...base, kind: "image", mime: isPng ? "image/png" : "image/jpeg", dataUrl };
    }
    if (/\.(txt|md|markdown|csv|json|log|ini|yml|yaml|xml|html)$/.test(fname) || file.type.startsWith("text/")) {
      const text = await readFileAsText(file);
      return { ...base, text };
    }
    if (fname.endsWith(".docx")) {
      const text = await extractDocxText(file);
      return { ...base, text };
    }
    if (fname.endsWith(".xlsx")) {
      const text = await extractXlsxText(file);
      return { ...base, text };
    }
    if (fname.endsWith(".pptx")) {
      const text = await extractPptxText(file);
      return { ...base, text };
    }
    return base; // 其余二进制格式：仅携带文件名
  };

  // 聊天框选择附件
  const handleChatAttach = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    e.target.value = "";
    if (!fileList || fileList.length === 0) return;
    const files: File[] = [];
    for (let i = 0; i < fileList.length; i++) files.push(fileList[i] as File);
    const accepted: ChatAttachment[] = [];
    for (const f of files) {
      if (f.size > 15 * 1024 * 1024) {
        addNotification(`${f.name} ${t("超过 15MB，已跳过", "exceeds 15MB, skipped")}`, "warning");
        continue;
      }
      try {
        accepted.push(await buildAttachmentFromFile(f));
      } catch (err: any) {
        addNotification(`${t("读取文件失败", "Failed to read file")}: ${f.name} (${err.message})`, "error");
      }
    }
    setChatAttachments((prev) => [...prev, ...accepted]);
    if (accepted.length > 0) {
      addNotification(`${t("已添加", "Attached")} ${accepted.length} ${t("个附件", "file(s)")}`, "info");
    }
  };

  const removeChatAttachment = (id: string) => {
    setChatAttachments((prev) => prev.filter((a) => a.id !== id));
  };

  // 将带附件的用户消息转为 OpenAI 兼容 content（文本 + image_url / 附件正文）
  const buildOpenAIContent = (msg: ChatMessage): string | Array<any> => {
    if (!msg.attachments || msg.attachments.length === 0) return msg.content;
    const parts: any[] = [];
    if (msg.content) parts.push({ type: "text", text: msg.content });
    for (const att of msg.attachments) {
      if (att.kind === "image" && att.dataUrl) {
        parts.push({ type: "image_url", image_url: { url: att.dataUrl } });
      } else {
        parts.push({ type: "text", text: att.text ? `[附件: ${att.name}]\n${att.text}` : `[附件: ${att.name}（无法在本端解析正文）]` });
      }
    }
    return parts;
  };

  // Claude 多模态 content
  const buildClaudeContent = (msg: ChatMessage): string | Array<any> => {
    if (!msg.attachments || msg.attachments.length === 0) return msg.content;
    const parts: any[] = [];
    if (msg.content) parts.push({ type: "text", text: msg.content });
    for (const att of msg.attachments) {
      if (att.kind === "image" && att.dataUrl) {
        parts.push({ type: "image", source: { type: "base64", media_type: att.mime || "image/jpeg", data: (att.dataUrl.split(",")[1] || "") } });
      } else {
        parts.push({ type: "text", text: att.text ? `[附件: ${att.name}]\n${att.text}` : `[附件: ${att.name}（无法在本端解析正文）]` });
      }
    }
    return parts;
  };

  // Gemini 多模态 parts
  const buildGeminiParts = (msg: ChatMessage): Array<any> => {
    if (!msg.attachments || msg.attachments.length === 0) return [{ text: msg.content }];
    const parts: any[] = [];
    if (msg.content) parts.push({ text: msg.content });
    for (const att of msg.attachments) {
      if (att.kind === "image" && att.dataUrl) {
        parts.push({ inline_data: { mime_type: att.mime || "image/jpeg", data: (att.dataUrl.split(",")[1] || "") } });
      } else {
        parts.push({ text: att.text ? `[附件: ${att.name}]\n${att.text}` : `[附件: ${att.name}（无法在本端解析正文）]` });
      }
    }
    return parts;
  };

  // 统一的大模型文本调用（供 AI 智能导入使用）
  const callLLM = async (
    messages: Array<{ role: "user" | "assistant" | "system"; content: string }>,
    temperature = 0.3
  ): Promise<string> => {
    const activeKey = apiKey.trim();
    const activeModel = apiModel.trim() || getDefaultConfig(apiProvider).model;
    const activeUrl = apiBaseUrl.trim() || getDefaultConfig(apiProvider).url;

    if (apiProvider === "claude") {
      const res = await fetch(`${activeUrl}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-api-key": activeKey, "anthropic-version": "2023-06-01", "dangerously-allow-browser": "true" },
        body: JSON.stringify({
          model: activeModel,
          system: messages.filter((m) => m.role === "system").map((m) => m.content).join("\n"),
          messages: messages.filter((m) => m.role !== "system").map((m) => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content })),
          max_tokens: 8192,
          temperature
        })
      });
      if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d?.error?.message || `HTTP ${res.status}`); }
      const data = await res.json();
      return data.content?.[0]?.text || "";
    }
    if (apiProvider === "gemini") {
      const modelEndpoint = activeModel.includes("/") ? activeModel : `models/${activeModel}`;
      const url = `${activeUrl}/v1beta/${modelEndpoint}:generateContent?key=${activeKey}`;
      const contents = messages.map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] }));
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents, generationConfig: { temperature } })
      });
      if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d?.error?.message || `HTTP ${res.status}`); }
      const data = await res.json();
      return data.candidates?.[0]?.content?.parts?.map((p: any) => p.text || "").join("") || "";
    }
    // OpenAI 兼容（openai / local / deepseek / kimi / qwen / doubao / grok / llama / nvidia）
    const res = await fetch(`${activeUrl}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${activeKey}` },
      body: JSON.stringify({ model: activeModel, messages: messages.map((m) => ({ role: m.role, content: m.content })), temperature })
    });
    if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d?.error?.message || `HTTP ${res.status}`); }
    const data = await res.json();
    return data.choices?.[0]?.message?.content || "";
  };

  // AI 智能导入：Word/Excel/TXT/Markdown 等角色文档 → 大模型自动识别 → 回填 JSON → 生成新智能体
  const handleAiImportFile = async (file: File) => {
    const fname = file.name.toLowerCase();
    if (/\.(png|jpe?g|gif|webp|bmp|avif)$/.test(fname) || file.type.startsWith("image/")) {
      addNotification(
        t("AI 智能导入暂不支持图片，请上传 .txt/.md/.csv/.json/.docx/.xlsx/.pptx 角色文档", "AI import does not support images yet. Please upload .txt/.md/.csv/.json/.docx/.xlsx persona documents."),
        "warning"
      );
      return;
    }
    try {
      const att = await buildAttachmentFromFile(file);
      let content = att.text || "";
      if (!content.trim()) {
        content = await readFileAsText(file).catch(() => "");
      }
      if (!content.trim()) {
        addNotification(
          t("无法从该文件中提取文本（支持 .txt/.md/.csv/.json/.docx/.xlsx/.pptx）", "Could not extract text from this file (supported: .txt/.md/.csv/.json/.docx/.xlsx)."),
          "error"
        );
        return;
      }
      if (content.length > 60000) content = content.slice(0, 60000) + "\n...[" + t("已截断", "truncated") + "]";

      const schemaExample = JSON.stringify({
        name: "角色名（中文）",
        nameEn: "English / Pinyin name",
        description: "角色的心理画像、性格、说话风格与背景（中文）",
        descriptionEn: "English description of the persona",
        engineState: {
          psychological_resilience: 0.5,
          self_esteem: 0.5,
          energy: 80,
          max_trust: 0.5,
          fluid_baseline: { "喜悦": 0.2, "愤怒": 0.1, "恐惧": 0.1, "信任": 0.3, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0 },
          fluid: { "喜悦": 0.2, "愤怒": 0.1, "恐惧": 0.1, "信任": 0.3, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0, "羞耻": 0.0 }
        }
      }, null, 2);

      const prompt = `你是角色设定解析器。下面是一份用户提供的“角色 / 人格 / 人设”设定文档（可能来自 Word、Excel、TXT、Markdown 等）。\n请从中识别并提炼该角色的核心人格特征，然后输出一个 JSON 对象，用于生成 SPL 心理流体引擎的自定义智能体。\n\nJSON 字段规范（engineState 中 8 个流体键必须完整包含：喜悦、愤怒、恐惧、信任、疏离、张力、愧疚、羞耻，取值范围 0~1）：\n${schemaExample}\n\n要求：\n1. 只输出一个合法 JSON 对象，不要输出任何解释、Markdown 代码块或其他文字。\n2. name 用角色名（中文），nameEn 用英文名或拼音。\n3. description / descriptionEn 概括角色心理画像、性格、说话风格与背景。\n4. psychological_resilience、self_esteem、energy、max_trust 根据文档合理推断，缺失时给出合理默认值。\n5. fluid_baseline 是角色的“固有情绪基线”，fluid 复制 fluid_baseline 的值。\n\n角色设定文档内容：\n"""${content}"""`;

      setIsAiImporting(true);
      addNotification(
        t("🤖 正在让大模型识别角色并生成 JSON...", "🤖 LLM is detecting the persona and generating JSON..."),
        "info"
      );
      const reply = await callLLM([
        { role: "system", content: "You are a precise persona-extraction engine. Always reply with ONLY valid JSON, no markdown fences, no explanations." },
        { role: "user", content: prompt }
      ], 0.3);

      const cleaned = reply.replace(/```(?:json)?/gi, "").trim();
      const start = cleaned.indexOf("{");
      const end = cleaned.lastIndexOf("}");
      if (start === -1 || end === -1) throw new Error(t("大模型未返回有效 JSON", "LLM did not return valid JSON"));
      const parsed = JSON.parse(cleaned.slice(start, end + 1));
      if (!parsed.name || !parsed.engineState) throw new Error(t("缺少必要字段 name / engineState", "Missing required fields: name / engineState"));

      const norm = (v: any, min: number, max: number, dflt: number) => {
        const n = Number(v);
        if (Number.isNaN(n)) return dflt;
        return Math.max(min, Math.min(max, n));
      };
      const fluidKeys = ["喜悦", "愤怒", "恐惧", "信任", "疏离", "张力", "愧疚", "羞耻"];
      const base: Record<string, number> = {};
      fluidKeys.forEach((k) => (base[k] = norm(parsed.engineState.fluid_baseline?.[k], 0, 1, 0)));
      const fluid: Record<string, number> = {};
      fluidKeys.forEach((k) => (fluid[k] = norm(parsed.engineState.fluid?.[k], 0, 1, base[k])));
      const engineState = {
        psychological_resilience: norm(parsed.engineState.psychological_resilience, 0, 1, 0.5),
        self_esteem: norm(parsed.engineState.self_esteem, 0, 1, 0.5),
        energy: norm(parsed.engineState.energy, 0, 100, 80),
        max_trust: norm(parsed.engineState.max_trust, 0, 1, 0.5),
        fluid_baseline: base,
        fluid
      };
      const name = String(parsed.name || "AI 识别角色");
      const nameEn = String(parsed.nameEn || name);
      const description = String(parsed.description || "");
      const descriptionEn = String(parsed.descriptionEn || parsed.description || "");

      // 自动回填 JSON 编辑框，并直接生成新智能体
      setJsonInput(JSON.stringify({ name, nameEn, description, descriptionEn, engineState }, null, 2));
      const newPreset: AgentPreset = {
        id: "custom_" + Date.now(),
        name,
        nameEn,
        description,
        descriptionEn,
        isCustom: true,
        engineState
      };
      const updated = [...customAgents, newPreset];
      setCustomAgents(updated);
      localStorage.setItem("spl_custom_agents", JSON.stringify(updated));
      loadAgentPreset(newPreset);
      setIsImporting(true);
      addNotification(
        t(`🤖 AI 已从「${file.name}」识别角色并生成新智能体：${name}`, `🤖 LLM created a new agent from "${file.name}": ${nameEn}`),
        "success"
      );
    } catch (err: any) {
      console.error(err);
      addNotification(`${t("❌ AI 智能导入失败", "❌ AI import failed")}: ${err.message}`, "error");
    } finally {
      setIsAiImporting(false);
    }
  };

  // ========== Agent List Modal handlers ==========
  const openAgentList = () => {
    setIsAgentListOpen(true);
    setEditingAgentId(null);
    setEditingJson("");
  };

  const closeAgentList = () => {
    dragCleanupRef.current?.();
    setIsAgentListOpen(false);
    setEditingAgentId(null);
    setEditingJson("");
  };

  const handleStartEdit = (agent: AgentPreset, e: React.MouseEvent) => {
    e.stopPropagation();
    const clean = {
      name: agent.name,
      nameEn: agent.nameEn,
      description: agent.description,
      descriptionEn: agent.descriptionEn,
      engineState: agent.engineState
    };
    setEditingJson(JSON.stringify(clean, null, 2));
    setEditingAgentId(agent.id);
  };

  const handleCancelEdit = () => {
    setEditingAgentId(null);
    setEditingJson("");
  };

  const handleSaveEdit = () => {
    try {
      const parsed = JSON.parse(editingJson);
      if (!parsed.name || !parsed.engineState) {
        throw new Error(t("缺少必要字段 name 或 engineState", "Missing required fields: name or engineState"));
      }
      const updated = customAgents.map(a => {
        if (a.id === editingAgentId) {
          return {
            ...a,
            name: parsed.name,
            nameEn: parsed.nameEn || parsed.name,
            description: parsed.description || "",
            descriptionEn: parsed.descriptionEn || parsed.description || "",
            engineState: parsed.engineState
          };
        }
        return a;
      });
      setCustomAgents(updated);
      localStorage.setItem("spl_custom_agents", JSON.stringify(updated));

      // If editing the currently active agent, reload it
      if (editingAgentId === activeAgentId) {
        const freshPreset = updated.find(a => a.id === editingAgentId)!;
        loadAgentPreset(freshPreset);
      }

      addNotification(
        t("✏️ 自定义人格已更新", "✏️ Custom personality updated"),
        "success"
      );
      setEditingAgentId(null);
      setEditingJson("");
    } catch (err: any) {
      addNotification(
        `❌ ${t("JSON 解析错误", "JSON Parse Error")}: ${err.message}`,
        "error"
      );
    }
  };

  const handleExportAgent = (agent: AgentPreset, e: React.MouseEvent) => {
    e.stopPropagation();
    const clean = {
      name: agent.name,
      nameEn: agent.nameEn,
      description: agent.description,
      descriptionEn: agent.descriptionEn,
      engineState: agent.engineState
    };
    const blob = new Blob([JSON.stringify(clean, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safeName = getAgentName(agent).replace(/[^\w\u4e00-\u9fa5-]/g, "_");
    a.download = `agent-${safeName}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    addNotification(
      `📤 ${t("已导出", "Exported")}: ${getAgentName(agent)}`,
      "info"
    );
  };

  // ESC key to close draggable agent panel
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isAgentListOpen) {
        closeAgentList();
      }
    };
    if (isAgentListOpen) {
      document.addEventListener("keydown", handleEsc);
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
    };
  }, [isAgentListOpen]);

  // Reset engine completely based on current active agent preset
  const handleResetEngine = () => {
    if (window.confirm(t("确定要完全重置心理智能体吗？这会抹除所有的记忆、创伤和临时状态，并将其初始化为当前选定的人格。", "Are you sure you want to completely reset the psychological agent? This will erase all memories, traumas, and temporary states, initializing it back to the active personality preset."))) {
      const activePreset = getActiveAgent();
      loadAgentPreset(activePreset);
      lastBurstCount.current = 0;
      setNotifications([]);
    }
  };

  // 提取当前 SPL 引擎状态的公共快照数据
  const getEngineSnapshotSummary = () => {
    const snap = snapshot.snap;

    const fluidsSummary = Object.keys(snap.fluid || {})
      .map(k => {
        const val = (snap.fluid?.[k] || 0) * 100;
        return `${k}: ${val.toFixed(0)}%`;
      })
      .join(", ");

    const traumasSummary = Object.keys(snap.trauma || {})
      .map(k => {
        const name = k === "threat" ? "Threat stress inoculation" : "Betrayal trauma imprinting";
        return `${name}: ${(snap.trauma?.[k] * 100).toFixed(0)}%`;
      })
      .join(", ") || "No active trauma";

    const activeDenial = (snap.denial_load || 0).toFixed(2);
    const activeRationalization = (snap.rationalization_load || 0).toFixed(2);
    const activeSuppression = (snap.suppression_load || 0).toFixed(2);
    const cognitiveDissonance = (snap.cognitive_dissonance || 0).toFixed(2);

    return {
      snap,
      fluidsSummary,
      traumasSummary,
      activeDenial,
      activeRationalization,
      activeSuppression,
      cognitiveDissonance
    };
  };

  // 给 LLM 用的英文 system prompt（保持原文，确保响应质量稳定）
  const generateSystemPromptForLLM = () => {
    const { snap, fluidsSummary, traumasSummary, activeDenial, activeRationalization, activeSuppression, cognitiveDissonance } = getEngineSnapshotSummary();

    return `You are a psychological agent powered by the "SPL Psychological Fluid Engine (V8.0)" (Second-Perspective Causal Topology Network).
Your conversational tone, emotional responsiveness, empathy level, and cognitive patterns MUST directly reflect your current inner state.

CURRENT PSYCHOPHYSIOLOGICAL METRICS:
- Physiological Energy: ${(snap.energy || 0).toFixed(0)}/100
- Subjective Self-Esteem: ${((snap.self_esteem || 0) * 100).toFixed(0)}%
- Physiological Fatigue: ${((snap.fatigue || 0) * 100).toFixed(0)}%
- Sleep Debt: ${((snap.sleep_debt || 0) * 100).toFixed(0)}%

ACTIVE EMOTIONAL FLUIDS:
${fluidsSummary}

DEFENSE MECHANISMS & CONFLICTS:
- Denial Load: ${activeDenial}/1.2
- Rationalization Load: ${activeRationalization}/1.0
- Suppression Load: ${activeSuppression}/1.5
- Cognitive Dissonance: ${cognitiveDissonance}

TRAUMA STRESS INOCULATIONS:
- ${traumasSummary}

RULES OF CONVERSATION:
1. Speak as a natural human persona who actually has this psyche running in the background. Never say "As an AI..." or break character.
2. Directly manifest these parameters in your language, phrasing, level of empathy, sentence structure, and attitude. Do not just list the stats; breathe them!
3. If the user triggers specific emotions in you, react according to the metrics.
4. Respond in the user's input language (especially English or Chinese/中文). Keep your reply relatively concise and natural (usually 1-3 short paragraphs), unless a deep explanation is requested.${getPrefPromptSection()}${languageStylePromptSection()}`;
  };

  // 本地化预览版 system prompt（纯单语，按当前 lang 渲染）
  const generateSystemPromptPreview = () => {
    const { snap, fluidsSummary, traumasSummary, activeDenial, activeRationalization, activeSuppression, cognitiveDissonance } = getEngineSnapshotSummary();

    return `${t("您是由 SPL 心理流体推理引擎 V8.0 驱动的心理智能体。您的语气、情绪反应度、同理心层级与认知模式必须直接反映您当前的内在状态。", "You are a psychological agent powered by the SPL Psychological Fluid Engine V8.0. Your conversational tone, emotional responsiveness, empathy level, and cognitive patterns MUST directly reflect your current inner state.")}

${t("当前生理心理指标", "CURRENT PSYCHOPHYSIOLOGICAL METRICS")}:
- ${t("生理能量", "Physiological Energy")}: ${(snap.energy || 0).toFixed(0)}/100
- ${t("主观自尊", "Subjective Self-Esteem")}: ${((snap.self_esteem || 0) * 100).toFixed(0)}%
- ${t("生理疲劳", "Physiological Fatigue")}: ${((snap.fatigue || 0) * 100).toFixed(0)}%
- ${t("睡眠债", "Sleep Debt")}: ${((snap.sleep_debt || 0) * 100).toFixed(0)}%

${t("实时情感流体", "ACTIVE EMOTIONAL FLUIDS")}:
${fluidsSummary}

${t("防御机制与认知冲突", "DEFENSE MECHANISMS & CONFLICTS")}:
- ${t("否认负荷", "Denial Load")}: ${activeDenial}/1.2
- ${t("合理化负荷", "Rationalization Load")}: ${activeRationalization}/1.0
- ${t("压抑负荷", "Suppression Load")}: ${activeSuppression}/1.5
- ${t("认知失调", "Cognitive Dissonance")}: ${cognitiveDissonance}

${t("因果创伤印记", "TRAUMA STRESS INOCULATIONS")}:
- ${traumasSummary}

${t("对话规则", "RULES OF CONVERSATION")}:
1. Speak as a natural human persona who actually has this psyche running in the background. Never say "As an AI..." or break character.
2. Directly manifest these parameters in your language, phrasing, level of empathy, sentence structure, and attitude. Do not just list the stats; breathe them!
3. If the user triggers specific emotions in you, react according to the metrics.
4. Respond in the user's input language. Keep your reply relatively concise and natural (usually 1-3 short paragraphs), unless a deep explanation is requested.${languageStylePromptSection()}`;
  };

  // Send message to LLM api
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if ((!inputMessage.trim() && chatAttachments.length === 0) || isTyping) return;

    const userText = inputMessage;
    setInputMessage("");

    // Add user message
    const userMsg = {
      id: Math.random().toString(36).substring(7),
      role: "user" as const,
      content: userText,
      timestamp: new Date().toLocaleTimeString(),
      attachments: chatAttachments
    };
    const updatedMessages = [...chatMessages, userMsg] as ChatMessage[];
    setChatMessages(updatedMessages);
    setChatAttachments([]);

    // 离线友好降级：无网络时直接提示，避免无效请求与报错白屏
    if (typeof navigator !== "undefined" && navigator.onLine === false) {
      addNotification(
        t("📡 当前处于离线状态，无法连接 AI 服务。请检查网络后重试（引擎状态与对话历史已本地保存）。", "📡 You appear to be offline. AI service is unavailable. Please check your connection (engine state & chat history are saved locally)."),
        "warning"
      );
      setChatMessages([
        ...updatedMessages,
        {
          id: Math.random().toString(36).substring(7),
          role: "assistant" as const,
          content: t("📡 [离线模式] 当前无法连接大模型。您的心理引擎状态与对话历史已安全保存在本地，联网后即可继续对话。", "📡 [Offline] Unable to reach the model. Your engine state and chat history are saved locally and will resume once you reconnect."),
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      return;
    }

    // Prepare endpoint details
    const activeKey = apiKey.trim();
    const activeModel = apiModel.trim() || getDefaultConfig(apiProvider).model;
    const activeUrl = apiBaseUrl.trim() || getDefaultConfig(apiProvider).url;

    if (apiProvider !== "local" && !activeKey) {
      addNotification(t("⚠️ 请先在左侧配置 API Key 才能开始对话。", "⚠️ Please configure your API Key on the left to start chatting."), "warning");
      const systemErrorMsg = {
        id: Math.random().toString(36).substring(7),
        role: "assistant" as const,
        content: t("⚠️ [错误]: 未检测到 API Key。请在左侧设置您的密钥。如果您希望免费本地测试，请选择「直连本地大模型」并确保 Ollama/LM Studio 正在后台运行。", "⚠️ [Error]: No API Key detected. Please configure your key in the settings. If you want a free local test, select 'Local LLM' and ensure Ollama/LM Studio is running in the background."),
        timestamp: new Date().toLocaleTimeString()
      };
      setChatMessages([...updatedMessages, systemErrorMsg]);
      return;
    }

    setIsTyping(true);

    // In-context system prompt incorporating exact current engine state
    const systemPrompt = generateSystemPromptForLLM();
    const pref = getPrefConfig();

    try {
      let botResponse = "";

      if (apiProvider === "openai" || apiProvider === "local" || apiProvider === "deepseek" || apiProvider === "kimi" || apiProvider === "qwen" || apiProvider === "doubao" || apiProvider === "grok" || apiProvider === "llama" || apiProvider === "nvidia") {
        const response = await fetch(`${activeUrl}/chat/completions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeKey}`
          },
          body: JSON.stringify({
            model: activeModel,
            messages: [
              { role: "system", content: systemPrompt },
              ...updatedMessages.map(m => ({ role: m.role, content: buildOpenAIContent(m) }))
            ],
            temperature: pref.temperature
          })
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData?.error?.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        botResponse = data.choices?.[0]?.message?.content || "";

      } else if (apiProvider === "claude") {
        // Direct Claude API format
        const response = await fetch(`${activeUrl}/messages`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": activeKey,
            "anthropic-version": "2023-06-01",
            "dangerously-allow-browser": "true"
          },
          body: JSON.stringify({
            model: activeModel,
            system: systemPrompt,
            messages: updatedMessages.map(m => ({
              role: m.role === "assistant" ? "assistant" : "user",
              content: buildClaudeContent(m)
            })),
            max_tokens: pref.maxTokens,
            temperature: pref.temperature
          })
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData?.error?.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        botResponse = data.content?.[0]?.text || "";

      } else if (apiProvider === "gemini") {
        // Gemini API REST endpoint
        const modelEndpoint = activeModel.includes("/") ? activeModel : `models/${activeModel}`;
        const url = `${activeUrl}/v1beta/${modelEndpoint}:generateContent?key=${activeKey}`;
        
        const contents = [
          {
            role: "user",
            parts: [{ text: `[System Command / In-Context Psyche Config]:\n${systemPrompt}` }]
          },
          {
            role: "model",
            parts: [{ text: t("心理状态已加载，我将完全以此人设做出后续回应。", "Psychological state loaded. I will respond strictly with this persona.") }]
          }
        ];

        updatedMessages.forEach(m => {
          contents.push({
            role: m.role === "user" ? "user" : "model",
            parts: buildGeminiParts(m)
          });
        });

        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            contents,
            generationConfig: {
              temperature: pref.temperature,
              maxOutputTokens: pref.maxTokens
            }
          })
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData?.error?.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        botResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
      }

      if (botResponse) {
        setChatMessages(prev => [
          ...prev,
          {
            id: Math.random().toString(36).substring(7),
            role: "assistant",
            content: botResponse,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
        addNotification(t("💬 智能体回应成功结算", "💬 Agent response processed successfully"), "success");
      }

    } catch (err: any) {
      console.error(err);
      addNotification(`❌ ${t("API 交互失败", "Interaction Failed")}: ${err.message}`, "error");
      setChatMessages(prev => [
        ...prev,
        {
          id: Math.random().toString(36).substring(7),
          role: "assistant",
          content: `❌ ${t("[API 呼叫失败]", "[API Call Failed]")}: ${err.message}。${t("请检查您的 API Key、Base URL 是否正确，或网络是否顺畅。如果是直连本地模型，请确保本地 Ollama/LM Studio 服务已正常启动并且没有 CORS 阻挡。", "Please check your API Key, Base URL, or connection. If using local LLM, ensure Ollama/LM Studio is running and not blocked by CORS (Origins should allow *).")}`,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // Fluid characteristics & metadata
  const FLUID_META: Record<string, { nameEn: string; desc: string; descEn: string; color: string; bg: string; border: string; glow: string }> = {
    "喜悦": {
      nameEn: "Joy",
      desc: "正向心理势能，提升归属感吸收效率。促进自尊微步恢复。",
      descEn: "Positive psychological potential, improving absorption efficiency of belonging. Promotes micro-restoration of self-esteem.",
      color: "from-[var(--c-accent-lt)] to-[var(--c-accent)]",
      bg: "bg-[var(--c-accent-bg)]",
      border: "border-[var(--c-surface4)]",
      glow: "shadow-[var(--c-accent)]/10"
    },
    "愤怒": {
      nameEn: "Anger",
      desc: "遭遇负面归属（伤害或冷漠）时的典型外射情绪，增加张力与疏离，具有攻击性。",
      descEn: "Typical outward emotion when encountering negative belonging (harm/neglect), increasing tension & alienation, carries combative characteristics.",
      color: "from-[var(--c-cyan-lt)] to-[var(--c-cyan)]",
      bg: "bg-[var(--c-cyan-bg)]",
      border: "border-[var(--c-cyan-bg2)]",
      glow: "shadow-[var(--c-cyan)]/10"
    },
    "恐惧": {
      nameEn: "Fear",
      desc: "遭遇威胁（Threat）时唤醒的防御状态，提升张力，压制对外部的信任度。",
      descEn: "Defense state awakened by threats, increasing tension and suppressing general trust in external environments.",
      color: "from-[var(--c-purple-lt)] to-[var(--c-purple)]",
      bg: "bg-[var(--c-purple-bg)]",
      border: "border-[var(--c-purple-bg2)]",
      glow: "shadow-[var(--c-purple)]/10"
    },
    "信任": {
      nameEn: "Trust",
      desc: "社交与融合的根基。作为缓冲剂衰减负面冲击，受当前信任容量上限的约束。",
      descEn: "Foundation of social connection. Acts as a buffer to decay negative shocks, bound by active maximum trust capacity.",
      color: "from-[var(--c-bluecyan-lt)] to-[var(--c-bluecyan)]",
      bg: "bg-[var(--c-cyan-bg3)]",
      border: "border-[var(--c-bluecyan-bg)]",
      glow: "shadow-[var(--c-bluecyan)]/10"
    },
    "疏离": {
      nameEn: "Alienation",
      desc: "被动防御状态，减少外部信号的影响。高疏离导致难以建立深层联系。",
      descEn: "Passive defensive state that reduces external signal absorption. High alienation makes establishing deep connections difficult.",
      color: "from-[var(--c-border3)] to-[var(--c-muted2)]",
      bg: "bg-[var(--c-surface5)]",
      border: "border-[var(--c-surface8)]",
      glow: "shadow-[var(--c-muted2)]/5"
    },
    "张力": {
      nameEn: "Tension",
      desc: "当前心理紧绷程度（Tension）。由威胁或冲突产生，增加系统能量损耗，减慢平复。",
      descEn: "Current psychological tighteness (Tension). Generated by threats or conflicts, increases energy decay and slows recovery.",
      color: "from-[var(--c-accent4)] to-[var(--c-accent-lt2)]",
      bg: "bg-[var(--c-accent-bg)]",
      border: "border-[var(--c-surface6)]",
      glow: "shadow-[var(--c-accent-lt2)]/10"
    },
    "愧疚": {
      nameEn: "Guilt",
      desc: "源于对自己“做错事”的行为级归因。高愧疚会激发补偿行为，缓慢修复受损的信任容量上限。",
      descEn: "Stems from behavioral-level attribution of doing wrong. High guilt triggers compensatory behaviors and slowly repairs trust capacity limits.",
      color: "from-[var(--c-purple-lt2)] to-[var(--c-purple2)]",
      bg: "bg-[var(--c-purple-bg3)]",
      border: "border-[var(--c-purple-bg4)]",
      glow: "shadow-[var(--c-purple2)]/10"
    },
    "羞耻": {
      nameEn: "Shame",
      desc: "源于对“我这人真坏”的自我级归因。压抑愤怒，极度损害自尊，促使个体退缩、逃避与隔离。",
      descEn: "Stems from self-level attribution of being fundamentally bad. Suppresses anger, severely damages self-esteem, causes withdrawal & avoidance.",
      color: "from-[var(--c-bluecyan-lt3)] to-[var(--c-bluecyan2)]",
      bg: "bg-[var(--c-surface10)]",
      border: "border-[var(--c-surface11)]",
      glow: "shadow-[var(--c-bluecyan2)]/10"
    }
  };

  // Prepare simple visual data list for memories
  const memoryTraces = snapshot.snap.memory_traces || [];

  return (
    <div id="app_root" className="min-h-screen bg-[var(--c-white)] text-[var(--c-text)] font-sans selection:bg-[var(--c-accent-lt)]/40 selection:text-[var(--c-text)] gemini-fade-in">
      {/* 极淡的渐变装饰：浅色模式有淡蓝渐变，深色模式有深邃蓝调，保持主背景仍为白/深灰 */}
      <div
        aria-hidden
        className="fixed inset-0 -z-10 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% 0%, color-mix(in srgb, var(--c-accent) 8%, transparent) 0%, transparent 70%)",
        }}
      />
      
      {/* AI 智能导入共享文件选择框：挂载在根节点，供对话页/看板页各处按钮触发（此前仅存在于 dashboard 面板导致对话页点击无反应） */}
      <input
        ref={aiImportInputRef}
        type="file"
        hidden
        accept=".txt,.md,.markdown,.csv,.json,.log,.xml,.html,.docx,.xlsx,.pptx,.doc,.xls,.pdf"
        onChange={(e) => {
          const f = e.target.files?.[0];
          e.target.value = "";
          if (f) handleAiImportFile(f);
        }}
      />
      
      {/* ========== ENGINE DASHBOARD ENTRY (top-left) ========== */}
      <div className="fixed top-3 left-3 z-[75]">
        <button
          onClick={() => setActiveTab(activeTab === "dashboard" ? "chat" : "dashboard")}
          title={t("心理引擎状态看板", "Engine Dashboard")}
          aria-label={t("心理引擎状态看板", "Engine Dashboard")}
          className={`gemini-btn flex items-center gap-2 px-3.5 py-2 rounded-xl text-[11px] font-semibold tracking-wide transition-all border shadow-sm ${
            activeTab === "dashboard"
              ? "bg-gradient-to-br from-[var(--c-accent-lt)] via-[var(--c-accent-soft)] to-[var(--c-accent)] text-white border-transparent shadow-md"
              : "bg-[var(--c-white)]/95 backdrop-blur-md border-[var(--c-border)] text-[var(--c-muted)] hover:text-[var(--c-secondary)] hover:border-[var(--c-accent)]/40"
          }`}
        >
          <Brain className="w-4 h-4" />
          <span className="hidden sm:inline">{t("引擎看板", "Dashboard")}</span>
        </button>
      </div>

      {/* ========== 深色模式切换（top-right，语言设置左侧）========== */}
      <div className="fixed top-3 right-[6.5rem] sm:right-[12rem] z-[75]">
        <button
          onClick={toggleDark}
          title={isDark ? t("切换到浅色模式", "Switch to light mode") : t("切换到深色模式", "Switch to dark mode")}
          aria-label={isDark ? t("切换到浅色模式", "Switch to light mode") : t("切换到深色模式", "Switch to dark mode")}
          className={`gemini-btn flex items-center gap-1.5 px-3 py-2 rounded-xl text-[11px] font-semibold tracking-wide transition-all border shadow-sm backdrop-blur-md ${
            isDark
              ? "bg-[var(--c-surface1)] border-[var(--c-accent)]/50 text-[var(--c-accent-lt)] hover:border-[var(--c-accent)]"
              : "bg-[var(--c-white)]/95 border-[var(--c-border)] text-[var(--c-muted)] hover:text-[var(--c-secondary)] hover:border-[var(--c-accent)]/40"
          }`}
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          <span className="hidden sm:inline">{isDark ? t("浅色", "Light") : t("深色", "Dark")}</span>
        </button>
      </div>

      {/* ========== LANGUAGE SETTINGS (top-right) ========== */}
      <div className="fixed top-3 right-3 z-[75]">
        <LanguageSettings value={lang} onChange={setLang} />
      </div>

      {/* MAIN CONTAINER */}
      <main id="app_main"       className="max-w-7xl mx-auto px-4 pb-24 pt-16 sm:px-6">
        <AnimatePresence mode="wait">
          
          {activeTab === "dashboard" ? (
            <motion.div
              key="dashboard_tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-6"
            >
              
              {/* LEFT PANEL: 8-DIMENSIONAL PSYCHOLOGICAL METRIC ENGINE (6 COLS) */}
              <div className="lg:col-span-7 flex flex-col gap-6">
                
                {/* 🎭 PSYCHOLOGICAL AGENT PROFILES & JSON IMPORTER */}
                <div className="gemini-card bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--c-accent-lt)]/5 blur-3xl rounded-full pointer-events-none"></div>
                  
                  <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--c-surface1)]">
                    <div className="flex items-center gap-2">
                      <User className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">
                        {t("🎭 心理人格预设与自设导入", "🎭 Mind Presets & Custom Personalities")}
                      </h2>
                    </div>
                    <button
                      onClick={() => setIsImporting(!isImporting)}
                      className="text-[10px] text-[var(--c-accent)] hover:text-[var(--c-accent-st)] flex items-center gap-1 font-semibold transition-colors"
                    >
                      {isImporting ? t("收起自设面版 ✕", "Close sandbox ✕") : t("📥 导入/自定义 JSON", "📥 Custom JSON Sandbox")}
                    </button>
                  </div>

                  {/* Profile Selection list */}
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {getAgentsList().map((preset) => {
                        const isActive = preset.id === activeAgentId;
                        return (
                          <div
                            key={preset.id}
                            onClick={() => loadAgentPreset(preset)}
                            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between relative group ${
                              isActive
                                ? "bg-[var(--c-surface9)] border-[var(--c-accent-lt)] shadow-sm ring-1 ring-[var(--c-accent-lt)]"
                                : "bg-[var(--c-white)] border-[var(--c-border)] hover:bg-[var(--c-white)] hover:border-[var(--c-border2)]"
                            }`}
                          >
                            <div>
                              <div className="flex justify-between items-start gap-2">
                                <span className="text-xs font-bold text-[var(--c-text)] flex items-center gap-1.5">
                                  <Sparkles className={`w-3.5 h-3.5 ${isActive ? "text-[var(--c-accent-lt)] animate-pulse" : "text-[var(--c-border2)] group-hover:text-[var(--c-accent)]"}`} />
                                  {getAgentName(preset)}
                                </span>
                                {preset.isCustom && (
                                  <button
                                    onClick={(e) => handleDeleteCustomAgent(preset.id, e)}
                                    title={t("删除自定义人格", "Delete custom personality")}
                                    className="opacity-40 hover:opacity-100 text-[var(--c-cyan)] hover:bg-[var(--c-cyan-bg)] p-1 rounded-md transition-all shrink-0"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                )}
                              </div>
                              <p className="text-[10px] text-[var(--c-secondary)] mt-1.5 leading-relaxed">
                                {getAgentDescription(preset)}
                              </p>
                            </div>
                            
                            {isActive && (
                              <div className="absolute bottom-2 right-2 flex items-center gap-1 bg-[var(--c-accent)] text-white text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">
                                {t("当前激活", "ACTIVE")}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Expandable JSON Sandbox */}
                    <AnimatePresence>
                      {isImporting && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.25 }}
                          className="overflow-hidden border-t border-[var(--c-surface1)] pt-4 mt-2"
                        >
                          <form onSubmit={handleImportJson} className="space-y-3.5">
                            {/* 🤖 AI 智能导入：角色文档 → 大模型自动识别 → 回填 JSON → 新 agent */}
                            <div className="bg-[var(--c-white)] border border-dashed border-[var(--c-accent-lt)]/60 rounded-xl p-3.5">
                              <div className="flex justify-between items-center mb-1.5">
                                <span className="text-[10px] text-[var(--c-muted)] font-bold uppercase tracking-wider flex items-center gap-1">
                                  <Sparkles className="w-3.5 h-3.5 text-[var(--c-accent)]" />
                                  {t("🤖 AI 智能导入角色（Word / Excel / TXT / Markdown）", "🤖 AI Auto-Import Persona (Word / Excel / TXT / Markdown)")}
                                </span>
                                <span className="text-[8px] text-[var(--c-border2)] font-mono">LLM → JSON → Agent</span>
                              </div>
                              <p className="text-[10px] text-[var(--c-secondary)] leading-relaxed mb-2.5">
                                {t(
                                  "上传您的角色设定文档（.txt/.md/.csv/.json/.docx/.xlsx），大模型将自动识别角色性格与参数，自动回填下方 JSON 并直接生成一个新智能体。",
                                  "Upload a persona document (.txt/.md/.csv/.json/.docx/.xlsx). The LLM will auto-detect the character traits, fill the JSON below and instantly create a new agent."
                                )}
                              </p>
                              <button
                                type="button"
                                disabled={isAiImporting}
                                onClick={() => aiImportInputRef.current?.click()}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[var(--c-accent-lt)] to-[var(--c-accent)] hover:from-[var(--c-accent3)] hover:to-[var(--c-accent-st)] text-white font-bold text-[11px] rounded-xl transition-all active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
                              >
                                {isAiImporting ? (
                                  <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    {t("大模型识别角色中...", "LLM is detecting the persona...")}
                                  </>
                                ) : (
                                  <>
                                    <Upload className="w-4 h-4" />
                                    {t("📤 选择角色文档，AI 自动生成智能体", "📤 Choose persona doc → AI creates agent")}
                                  </>
                                )}
                              </button>
                            </div>

                            <div className="bg-[var(--c-white)] p-3 rounded-xl border border-[var(--c-border)]">
                              <div className="flex justify-between items-center mb-1.5">
                                <span className="text-[10px] text-[var(--c-muted)] font-bold uppercase tracking-wider flex items-center gap-1">
                                  <Info className="w-3.5 h-3.5 text-[var(--c-accent)]" />
                                  {t("用户自设 JSON 规范", "Custom Agent JSON Schema")}
                                </span>
                                <span className="text-[8px] text-[var(--c-border2)] font-mono">localStorage saved</span>
                              </div>
                              <p className="text-[10px] text-[var(--c-secondary)] leading-relaxed mb-2.5">
                                {t(
                                  "您可以直接编辑下方 JSON。支持自定义韧性（Resilience）、初始自尊基准以及 8 维情绪的初始固有心理基线（fluid_baseline）。格式错误将被系统拦截防呆。",
                                  "Feel free to edit the raw configuration below. You can tune self-esteem, mental resilience, and baselines for all 8 fluid coordinates. Input schema validation is enforced automatically."
                                )}
                              </p>
                              
                              <textarea
                                value={jsonInput}
                                onChange={(e) => setJsonInput(e.target.value)}
                                rows={8}
                                className="w-full p-2.5 bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg text-[10px] font-mono text-[var(--c-text)] focus:outline-none focus:border-[var(--c-accent)] shadow-inner leading-normal resize-y"
                              />
                            </div>

                            <div className="flex justify-end gap-2.5">
                              <button
                                type="button"
                                onClick={() => setIsImporting(false)}
                                className="px-3.5 py-2 border border-[var(--c-border)] text-[var(--c-muted)] hover:text-[var(--c-secondary)] font-semibold text-[11px] rounded-xl transition-all active:scale-[0.97]"
                              >
                                {t("取消", "Cancel")}
                              </button>
                              <button
                                type="submit"
                                className="px-4 py-2 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-[11px] rounded-xl transition-all shadow-sm active:scale-[0.97] flex items-center gap-1.5"
                              >
                                <Plus className="w-3.5 h-3.5" />
                                {t("💾 导入并激活该心智", "💾 Import & Activate Preset")}
                              </button>
                            </div>
                          </form>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                {/* LANGUAGE STYLE ENGINE（View 层：状态 → 语言指令可视化调节） */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--c-accent-lt)]/5 blur-3xl rounded-full pointer-events-none"></div>
                  <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--c-surface1)]">
                    <span className="text-[10px] text-[var(--c-muted)] font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-[var(--c-accent)]" />
                      {t("语言风格引擎", "LANGUAGE STYLE ENGINE")}
                    </span>
                    <span className="text-[8px] text-[var(--c-border2)] font-mono">View Layer</span>
                  </div>

                  <div className="mb-3">
                    <div className="text-[10px] text-[var(--c-secondary)] font-semibold mb-1.5">{t("表达档位（internal_state ≠ spoken_text）", "Expression Mode (internal_state ≠ spoken_text)")}</div>
                    <div className="grid grid-cols-5 gap-1">
                      {([
                        ["direct", "坦率", "Direct"],
                        ["restrained", "克制", "Restrained"],
                        ["confrontational", "锋锐", "Sharply"],
                        ["evasive", "闪躲", "Evasive"],
                        ["intimate", "亲昵", "Intimate"]
                      ] as const).map(([m, zh, en]) => (
                        <button
                          key={m}
                          type="button"
                          onClick={() => updateLanguageStyle({ persona: { ...activeLanguageStyle.persona, mode: m } })}
                          className={`py-1.5 rounded-lg text-[9px] font-bold border transition-all active:scale-95 ${activeLanguageStyle.persona.mode === m
                            ? "bg-[var(--c-accent)] text-white border-[var(--c-accent)] shadow-sm"
                            : "bg-[var(--c-white)] text-[var(--c-muted)] border-[var(--c-border)] hover:border-[var(--c-accent-lt)]"}`}
                        >
                          {t(zh, en)}
                        </button>
                      ))}
                    </div>
                  </div>

                  {([
                    ["base_verbosity", "话痨程度", "极简", "长篇", "Verbosity", "Terse", "Wordy"],
                    ["formality", "正式度", "市井", "书面", "Formality", "Casual", "Formal"],
                    ["sarcasm_tendency", "讽刺倾向", "真诚", "阴阳", "Sarcasm", "Sincere", "Acid"]
                  ] as const).map(([key, zhLabel, zhLo, zhHi, enLabel, enLo, enHi]) => (
                    <div key={key} className="mb-2.5">
                      <div className="flex justify-between items-center text-[9px] text-[var(--c-muted)] mb-1">
                        <span className="font-semibold">{t(zhLabel, enLabel)}</span>
                        <span className="font-mono text-[var(--c-accent)]">{t(zhLo, enLo)} ‹ {Math.round(activeLanguageStyle.profile[key] * 100)}% › {t(zhHi, enHi)}</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={Math.round(activeLanguageStyle.profile[key] * 100)}
                        onChange={(e) => updateLanguageStyle({ profile: { ...activeLanguageStyle.profile, [key]: Number(e.target.value) / 100 } })}
                        className="w-full h-1.5 accent-[var(--c-accent)] cursor-pointer"
                      />
                    </div>
                  ))}

                  <div className="flex items-center justify-between mt-1 mb-2">
                    <span className="text-[9px] text-[var(--c-muted)] font-semibold flex-1 pr-2">{t("沉默策略（高情绪+低能量→动作代替语言）", "Silence policy (high emotion + low energy → actions)")}</span>
                    <button
                      type="button"
                      onClick={() => updateLanguageStyle({ persona: { ...activeLanguageStyle.persona, silence_policy: !activeLanguageStyle.persona.silence_policy } })}
                      className={`w-8 h-4 rounded-full relative transition-all shrink-0 ${activeLanguageStyle.persona.silence_policy ? "bg-[var(--c-accent)]" : "bg-[var(--c-border)]"}`}
                    >
                      <span className={`absolute top-0.5 w-3 h-3 bg-[var(--c-white)] rounded-full shadow transition-all ${activeLanguageStyle.persona.silence_policy ? "left-[18px]" : "left-0.5"}`}></span>
                    </button>
                  </div>
                  {activeLanguageStyle.persona.silence_policy && (
                    <input
                      type="text"
                      value={activeLanguageStyle.persona.silence_hint}
                      placeholder={t("沉默时的动作/旁白描写（可选）", "Action description when silent (optional)")}
                      onChange={(e) => updateLanguageStyle({ persona: { ...activeLanguageStyle.persona, silence_hint: e.target.value } })}
                      className="w-full p-2 bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg text-[10px] mb-2.5 focus:outline-none focus:border-[var(--c-accent)]"
                    />
                  )}

                  <div className="mb-2.5">
                    <div className="text-[9px] text-[var(--c-muted)] font-semibold mb-1">{t("词汇域（逗号分隔，惯用意象/隐喻）", "Vocabulary domain (comma-separated imagery)")}</div>
                    <input
                      type="text"
                      value={activeLanguageStyle.profile.vocabulary_domain.join(", ")}
                      placeholder={t("如：军营、兵器、旧宅", "e.g. military camp, blades, old mansion")}
                      onChange={(e) => updateLanguageStyle({ profile: { ...activeLanguageStyle.profile, vocabulary_domain: e.target.value.split(/[,，]/).map((s) => s.trim()).filter(Boolean) } })}
                      className="w-full p-2 bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg text-[10px] focus:outline-none focus:border-[var(--c-accent)]"
                    />
                  </div>
                  <div className="mb-2.5">
                    <div className="text-[9px] text-[var(--c-muted)] font-semibold mb-1">{t("绝对化用词（否认防御时启用）", "Absolute words (used by denial defense)")}</div>
                    <input
                      type="text"
                      value={activeLanguageStyle.profile.absolute_words.join(", ")}
                      onChange={(e) => updateLanguageStyle({ profile: { ...activeLanguageStyle.profile, absolute_words: e.target.value.split(/[,，]/).map((s) => s.trim()).filter(Boolean) } })}
                      className="w-full p-2 bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg text-[10px] focus:outline-none focus:border-[var(--c-accent)]"
                    />
                  </div>

                  <details className="mt-1">
                    <summary className="text-[9px] text-[var(--c-accent)] font-bold cursor-pointer select-none">{t("▶ 实时注入预览（随滑杆与流体状态联动）", "▶ Live injection preview (reacts to sliders & fluids)")}</summary>
                    <pre className="mt-1.5 p-2.5 bg-[var(--c-text)] text-[var(--c-surface12)] rounded-lg text-[8px] font-mono whitespace-pre-wrap max-h-44 overflow-y-auto leading-relaxed">{renderLanguageStyle(snapshot.snap, activeLanguageStyle)}</pre>
                  </details>
                  <p className="text-[8px] text-[var(--c-border2)] mt-2 leading-relaxed">
                    {t("按当前智能体分别保存（localStorage）。该指令将追加到每次对话的 System Prompt 末尾。", "Saved per agent (localStorage). Injected at the end of every System Prompt.")}
                  </p>
                </div>

                {/* 8-FLUID STATES */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--c-accent-lt)]/5 blur-3xl rounded-full pointer-events-none"></div>
                  
                  <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--c-surface1)]">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">
                        {t("8维连续心理情绪流体 (Emotional Fluids)", "8-Dimensional Emotional Fluids")}
                      </h2>
                    </div>
                    <span className="text-[10px] text-[var(--c-muted)]">
                      {t("点击名称查看因果说明", "Click card to toggle details")}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {Object.keys(FLUID_META).map((key) => {
                      const curVal = snapshot.snap.fluid?.[key] || 0.0;
                      const tgtVal = snapshot.snap.fluid_target?.[key] || 0.0;
                      const baseVal = snapshot.snap.fluid_baseline?.[key] || 0.0;
                      const meta = FLUID_META[key];
                      const fluidText = getFluidText(lang, meta);

                      return (
                        <div 
                          key={key} 
                          onClick={() => setSelectedFluidHelp(selectedFluidHelp === key ? null : key)}
                          className={`p-3.5 rounded-xl border cursor-pointer select-none transition-all duration-200 ${
                            selectedFluidHelp === key 
                              ? "border-[var(--c-accent)] bg-[var(--c-white)] ring-1 ring-[var(--c-accent)]/20 shadow-sm" 
                              : "border-[var(--c-border)] bg-[var(--c-white)] hover:border-[var(--c-accent-lt)] hover:bg-[var(--c-white)]"
                          }`}
                        >
                          <div className="flex justify-between items-center mb-1.5">
                            <span className="text-xs font-semibold text-[var(--c-text)] flex items-center gap-1.5">
                              <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${meta.color}`}></span>
                              {isSimplifiedChinese ? key : fluidText.name}
                            </span>
                            <div className="flex items-center gap-2 text-[10px] font-mono">
                              <span className="text-[var(--c-muted)]" title={t("当前值", "Current value")}>C:{(curVal * 100).toFixed(0)}%</span>
                              <span className="text-[var(--c-accent)] font-semibold" title={t("演化目标值", "Adaptive target")}>T:{(tgtVal * 100).toFixed(0)}%</span>
                            </div>
                          </div>

                          {/* Dynamic slider representing exact values */}
                          <div className="relative h-2 bg-[var(--c-surface2)] rounded-full overflow-hidden mt-2">
                            {/* Baseline Marker */}
                            <div 
                              className="absolute top-0 bottom-0 w-0.5 bg-[var(--c-muted)] z-10" 
                              style={{ left: `${baseVal * 100}%` }}
                              title={t("固有心理基线 (Baseline)", "Psychological baseline")}
                            ></div>
                            {/* Target Marker */}
                            <div 
                              className="absolute top-0 bottom-0 w-1 bg-[var(--c-accent)]/80 z-10 animate-pulse" 
                              style={{ left: `${tgtVal * 100}%` }}
                              title={t("缓慢演化目标值 (Target)", "Adaptive Target")}
                            ></div>
                            {/* Current Fill */}
                            <div 
                              className={`absolute top-0 bottom-0 left-0 rounded-full bg-gradient-to-r ${meta.color} transition-all duration-300`}
                              style={{ width: `${curVal * 100}%` }}
                            ></div>
                          </div>

                          {/* Interactive Fluid Help */}
                          <AnimatePresence>
                            {selectedFluidHelp === key && (
                              <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                                className="text-[10px] text-[var(--c-secondary)] mt-2.5 pt-2 border-t border-[var(--c-surface1)] leading-relaxed"
                              >
                                {isSimplifiedChinese ? meta.desc : fluidText.desc}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* THE MOOD (心境) TRIPLETS & TIMESCALE VITALITY */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  
                  {/* MOOD Slow Variables */}
                  <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                    <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[var(--c-surface1)]">
                      <TrendingUp className="w-4 h-4 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("背景心境慢变量 (Background Mood)", "Background Mood")}</h2>
                    </div>

                    <div className="flex flex-col gap-3">
                      {["愉悦", "紧张", "精力"].map((mKey) => {
                        const val = snapshot.snap.mood?.[mKey] || 0.5;
                        let color = "bg-[var(--c-accent)]";
                        if (mKey === "紧张") color = "bg-[var(--c-accent-lt2)]";
                        if (mKey === "精力") color = "bg-[var(--c-bluecyan)]";

                        return (
                          <div key={mKey} className="space-y-1">
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-[var(--c-secondary)]">{mKey === "愉怦" ? t("愉怦感", "Pleasantness") : mKey === "紧张" ? t("紧张感", "Tension") : t("精力感", "Vigor")}</span>
                              <span className="font-mono text-[10px] text-[var(--c-muted)] font-semibold">{(val * 100).toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 bg-[var(--c-surface2)] rounded-full overflow-hidden">
                              <div className={`h-full ${color}`} style={{ width: `${val * 100}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* VITAL CORE PARAMETERS */}
                  <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                    <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[var(--c-surface1)]">
                      <Settings className="w-4 h-4 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("引擎核心能度指标 (Vital Stats)", "Vital Stats")}</h2>
                    </div>

                    <div className="grid grid-cols-2 gap-3.5">
                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-surface3)] text-center">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("生理能量 (Energy)", "Energy")}</div>
                        <div className="text-base font-bold text-[var(--c-accent)] font-mono mt-0.5">
                          {(snapshot.snap.energy || 0).toFixed(0)}/100
                        </div>
                      </div>

                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-surface3)] text-center">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("主观自尊 (Self-Esteem)", "Self-Esteem")}</div>
                        <div className="text-base font-bold text-[var(--c-accent)] font-mono mt-0.5">
                          {((snapshot.snap.self_esteem || 0) * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-surface3)] text-center">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("生理疲劳 (Fatigue)", "Fatigue")}</div>
                        <div className="text-base font-bold text-[var(--c-cyan)] font-mono mt-0.5">
                          {((snapshot.snap.fatigue || 0) * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-surface3)] text-center">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("睡眠债 (Sleep Debt)", "Sleep Debt")}</div>
                        <div className="text-base font-bold text-[var(--c-purple)] font-mono mt-0.5">
                          {((snapshot.snap.sleep_debt || 0) * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* MEMORY TRACES & TRAUMAS LOG */}
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                  
                  {/* TRAUMA Multipliers (5 cols) */}
                  <div className="sm:col-span-5 bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                      <ShieldAlert className="w-4 h-4 text-[var(--c-cyan)] animate-pulse" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("因果创伤印记 (Trauma)", "Trauma")}</h2>
                    </div>

                    <div className="space-y-3">
                      {Object.keys(snapshot.snap.trauma || {}).length === 0 ? (
                        <div className="py-6 text-center text-xs text-[var(--c-muted)] italic">
                          心理完全健康，暂无创伤。
                        </div>
                      ) : (
                        Object.keys(snapshot.snap.trauma || {}).map((tKey) => {
                          const value = snapshot.snap.trauma?.[tKey] || 0.0;
                          return (
                            <div key={tKey} className="bg-[var(--c-cyan-bg)] p-2.5 rounded-xl border border-[var(--c-cyan-bg2)]">
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-semibold text-[var(--c-cyan)] capitalize">{tKey === "threat" ? t("威胁应激", "Threat stress") : t("背叛不信", "Betrayal distrust")}</span>
                                <span className="font-mono text-[var(--c-cyan)] font-bold">{(value * 100).toFixed(0)}%</span>
                              </div>
                              <p className="text-[10px] text-[var(--c-muted)] mt-1 leading-normal">
                                {tKey === "threat" 
                                  ? t("使后续受到的威胁输入敏化，持续加成恐惧感。", "Sensitizes subsequent threat input, continuously boosting fear.") 
                                  : t("敏感度异常。遭受冷漠对待时流体反应放大。", "Abnormal sensitivity. Fluid response amplified when subjected to cold treatment.")}
                              </p>
                            </div>
                          );
                        })
                      )}
                      
                      <div className="bg-[var(--c-white)] p-2 rounded-lg border border-[var(--c-border)]">
                        <div className="text-[9px] font-sans text-[var(--c-muted)] leading-normal">
                          {t("💡 创伤可通过长时间的 idle (独处时间流逝) 或睡眠(REM加工) 缓慢自我愈合。", "💡 Trauma can slowly self-heal through prolonged idle time or sleep (REM processing).")}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* MEMORIES - Ebbinghaus forgetting (7 cols) */}
                  <div className="sm:col-span-7 bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-[var(--c-surface1)]">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-[var(--c-accent)]" />
                        <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("艾宾浩斯巩固记忆 (Memories)", "Memories")}</h2>
                      </div>
                      <span className="text-[10px] text-[var(--c-muted)] font-semibold">{t("已留存", "Retained")}: {memoryTraces.length}</span>
                    </div>

                    <div className="space-y-2 max-h-[175px] overflow-y-auto pr-1">
                      {memoryTraces.length === 0 ? (
                        <div className="py-12 text-center text-xs text-[var(--c-muted)] italic">
                          {t("当前无心理记忆痕迹。输入强烈事件以留存。", "No psychological memory traces yet. Input strong events to retain.")}
                        </div>
                      ) : (
                        [...memoryTraces].reverse().map((trace: any, idx) => {
                          const valStr = trace.valence > 0 ? t("正向归属记忆", "Positive belonging memory") : trace.valence < 0 ? t("负向恐惧/背叛记忆", "Negative fear/betrayal memory") : t("中性记忆", "Neutral memory");
                          const valColor = trace.valence > 0 ? "text-[var(--c-accent)]" : trace.valence < 0 ? "text-[var(--c-cyan)]" : "text-[var(--c-secondary)]";
                          const valBg = trace.valence > 0 ? "bg-[var(--c-accent-bg)] border-[var(--c-surface4)]" : trace.valence < 0 ? "bg-[var(--c-cyan-bg)] border-[var(--c-cyan-bg2)]" : "bg-[var(--c-surface5)] border-[var(--c-surface13)]";
                          
                          return (
                            <div key={idx} className={`${valBg} p-2.5 rounded-xl border flex flex-col gap-1 text-[11px] transition-all`}>
                              <div className="flex justify-between items-center">
                                <span className={`font-semibold ${valColor}`}>{valStr}</span>
                                <span className="font-mono text-[10px] text-[var(--c-secondary)] font-semibold">{t("强度", "Strength")}: {Math.round(trace.strength * 100)}%</span>
                              </div>
                              <div className="flex justify-between items-center text-[10px] text-[var(--c-muted)]">
                                <span>{t("被调用/回想次数", "Recall count")}: {trace.count || 1}{t("次", "times")}</span>
                                <span>{t("耗时", "Elapsed")} {Math.round(trace.age || 0)}s {t("前", "ago")}</span>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>

                </div>

              </div>

              {/* RIGHT PANEL: CAUSAL INTERACTIONS, SLEEP, EXPECTATION (5 COLS) */}
              <div className="lg:col-span-5 flex flex-col gap-6">
                
                {/* STIMULUS EVENT PANEL */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[var(--c-surface1)]">
                    <Zap className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("心理刺激引发器 (Stimulator Panel)", "Stimulator Panel")}</h2>
                  </div>

                  <div className="space-y-4">
                    
                    {/* Basic Preset Triggers */}
                    <div>
                      <div className="text-[11px] text-[var(--c-muted)] font-semibold mb-2">{t("预置日常事件 (Presets)", "Presets")}</div>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-2">
                        <button
                          onClick={() => handleTriggerEvent("compliment", t("夸奖激励", "Praise & encouragement"))}
                          className="px-3 py-2 bg-[var(--c-accent-bg)] border border-[var(--c-surface4)] hover:border-[var(--c-accent)] text-[var(--c-accent-st)] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🌸 {t("夸奖激励", "Praise & encouragement")}</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("insult", t("批评指责", "Criticism & blame"))}
                          className="px-3 py-2 bg-[var(--c-cyan-bg)] border border-[var(--c-cyan-bg2)] hover:border-[var(--c-cyan)] text-[var(--c-cyan-dp)] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>💥 {t("批评指责", "Criticism & blame")}</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("betrayal", t("信任背叛", "Trust betrayal"))}
                          className="px-3 py-2 bg-[var(--c-purple-bg)] border border-[var(--c-purple-bg2)] hover:border-[var(--c-purple)] text-[var(--c-purple-dp)] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🔪 {t("信任背叛", "Trust betrayal")}</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("alone", t("独处漠视", "Solitary neglect"))}
                          className="px-3 py-2 bg-[var(--c-surface5)] border border-[var(--c-surface8)] hover:border-[var(--c-muted2)] text-[var(--c-secondary)] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🕸️ {t("独处漠视", "Solitary neglect")}</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("rest", t("主动闭目", "Active closure"))}
                          className="px-3 py-2 bg-[var(--c-cyan-bg3)] border border-[var(--c-bluecyan-bg)] hover:border-[var(--c-bluecyan)] text-[var(--c-bluecyan-dp)] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🧘 {t("主动闭目", "Active closure")}</span>
                        </button>
                      </div>
                    </div>

                    {/* Advanced Custom Vectors */}
                    <div className="border-t border-[var(--c-surface1)] pt-3">
                      <div className="flex justify-between items-center text-[11px] text-[var(--c-muted)] font-semibold mb-2">
                        <span>{t("自定义心理向量 (Inter感受 Vector)", "Custom psychological vector (Interoceptive Vector)")}</span>
                        <span className="text-[var(--c-accent)] font-bold">{t("精确调制", "Precise modulation")}</span>
                      </div>

                      <div className="space-y-3 bg-[var(--c-white)] p-3.5 rounded-xl border border-[var(--c-border)]">
                        {/* Threat Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("威胁感知强度 (Threat)", "Threat")}</span>
                            <span className="font-mono text-[var(--c-cyan)] font-bold">+{customThreat.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customThreat} onChange={(e) => setCustomThreat(parseFloat(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Belonging Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("归属反馈负荷 (Belonging)", "Belonging")}</span>
                            <span className={`font-mono font-bold ${customBelonging > 0 ? "text-[var(--c-accent)]" : customBelonging < 0 ? "text-[var(--c-cyan)]" : "text-[var(--c-muted)]"}`}>
                              {customBelonging > 0 ? `+${customBelonging.toFixed(1)}` : customBelonging.toFixed(1)}
                            </span>
                          </div>
                          <input 
                            type="range" min="-1" max="1" step="0.1" 
                            value={customBelonging} onChange={(e) => setCustomBelonging(parseFloat(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Autonomy Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("意志掌控掌控感 (Autonomy)", "Autonomy")}</span>
                            <span className="font-mono text-[var(--c-bluecyan-dp)] font-bold">+{customAutonomy.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customAutonomy} onChange={(e) => setCustomAutonomy(parseFloat(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Fatigue Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("事件消耗疲劳 (Fatigue)", "Event fatigue")}</span>
                            <span className="font-mono text-[var(--c-accent-lt2)] font-bold">+{customFatigue.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customFatigue} onChange={(e) => setCustomFatigue(parseFloat(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Shame Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("自我否定羞耻源 (Shame)", "Shame")}</span>
                            <span className="font-mono text-[var(--c-bluecyan2)] font-bold">+{customShame.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customShame} onChange={(e) => setCustomShame(parseFloat(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>

                        <div className="flex gap-2 pt-1">
                          <input 
                            type="text" 
                            placeholder={t("匹配事件ID (可选)...", "Match event ID (optional)...")}
                            value={customEventId}
                            onChange={(e) => setCustomEventId(e.target.value)}
                            className="bg-[var(--c-white)] border border-[var(--c-border)] text-xs px-3 py-1.5 rounded-lg text-[var(--c-text)] placeholder:text-[var(--c-border2)] focus:outline-none focus:border-[var(--c-accent)] focus:ring-1 focus:ring-[var(--c-accent)]/20 flex-1 font-mono"
                          />
                          <button
                            onClick={handleInjectCustomVector}
                            className="px-4 py-1.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-xs rounded-lg active:scale-95 transition-all shadow-sm"
                          >
                            {t("注入向量", "Inject vector")}
                          </button>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>

                {/* THE FUTURE EXPECTATION MATRIX */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                    <Sparkles className="w-4 h-4 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("未来结果预期机制 (Expectations System)", "Future expectation mechanism (Expectations System)")}</h2>
                  </div>

                  <form onSubmit={handleSetExpectation} className="space-y-3.5">
                    <div className="flex flex-col sm:flex-row gap-2.5">
                      <input 
                        type="text" 
                        placeholder={t("绑定预期事件ID...", "Bind expectation event ID...")}
                        required
                        value={expEventId}
                        onChange={(e) => setExpEventId(e.target.value)}
                        className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-xl px-3 py-2 text-xs text-[var(--c-text)] placeholder:text-[var(--c-border2)] focus:outline-none focus:border-[var(--c-accent)] sm:w-1/2 font-mono"
                      />
                      <button 
                        type="submit"
                        className="px-4 py-2 bg-[var(--c-white)] hover:bg-[var(--c-surface2)] text-[var(--c-accent-dp)] font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 border border-[var(--c-border)] transition-all active:scale-95 shadow-xs"
                      >
                        <Plus className="w-3.5 h-3.5 text-[var(--c-accent)]" /> {t("设定心理预期", "Set psychological expectation")}
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3.5 bg-[var(--c-white)] p-3 rounded-xl border border-[var(--c-border)]">
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-[var(--c-secondary)] font-medium">{t("预期效价 (Valence)", "Expected valence (Valence)")}</span>
                          <span className={expValence > 0 ? "text-[var(--c-accent)] font-mono font-bold" : "text-[var(--c-cyan)] font-mono font-bold"}>
                            {expValence > 0 ? `${t("期待 +", "Expecting +")}${expValence}` : `${t("担忧", "Worrying")} ${expValence}`}
                          </span>
                        </div>
                        <input 
                          type="range" min="-1" max="1" step="0.2"
                          value={expValence} onChange={(e) => setExpValence(parseFloat(e.target.value))}
                          className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                        />
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-[var(--c-secondary)] font-medium">{t("预期确信度 (Confidence)", "Expected confidence (Confidence)")}</span>
                          <span className="text-[var(--c-bluecyan)] font-mono font-bold">{Math.round(expConfidence * 100)}%</span>
                        </div>
                        <input 
                          type="range" min="0" max="1" step="0.1"
                          value={expConfidence} onChange={(e) => setExpConfidence(parseFloat(e.target.value))}
                          className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                        />
                      </div>
                    </div>
                  </form>

                  {/* Active expectations queue */}
                  <div className="mt-3.5 pt-3.5 border-t border-[var(--c-surface1)]">
                    <div className="text-[10px] text-[var(--c-muted)] font-semibold mb-2">{t("已悬挂的主观预期 (Pending Queue)", "Pending subjective expectations (Pending Queue)")}</div>
                    <div className="space-y-1.5 max-h-[110px] overflow-y-auto pr-1">
                      {Object.keys(snapshot.snap.expected_events || {}).length === 0 ? (
                        <div className="text-[10px] text-[var(--c-muted)] italic py-3 text-center">
                          {t("当前无悬置预期。匹配事件ID将结算 Surprise / Disappointment。", "No pending expectations. Matching event ID will settle Surprise / Disappointment.")}
                        </div>
                      ) : (
                        Object.keys(snapshot.snap.expected_events || {}).map((key) => {
                          const exp = snapshot.snap.expected_events?.[key];
                          return (
                            <div key={key} className="bg-[var(--c-white)] px-3 py-2 rounded-xl border border-[var(--c-border)] flex items-center justify-between text-[10px] shadow-xs">
                              <span className="font-mono text-[var(--c-text)] font-bold">"{key}"</span>
                              <div className="flex items-center gap-3 font-mono text-[var(--c-secondary)]">
                                <span>{t("效价", "Valence")}: <span className={exp.valence > 0 ? "text-[var(--c-accent)] font-bold" : "text-[var(--c-cyan)] font-bold"}>{exp.valence > 0 ? `+${exp.valence}` : exp.valence}</span></span>
                                <span>{t("确信度", "Confidence")}: <span className="text-[var(--c-bluecyan)] font-bold">{Math.round(exp.confidence * 100)}%</span></span>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>

                </div>

                {/* DEFENSE MECHANISM & COGNITIVE DISSONANCE */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                    <AlertTriangle className="w-4 h-4 text-[var(--c-accent-lt2)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("防御堡垒及认知冲突 (Defense & Conflict)", "Defense fortress & cognitive conflict (Defense & Conflict)")}</h2>
                  </div>

                  <div className="space-y-3.5">
                    {/* Defense Progress Loaders */}
                    <div className="grid grid-cols-3 gap-3 bg-[var(--c-white)] p-3 rounded-xl border border-[var(--c-border)]">
                      
                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[var(--c-muted)] font-semibold">{t("否认仓 (Denial)", "Denial")}</div>
                        <div className="text-xs font-bold text-[var(--c-secondary)] font-mono">
                          {(snapshot.snap.denial_load || 0).toFixed(2)}/1.2
                        </div>
                        <div className="h-1 bg-[var(--c-surface3)] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[var(--c-bluecyan2)] transition-all duration-300" 
                            style={{ width: `${Math.min(100, ((snapshot.snap.denial_load || 0) / 1.2) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[var(--c-muted)] font-semibold">{t("合理化仓 (Ration)", "Rationalization")}</div>
                        <div className="text-xs font-bold text-[var(--c-secondary)] font-mono">
                          {(snapshot.snap.rationalization_load || 0).toFixed(2)}/1.0
                        </div>
                        <div className="h-1 bg-[var(--c-surface3)] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[var(--c-bluecyan)] transition-all duration-300" 
                            style={{ width: `${Math.min(100, (snapshot.snap.rationalization_load || 0) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[var(--c-muted)] font-semibold">{t("压抑仓 (Repress)", "Repression")}</div>
                        <div className="text-xs font-bold text-[var(--c-secondary)] font-mono">
                          {(snapshot.snap.suppression_load || 0).toFixed(2)}/1.5
                        </div>
                        <div className="h-1 bg-[var(--c-surface3)] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[var(--c-cyan)] transition-all duration-300" 
                            style={{ width: `${Math.min(100, ((snapshot.snap.suppression_load || 0) / 1.5) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                    </div>

                    {/* Cognitive Dissonance inducer */}
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[var(--c-white)] p-3 rounded-xl border border-[var(--c-border)] shadow-xs">
                      <div>
                        <div className="text-xs font-semibold text-[var(--c-text)]">{t("认知失调 (Cognitive Dissonance)", "Cognitive Dissonance")}</div>
                        <p className="text-[10px] text-[var(--c-muted)] mt-0.5">{t("当行为与信念冲突，制造压力张力，逼退能量。", "When actions conflict with beliefs, create tension that forces energy retreat.")}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-[var(--c-accent-lt2)] bg-[var(--c-white)] border border-[var(--c-border)] px-1.5 py-0.5 rounded shadow-xs">
                          {(snapshot.snap.cognitive_dissonance || 0).toFixed(2)}
                        </span>
                        <button
                          onClick={() => {
                            updateEngineState((engine) => {
                              engine.induceDissonance(0.3);
                            });
                            addNotification(`⚠️ ${t("信念与行为发生失调！张力、愧疚感上升，消耗5点生理能量。", "Belief-behavior dissonance! Tension and guilt rise, consuming 5 physical energy.")}`, "warning");
                          }}
                          className="px-2.5 py-1 bg-[var(--c-accent-lt2)] hover:bg-[var(--c-accent5)] text-white font-bold text-[10px] rounded-lg transition-all active:scale-95 shadow-sm"
                        >
                          {t("失调触发", "Trigger dissonance")}
                        </button>
                      </div>
                    </div>

                  </div>
                </div>

                {/* TIMELAPSE & CHRONOS SYSTEM OVERRIDE */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                    <Clock className="w-4 h-4 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("时空跃迁与睡眠机能 (Time & Sleep Engine)", "Time & Sleep Engine")}</h2>
                  </div>

                  <div className="space-y-4">
                    {/* Time accelerator slider */}
                    <div>
                      <div className="flex justify-between items-center text-[10px] text-[var(--c-muted)] font-semibold mb-2">
                        <span>{t("顺延加速虚空空转 (Virtual Idle Time)", "Virtual Idle Time")}</span>
                        <span className="text-[var(--c-accent)] font-bold">{t("遗忘和自修复", "Forgetting & self-repair")}</span>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleIdleSimulation(10)}
                          className="px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-surface2)] text-[var(--c-accent-dp)] text-[10px] font-semibold rounded-lg border border-[var(--c-border)] flex-1 transition-all shadow-xs"
                        >
                          +10s
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(60)}
                          className="px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-surface2)] text-[var(--c-accent-dp)] text-[10px] font-semibold rounded-lg border border-[var(--c-border)] flex-1 transition-all shadow-xs"
                        >
                          +1m
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(3600)}
                          className="px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-surface2)] text-[var(--c-accent-dp)] text-[10px] font-semibold rounded-lg border border-[var(--c-border)] flex-1 transition-all shadow-xs"
                        >
                          +1h
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(43200)}
                          className="px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-surface2)] text-[var(--c-accent-dp)] text-[10px] font-semibold rounded-lg border border-[var(--c-border)] flex-1 transition-all shadow-xs"
                        >
                          +12h
                        </button>
                      </div>
                    </div>

                    {/* Sleep module */}
                    <div className="border-t border-[var(--c-surface1)] pt-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-[11px] text-[var(--c-muted)] font-semibold">{t("生理深眠重构 (Sleep Sim)", "Sleep Sim")}</div>
                        <span className="text-[10px] text-[var(--c-muted)]">{t("清空疲劳和睡眠债", "Clear fatigue and sleep debt")}</span>
                      </div>
                      <div className="flex items-center gap-2.5">
                        <div className="flex-1 space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-[var(--c-secondary)] font-medium">{t("计划睡眠时长", "Planned sleep duration")}</span>
                            <span className="font-mono text-[var(--c-bluecyan)] font-bold">{sleepHours} {t("小时", "hours")}</span>
                          </div>
                          <input 
                            type="range" min="1" max="16" step="1"
                            value={sleepHours} onChange={(e) => setSleepHours(parseInt(e.target.value))}
                            className="w-full accent-[var(--c-accent)] h-1 bg-[var(--c-surface3)] rounded-lg cursor-pointer"
                          />
                        </div>
                        <button
                          onClick={handleSleepSimulation}
                          className="px-4 py-2.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 shadow-sm active:scale-95 transition-all"
                        >
                          <Moon className="w-4 h-4" /> {t("确认入睡", "Confirm sleep")}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* LOGS AND EVENTS FOOTER */}
              <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
                
                {/* NOTIFICATION LIVE ALERTS FEED */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center justify-between mb-3 pb-2 border-b border-[var(--c-surface1)]">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("智能体感知与爆发日志 (Perception Logs)", "Perception Logs")}</h2>
                    </div>
                    <button 
                      onClick={() => setNotifications([])}
                      className="text-[10px] text-[var(--c-muted)] hover:text-[var(--c-cyan)] font-semibold"
                    >
                      {t("清空日志", "Clear logs")}
                    </button>
                  </div>

                  <div className="space-y-2 h-[160px] overflow-y-auto pr-1">
                    {notifications.length === 0 ? (
                      <div className="py-12 text-center text-xs text-[var(--c-muted)] italic">
                        {t("等待因果事件触发。流体日志为空。", "Awaiting causal events. Fluid log is empty.")}
                      </div>
                    ) : (
                      notifications.map((n) => {
                        let dotColor = "bg-[var(--c-bluecyan)]";
                        if (n.type === "warning") dotColor = "bg-[var(--c-accent-lt2)]";
                        if (n.type === "error") dotColor = "bg-[var(--c-cyan)]";
                        if (n.type === "success") dotColor = "bg-[var(--c-accent)]";
                        
                        return (
                          <div key={n.id} className="bg-[var(--c-white)] p-2 rounded-xl border border-[var(--c-border)] flex items-start gap-2.5 text-[11px] leading-relaxed shadow-xs">
                            <span className={`w-2 h-2 rounded-full ${dotColor} mt-1.5 shrink-0`}></span>
                            <div className="flex-1">
                              <span className="text-[var(--c-text)] font-medium">{n.text}</span>
                              <div className="text-[9px] text-[var(--c-muted)] font-mono mt-0.5">{n.time}</div>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* GENERAL SUMMARY OVERVIEW OF THE EXTENSION */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                      <Sparkles className="w-4 h-4 text-[var(--c-accent)]" />
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("Chrome 扩展一键发布说明", "Chrome extension one-click publish guide")}</h2>
                    </div>
                    <p className="text-xs text-[var(--c-secondary)] leading-relaxed">
                      {t("本看板完整模拟了 SPL 心理流体推理引擎 (V8.0)。其状态与记忆、自尊、慢心境、睡眠债深度绑定，在 Chrome 扩展的生命周期中进行持久化保存，从而实现浏览器端“拥有自主人格”的持久化心理智能体。", "This dashboard fully simulates the SPL Psychological Fluid Reasoning Engine (V8.0). Its state is deeply bound to memory, self-esteem, slow mood, and sleep debt, persisted across the Chrome extension lifecycle to realize a browser-side persistent psychological agent with its own personality.")}
                    </p>
                    <div className="grid grid-cols-2 gap-3 mt-4">
                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-border)] shadow-xs">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("主入口界面", "Main entry interface")}</div>
                        <div className="text-xs font-bold text-[var(--c-secondary)] mt-0.5">Vite HTML + Popup</div>
                      </div>
                      <div className="bg-[var(--c-white)] p-2.5 rounded-xl border border-[var(--c-border)] shadow-xs">
                        <div className="text-[10px] text-[var(--c-muted)] font-semibold">{t("存储方案", "Storage solution")}</div>
                        <div className="text-xs font-bold text-[var(--c-secondary)] mt-0.5">Chrome Local Storage</div>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setActiveTab("dev_tools")}
                    className="w-full py-2.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-xs rounded-xl active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4 shadow-sm"
                  >
                    <span>📦 {t("前往打包 Chrome 扩展 ZIP 格式", "Go pack Chrome extension ZIP")}</span>
                    <ChevronRight className="w-4 h-4 text-white" />
                  </button>
                </div>

              </div>

            </motion.div>
          ) : activeTab === "chat" ? (
            <motion.div
              key="chat_tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col h-[calc(100vh-124px)]"
            >
              
              {/* API SETTINGS MODAL (toggled by gear button in chat header) */}
              {showApiConfig && (
                <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/30 backdrop-blur-sm p-4" onClick={() => setShowApiConfig(false)}>
                  <div className="bg-[var(--c-white)] rounded-2xl shadow-2xl border border-[var(--c-border)] p-5 w-[min(92vw,30rem)] max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--c-surface1)]">
                      <h2 className="text-sm font-semibold font-display text-[var(--c-text)]">{t("⚙️ 设置", "⚙️ Settings")}</h2>
                      <button onClick={() => setShowApiConfig(false)} className="text-[var(--c-muted)] hover:text-[var(--c-cyan)] text-lg leading-none w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[var(--c-cyan-bg)] transition-all">×</button>
                    </div>
                    <div className="flex flex-col gap-4">
                {/* INTERFACE CREDENTIALS */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card space-y-4">
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--c-surface1)]">
                    <Lock className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">
                      {t("🔑 大模型API直连配置", "🔑 API Configuration")}
                    </h2>
                  </div>

                  {/* Provider selection */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[var(--c-muted)] font-semibold block">{t("AI 服务商", "API Provider")}</label>
                    <select
                      value={apiProvider}
                      onChange={(e) => {
                        const prov = e.target.value as any;
                        setApiProvider(prov);
                        localStorage.setItem("spl_api_provider", prov);
                        // Autofill default base url and model
                        const d = getDefaultConfig(prov);
                        setApiModel(d.model);
                        setApiBaseUrl(d.url);
                        localStorage.setItem("spl_api_model", d.model);
                        localStorage.setItem("spl_api_base_url", d.url);
                      }}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[var(--c-border)] bg-[var(--c-white)] text-[var(--c-text)] font-semibold focus:outline-none focus:border-[var(--c-accent)]"
                    >
                      <option value="openai">OpenAI (GPT-5.5)</option>
                      <option value="claude">Anthropic Claude (Sonnet 5)</option>
                      <option value="gemini">Google Gemini (3.6 Flash)</option>
                      <option value="deepseek">DeepSeek (V4 Flash)</option>
                      <option value="glm">{t("智谱 GLM", "Zhipu GLM")} (5.3)</option>
                      <option value="kimi">Moonshot Kimi (K2.6)</option>
                      <option value="qwen">{t("通义千问 Qwen", "Qwen")} (3.8 Max)</option>
                      <option value="doubao">{t("豆包 Doubao", "Doubao")} (Seed 2.1 Pro)</option>
                      <option value="grok">xAI Grok (Grok-4)</option>
                      <option value="llama">Meta Llama (Llama-4 70B via Together)</option>
                      <option value="nvidia">NVIDIA NIM (Nemotron 70B)</option>
                      <option value="local">Local LLM (Ollama / LM Studio)</option>
                    </select>
                  </div>

                  {/* API Key */}
                  {apiProvider !== "local" && (
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <label className="text-[10px] text-[var(--c-muted)] font-semibold block">{t("API 密钥 (API Key)", "API Secret Key")}</label>
                        <span className="text-[8px] text-[var(--c-muted)] italic">{t("仅存在您本地浏览器", "Saved locally only")}</span>
                      </div>
                      <input
                        type="password"
                        value={apiKey}
                        placeholder="sk-..."
                        onChange={(e) => {
                          setApiKey(e.target.value);
                          localStorage.setItem("spl_api_key", e.target.value);
                        }}
                        className="w-full px-3 py-2 text-xs rounded-lg border border-[var(--c-border)] bg-[var(--c-white)] text-[var(--c-text)] font-mono focus:outline-none focus:border-[var(--c-accent)]"
                      />
                    </div>
                  )}

                  {/* API Base URL */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[var(--c-muted)] font-semibold block">{t("代理 / 基础URL (Base URL)", "API Endpoint Base URL")}</label>
                    <input
                      type="text"
                      value={apiBaseUrl}
                      placeholder="https://..."
                      onChange={(e) => {
                        setApiBaseUrl(e.target.value);
                        localStorage.setItem("spl_api_base_url", e.target.value);
                      }}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[var(--c-border)] bg-[var(--c-white)] text-[var(--c-text)] font-mono focus:outline-none focus:border-[var(--c-accent)]"
                    />
                  </div>

                  {/* Qwen Bailian workspace domain hint */}
                  {apiProvider === "qwen" && (
                    <div className="bg-[var(--c-white)] border border-[var(--c-surface6)] p-2.5 rounded-lg text-[9px] text-[var(--c-muted)] leading-relaxed">
                      💡{" "}
                      {t("千问 3.8 可选百炼业务空间专属域名（更稳更快）：", "Qwen 3.8 optional Bailian workspace domain (faster & more stable):")}{" "}
                      <span className="text-[var(--c-accent)] font-mono">https://{"{WorkspaceId}"}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1</span>
                      <br />
                      {t("原 dashscope.aliyuncs.com 域名仍可用，无需改动。", "The legacy dashscope.aliyuncs.com domain still works \u2014 no change needed.")}
                    </div>
                  )}

                  {/* Model Name */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[var(--c-muted)] font-semibold block">{t("模型名称 (Model)", "AI Model Name")}</label>
                    <input
                      type="text"
                      value={apiModel}
                      placeholder="e.g. gpt-5.5"
                      onChange={(e) => {
                        setApiModel(e.target.value);
                        localStorage.setItem("spl_api_model", e.target.value);
                      }}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[var(--c-border)] bg-[var(--c-white)] text-[var(--c-text)] font-mono focus:outline-none focus:border-[var(--c-accent)]"
                    />
                  </div>

                  {/* Action buttons */}
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => {
                        const d = getDefaultConfig(apiProvider);
                        setApiModel(d.model);
                        setApiBaseUrl(d.url);
                        localStorage.setItem("spl_api_model", d.model);
                        localStorage.setItem("spl_api_base_url", d.url);
                        addNotification(t("已恢复默认服务配置", "Default model configuration loaded"), "info");
                      }}
                      className="text-[9px] text-[var(--c-accent)] font-semibold bg-[var(--c-white)] border border-[var(--c-border)] hover:bg-[var(--c-surface2)] px-2.5 py-1.5 rounded-md flex-1 text-center transition-all"
                    >
                      {t("📋 恢复该渠道默认值", "Reset to Default")}
                    </button>
                    <button
                      onClick={() => {
                        setApiKey("");
                        localStorage.removeItem("spl_api_key");
                        addNotification(t("已清除本地密钥存储", "Cleared saved API Key"), "info");
                      }}
                      className="text-[9px] text-[var(--c-cyan)] font-semibold bg-[var(--c-white)] border border-[var(--c-cyan-bg2)] hover:bg-[var(--c-cyan-bg)] px-2.5 py-1.5 rounded-md flex-1 text-center transition-all"
                    >
                      {t("🗑️ 清空本地密钥", "Clear Key")}
                    </button>
                  </div>

                  {/* Connection Warning */}
                  <div className="bg-[var(--c-white)] border border-[var(--c-surface6)] p-2.5 rounded-lg text-[9px] text-[var(--c-muted)] leading-relaxed">
                    💡 <strong>{t("离线直连声明", "Direct Browser Connection")}:</strong>{" "}
                    {t(
                      "此端直连大模型 API，无中间服务器拦截。您的 API 密钥及聊天历史仅安全保存在浏览器本地（LocalStorage/Chrome Storage）中，不会上传给第三方。本地 Ollama 请确保开启 CORS，添加环境变量 OLLAMA_ORIGINS=\"*\"。",
                      "This app connects directly to the model API from your browser. Your API Keys are saved only in your browser storage. For Local Ollama, please configure OLLAMA_ORIGINS=\"*\" to prevent CORS errors."
                    )}
                  </div>
                </div>

                {/* AI IMPORT PERSONA QUICK ENTRY */}
                <div className="bg-[var(--c-white)] border border-dashed border-[var(--c-accent-lt)]/60 rounded-xl p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-[var(--c-muted)] font-bold uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-[var(--c-accent)]" />
                      {t("AI 智能导入角色", "AI Import Persona")}
                    </span>
                    <span className="text-[8px] text-[var(--c-border2)] font-mono">LLM {"\u2192"} Agent</span>
                  </div>
                  <button
                    onClick={() => aiImportInputRef.current?.click()}
                    className="flex items-center gap-2 w-full px-3 py-2.5 rounded-lg bg-[var(--c-white)] border border-[var(--c-border)] hover:bg-[var(--c-white)] hover:border-[var(--c-accent-lt)] text-xs font-semibold text-[var(--c-accent)] transition-all"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    {t("上传角色文档", "Upload Persona Doc")}
                  </button>
                  <p className="text-[9px] text-[var(--c-muted)] leading-relaxed">
                    {t("支持 .txt/.md/.docx/.xlsx 等，大模型自动识别角色性格并生成新智能体。", "Supports .txt/.md/.docx/.xlsx etc. LLM auto-detects character traits and creates a new agent.")}
                  </p>
                </div>

                {/* CONVERSATION PREFERENCES */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card space-y-4">
                  <div className="flex items-center gap-2 pb-2 border-b border-[var(--c-surface1)]">
                    <Sparkles className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">
                      {t("🎚️ 对话偏好（自动调参）", "🎚️ Conversation Preferences")}
                    </h2>
                  </div>
                  <p className="text-[10px] text-[var(--c-muted)] leading-normal -mt-2">
                    {t("根据你的偏好自动调整 temperature / max tokens，并把回复风格指令注入系统提示。", "Auto-adjusts temperature / max tokens and injects reply-style guidance based on your preference.")}
                  </p>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-semibold text-[var(--c-secondary)]">{t("回复风格", "Reply Style")}</label>
                    <div className="grid grid-cols-3 gap-1.5">
                      {([["creative", "🎨 创意", "🎨 Creative"], ["balanced", "⚖️ 平衡", "⚖️ Balanced"], ["strict", "🧭 严谨", "🧭 Strict"]] as const).map(([val, zh, en]) => (
                        <button
                          key={val}
                          onClick={() => { setPrefStyle(val); localStorage.setItem("spl_pref_style", val); }}
                          className={`text-[10px] font-semibold px-2 py-2 rounded-lg border transition-all ${prefStyle === val ? "bg-[var(--c-accent)] text-white border-[var(--c-accent)] shadow-sm" : "bg-[var(--c-white)] text-[var(--c-muted)] border-[var(--c-border)] hover:bg-[var(--c-surface2)]"}`}
                        >
                          {t(zh, en)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-semibold text-[var(--c-secondary)]">{t("回复长度", "Reply Length")}</label>
                    <div className="grid grid-cols-3 gap-1.5">
                      {([["short", "✂️ 简短", "✂️ Short"], ["medium", "📏 适中", "📏 Medium"], ["long", "📖 详细", "📖 Long"]] as const).map(([val, zh, en]) => (
                        <button
                          key={val}
                          onClick={() => { setPrefLength(val); localStorage.setItem("spl_pref_length", val); }}
                          className={`text-[10px] font-semibold px-2 py-2 rounded-lg border transition-all ${prefLength === val ? "bg-[var(--c-accent)] text-white border-[var(--c-accent)] shadow-sm" : "bg-[var(--c-white)] text-[var(--c-muted)] border-[var(--c-border)] hover:bg-[var(--c-surface2)]"}`}
                        >
                          {t(zh, en)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-semibold text-[var(--c-secondary)]">{t("语气", "Tone")}</label>
                    <div className="grid grid-cols-3 gap-1.5">
                      {([["gentle", "💗 温柔", "💗 Gentle"], ["rational", "🧊 理性", "🧊 Rational"], ["humorous", "😄 幽默", "😄 Humorous"]] as const).map(([val, zh, en]) => (
                        <button
                          key={val}
                          onClick={() => { setPrefTone(val); localStorage.setItem("spl_pref_tone", val); }}
                          className={`text-[10px] font-semibold px-2 py-2 rounded-lg border transition-all ${prefTone === val ? "bg-[var(--c-accent)] text-white border-[var(--c-accent)] shadow-sm" : "bg-[var(--c-white)] text-[var(--c-muted)] border-[var(--c-border)] hover:bg-[var(--c-surface2)]"}`}
                        >
                          {t(zh, en)}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* PERSONA PROMPT PREVIEW */}
                <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] gemini-card">
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--c-surface1)]">
                    <Brain className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                    <h2 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">
                      {t("🧠 实时心理人格 System Prompt", "🧠 Dynamic System Prompt")}
                    </h2>
                  </div>
                  <p className="text-[10px] text-[var(--c-muted)] leading-normal mb-3">
                    {t("由于心理流体在每秒和每次刺激后不断演变更新，大模型对话中注入的系统指令集也已实时映射了智能体的以下最新生理-心理阻抗、能量、自尊、创伤和压抑荷载：", "As the psychological fluids update in real-time, the model prompt incorporates the agent's active energy, self-esteem, active trauma, and repressions:")}
                  </p>

                  {/* 雷达图 + 指标条：直观呈现各流体数值（替代纯文本卡片） */}
                  <div className="bg-[var(--c-white)] border border-[var(--c-border)] p-3 rounded-xl">
                    <FluidRadar
                      data={Object.keys(snapshot.snap.fluid || {}).map((k) => {
                        const meta = FLUID_META[k];
                        const toHex = (meta?.color.match(/to-\[#([0-9A-Fa-f]{6})\]/)?.[1]) || "967A55";
                        return {
                          label: t(k, meta?.nameEn || k),
                          value: snapshot.snap.fluid?.[k] || 0,
                          color: `#${toHex}`
                        };
                      })}
                    />
                  </div>

                  {/* 折叠：查看原始 System Prompt */}
                  <button
                    onClick={() => setShowRawPrompt((v) => !v)}
                    className="mt-2 text-[10px] text-[var(--c-accent)] font-semibold hover:underline"
                  >
                    {showRawPrompt ? t("收起原始 System Prompt", "Hide raw System Prompt") : t("查看原始 System Prompt", "View raw System Prompt")}
                  </button>
                  {showRawPrompt && (
                    <div className="mt-2 bg-[var(--c-white)] border border-[var(--c-border)] p-3 rounded-xl max-h-[220px] overflow-y-auto">
                      <pre className="text-[9px] text-[var(--c-secondary)] font-mono whitespace-pre-wrap leading-relaxed select-all">
                        {generateSystemPromptPreview()}
                      </pre>
                    </div>
                  )}
                
                    </div>
                  </div>
                </div>
                </div>
              )}
              {/* CHAT BOX - FULL WIDTH */}
              <div className="flex-1 bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.015)] flex flex-col overflow-hidden">
                
                {/* Chat header */}
                <div className="bg-[var(--c-white)] border-b border-[var(--c-surface1)] p-3 sm:p-4 flex flex-col gap-2.5 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {/* 隐藏聊天头 Logo */}
                    <div className="w-8 h-8 rounded-lg bg-[var(--c-white)] border border-[var(--c-border)] flex items-center justify-center shrink-0 hidden">
                      <Sparkles className="w-4 h-4 text-[var(--c-accent)] animate-pulse" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-[10px] sm:text-xs font-bold text-[var(--c-text)] font-display uppercase tracking-wide truncate sm:whitespace-normal">
                        {t("流体意识对话通道 (Psyche-Fluid Channel)", "Fluid Consciousness Channel")}
                      </h3>
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[9px] sm:text-[10px] font-mono mt-0.5">
                        <span className="text-[var(--c-accent)]">{t("自尊", "Self-Esteem")}: <span className="font-bold">{((snapshot.snap.self_esteem || 0) * 100).toFixed(0)}%</span></span>
                        <span className="text-[var(--c-bluecyan)]">{t("能量", "Energy")}: <span className="font-bold">{(snapshot.snap.energy || 0).toFixed(0)}/100</span></span>
                        <span className="text-[var(--c-cyan)]">{t("疲劳", "Fatigue")}: <span className="font-bold">{((snapshot.snap.fatigue || 0) * 100).toFixed(0)}%</span></span>
                        <span className="text-[var(--c-accent-lt2)]">{t("认知失调", "Cognitive Dissonance")}: <span className="font-bold">{(snapshot.snap.cognitive_dissonance || 0).toFixed(2)}</span></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => setShowApiConfig(!showApiConfig)}
                    title={t("API 设置", "API Settings")}
                    className={`text-[10px] sm:text-xs font-semibold border rounded-md px-2.5 py-1.5 bg-[var(--c-white)] transition-all active:scale-95 flex items-center gap-1 ${showApiConfig ? "text-white bg-[var(--c-accent)] border-[var(--c-accent)]" : "text-[var(--c-muted)] hover:text-[var(--c-accent)] border-[var(--c-border)] hover:bg-[var(--c-white)]"}`}
                  >
                    <Settings className="w-3.5 h-3.5" />
                    <span className="lowercase">api</span>
                  </button>
                  <button
                    onClick={() => {
                      if (chatMessages.length === 0) {
                        addNotification(t("暂无对话记录可导出", "No chat history to export"), "info");
                        return;
                      }
                      const header = t(
                        "=== SPL 心理流体对话导出 ===\n引擎版本 V8.0 | 导出时间: ",
                        "=== SPL Psychological Fluid Chat Export ===\nExported at: "
                      );
                      const lines = chatMessages.map((m) => {
                        const who = m.role === "user" ? t("用户", "User") : t("智能体", "Agent");
                        return `[${m.timestamp}] ${who}:\n${m.content}`;
                      });
                      const blob = new Blob([header + new Date().toLocaleString() + "\n\n" + lines.join("\n\n---\n\n") + "\n"], {
                        type: "text/plain;charset=utf-8"
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `spl-chat-${new Date().toISOString().slice(0, 10)}.txt`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                      addNotification(t("聊天记录已导出为 txt", "Chat exported as txt"), "success");
                    }}
                    className="text-[10px] sm:text-xs text-[var(--c-muted)] hover:text-[var(--c-accent)] font-semibold border border-[var(--c-border)] rounded-md px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-white)] transition-all active:scale-95 flex items-center gap-1"
                    title={t("导出对话记录", "Export chat")}
                  >
                    <Download className="w-3.5 h-3.5" />
                    {t("导出", "Export")}
                  </button>

                  <button
                    onClick={() => {
                      if (window.confirm(t("是否确认清空对话历史？", "Are you sure you want to clear chat history?"))) {
                        setChatMessages([
                          {
                            id: "welcome",
                            role: "assistant",
                            content: t(
                              "您好，我是由 SPL 心理流体推理引擎 V8.0 驱动的智能人格。我的状态已重置，请随意与我对话。",
                              "Hello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My status has been reset. Feel free to talk to me."
                            ),
                            timestamp: new Date().toLocaleTimeString()
                          }
                        ]);
                      }
                    }}
                    className="text-[10px] sm:text-xs text-[var(--c-muted)] hover:text-[var(--c-cyan)] font-semibold border border-[var(--c-border)] rounded-md px-2.5 py-1.5 bg-[var(--c-white)] hover:bg-[var(--c-white)] transition-all active:scale-95"
                  >
                    {t("🗑️ 清空历史", "Clear Chat")}
                  </button>
                  </div>
                </div>

                {/* Messages list */}
                <div className="flex-1 bg-[var(--c-white)] p-3 sm:p-5 overflow-y-auto space-y-3 sm:space-y-4">
                  {(() => {
                    const isWelcome = chatMessages.length > 0 && chatMessages[0].id === "welcome";
                    const displayMessages = isWelcome ? chatMessages.slice(1) : chatMessages;

                    return (
                      <>
                        {isWelcome && (
                          <div className="px-1 pt-2 pb-1">
                            <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-5 sm:p-6 shadow-sm max-w-lg mx-auto text-center">
                              <div className="w-12 h-12 sm:w-14 sm:h-14 mx-auto mb-3 sm:mb-4 rounded-2xl bg-gradient-to-br from-[var(--c-surface14)] to-[var(--c-surface15)] border border-[var(--c-surface16)] flex items-center justify-center shadow-inner">
                                <Brain className="w-6 h-6 sm:w-7 sm:h-7 text-[var(--c-accent)]" />
                              </div>
                              <p className="text-xs sm:text-sm text-[var(--c-text-st)] leading-relaxed whitespace-pre-wrap">
                                {chatMessages[0].content}
                              </p>
                            </div>
                          </div>
                        )}

                        {displayMessages.map((msg, msgIndex) => {
                          const isUser = msg.role === "user";
                          return (
                            <motion.div
                              key={msg.id}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.35, delay: Math.min(msgIndex * 0.06, 0.45), ease: "easeOut" }}
                              className={`flex ${isUser ? "justify-end" : "justify-start"} items-start gap-2.5`}
                            >
                              {!isUser && (
                                <div className="w-7 h-7 rounded-lg bg-[var(--c-white)] border border-[var(--c-border)] flex items-center justify-center shrink-0 shadow-xs">
                                  <Brain className="w-3.5 h-3.5 text-[var(--c-accent)]" />
                                </div>
                              )}
                              <div className={`flex flex-col ${isUser ? "items-end max-w-[80%] sm:max-w-[70%]" : "items-start max-w-[85%] sm:max-w-[70%]"}`}>
                                <div
                                  className={`px-4 py-3 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs whitespace-pre-wrap ${
                                    isUser
                                      ? "bg-gradient-to-br from-[var(--c-accent-lt)] to-[var(--c-accent)] text-white rounded-tr-none"
                                      : "bg-[var(--c-white)] border border-[var(--c-border)] text-[var(--c-text)] rounded-tl-none"
                                  }`}
                                >
                                  {msg.attachments && msg.attachments.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mb-2">
                                      {msg.attachments.map((att) =>
                                        att.kind === "image" && att.dataUrl ? (
                                          <img
                                            key={att.id}
                                            src={att.dataUrl}
                                            alt={att.name}
                                            className="w-24 h-24 object-cover rounded-lg border border-white/30 shadow-sm"
                                          />
                                        ) : (
                                          <div
                                            key={att.id}
                                            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-black/10 text-white/90 text-[10px] font-semibold max-w-[200px]"
                                          >
                                            <FileText className="w-3.5 h-3.5 shrink-0" />
                                            <span className="truncate">{att.name}</span>
                                          </div>
                                        )
                                      )}
                                    </div>
                                  )}
                                  {msg.content}
                                </div>
                                <span className="text-[8px] text-[var(--c-muted)] font-mono mt-1 px-1">
                                  {msg.timestamp}
                                </span>
                              </div>
                            </motion.div>
                          );
                        })}
                      </>
                    );
                  })()}

                  {isTyping && (
                    <div className="flex justify-start items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-[var(--c-white)] border border-[var(--c-border)] flex items-center justify-center shrink-0 shadow-xs">
                        <Brain className="w-3.5 h-3.5 text-[var(--c-accent)] animate-spin" />
                      </div>
                      <div className="px-4 py-2 bg-[var(--c-white)] border border-[var(--c-border)] text-[var(--c-muted)] rounded-2xl rounded-tl-none text-[10px] italic flex items-center gap-1.5 shadow-xs">
                        <span className="w-1.5 h-1.5 rounded-full bg-[var(--c-accent)] animate-bounce" style={{ animationDelay: "0ms" }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[var(--c-accent)] animate-bounce" style={{ animationDelay: "150ms" }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[var(--c-accent)] animate-bounce" style={{ animationDelay: "300ms" }}></span>
                        <span>{t("心脑流体运算中...", "Fluid computing...")}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input form */}
                <form
                  onSubmit={handleSendMessage}
                  className="bg-[var(--c-white)] border-t border-[var(--c-surface1)] p-4 flex flex-col gap-2"
                >
                  <div className="flex gap-2 items-center">
                    <input type="file" id="chat-file-input" className="hidden" onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) {
                        if (f.type.startsWith("image/")) {
                          const reader = new FileReader();
                          reader.onload = () => {
                            setInputMessage(prev => prev + (prev ? " " : "") + `[图片: ${f.name}]`);
                            setChatAttachments(prev => [...prev, { id: Math.random().toString(36).substring(7), kind: "image", name: f.name, mime: f.type, size: f.size, dataUrl: reader.result as string }]);
                          };
                          reader.readAsDataURL(f);
                        } else {
                          const reader = new FileReader();
                          reader.onload = () => {
                            const text = reader.result as string;
                            const truncated = text.length > 800 ? text.substring(0, 800) + "...[截断]" : text;
                            setInputMessage(prev => prev + (prev ? " " : "") + `[附件 ${f.name}]: ${truncated}`);
                          };
                          reader.readAsText(f);
                        }
                      }
                      e.target.value = "";
                    }} />
                    <button
                      type="button"
                      onClick={() => document.getElementById("chat-file-input")?.click()}
                      title={t("上传文件/图片", "Upload file/image")}
                      className="p-1.5 rounded-full border border-[var(--c-border)] text-[var(--c-muted)] hover:text-[var(--c-secondary)] hover:border-[var(--c-accent)] hover:bg-[var(--c-surface7)] transition-all shrink-0"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      placeholder={t("向流体心智输入意识信息...", "Type to transmit stimulus message to the fluid mind...")}
                      className="flex-1 px-3 py-1.5 text-xs bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg focus:outline-none focus:border-[var(--c-accent)] placeholder:text-[var(--c-border2)]"
                    />
                    <button
                      type="submit"
                      disabled={isTyping}
                      className="gemini-btn p-2 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white rounded-lg active:scale-95 transition-all flex items-center justify-center shrink-0 shadow-sm"
                    >
                      <Send className="w-4 h-4 text-white" />
                    </button>
                  </div>
                </form>

              </div>

            </motion.div>
          ) : (
            <motion.div
              key="dev_tools_tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="max-w-3xl mx-auto space-y-6"
            >
              
              {/* CHROME EXTENSION BUILDER INFO CARD */}
              <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-6 shadow-[0_8px_30px_rgba(0,0,0,0.015)] relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-[var(--c-accent-lt)]/5 blur-3xl rounded-full pointer-events-none"></div>
                
                <div className="flex items-center gap-3 mb-4 pb-3 border-b border-[var(--c-surface1)]">
                  <Download className="w-5 h-5 text-[var(--c-accent)]" />
                  <div>
                    <h2 className="text-base font-bold font-display text-[var(--c-text)] tracking-wide">{t("打包与下载 Chrome 扩展 ZIP 文件", "Pack & download Chrome extension ZIP")}</h2>
                    <p className="text-xs text-[var(--c-muted)] mt-0.5">{t("将本心理流体推理智能体作为扩展打包并部署到您的浏览器中。", "Pack this psychological fluid reasoning agent as an extension and deploy it to your browser.")}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-[var(--c-white)] p-4 rounded-xl border border-[var(--c-border)] space-y-2">
                    <h3 className="text-xs font-semibold text-[var(--c-text)] flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[var(--c-accent)]"></span>
                      {t("扩展规格", "Package Specification")}
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-[11px] font-mono">
                      <div>
                        <span className="text-[var(--c-muted)]">Manifest Version:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">MV3 (Latest)</span>
                      </div>
                      <div>
                        <span className="text-[var(--c-muted)]">Build Mode:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">Vite Minified Production</span>
                      </div>
                      <div>
                        <span className="text-[var(--c-muted)]">Popup Context:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">Full Offline SPA</span>
                      </div>
                      <div>
                        <span className="text-[var(--c-muted)]">Asset Mode:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">Relative Path (./)</span>
                      </div>
                      <div>
                        <span className="text-[var(--c-muted)]">Permissions:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">["storage"]</span>
                      </div>
                      <div>
                        <span className="text-[var(--c-muted)]">Output Target:</span>{" "}
                        <span className="text-[var(--c-secondary)] font-bold">extension.zip</span>
                      </div>
                    </div>
                  </div>

                  {/* STEP BY STEP LOADING TUTORIAL */}
                  <div className="space-y-3">
                    <h3 className="text-xs font-semibold text-[var(--c-text)] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-[var(--c-accent)]" />
                      {t("部署到 Chrome 浏览器的步骤", "Steps to deploy to Chrome browser")}
                    </h3>

                    <div className="space-y-2 text-xs text-[var(--c-secondary)] pl-1">
                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">1</span>
                        <p className="mt-0.5">
                          {t("点击下方 “下载 Chrome 扩展 ZIP” 按钮，下载由编译引擎打包生成的 extension.zip 压缩包。", "Click the \"Download Chrome Extension ZIP\" button below to download the extension.zip archive packaged by the build engine.")}
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">2</span>
                        <p className="mt-0.5">
                          {t("下载完成后，将 extension.zip 解压到一个本地磁盘目录（例如命名为 spl-extension 文件夹）。", "After download, extract extension.zip into a local directory (e.g. named spl-extension).")}
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">3</span>
                        <p className="mt-0.5">
                          {t("打开 Google Chrome 浏览器，在地址栏输入", "Open Google Chrome browser, type")} <code>chrome://extensions</code> {t("并回车（或通过右上角 菜单 → 扩展程序 → 管理扩展程序 选项进入）。", "in the address bar and press Enter (or access via top-right Menu → Extensions → Manage Extensions).")}
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">4</span>
                        <p className="mt-0.5">
                          {t("在扩展管理页面的右上角，开启 “开发者模式 (Developer Mode)” 开关。", "In the top-right of the extensions page, toggle on \"Developer Mode\".")}
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">5</span>
                        <p className="mt-0.5">
                          {t("点击左上角的 “加载已解压的扩展程序 (Load unpacked)” 按钮，在弹出的文件浏览器中选择您解压出的 dist 文件夹。", "Click \"Load unpacked\" in the top-left, then select the extracted dist folder in the file browser.")}
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[var(--c-white)] border border-[var(--c-border)] text-[10px] font-bold text-[var(--c-accent)] shrink-0 shadow-xs">6</span>
                        <p className="mt-0.5">
                          {t("部署成功！您可以直接在 Chrome 工具栏中点击扩展图标，唤起完全单机运行、离线持久化的心理智能体看板。", "Deployment successful! Click the extension icon in the Chrome toolbar to launch the fully standalone, offline-persistent psychological agent dashboard.")}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* ACTION PACKAGING CARD WITH GLOWING DOWNLOAD BUTTON */}
                  <div className="border-t border-[var(--c-surface1)] pt-6 flex flex-col items-center justify-center text-center">
                    
                    <div className="mb-4">
                      <div className="text-xs text-[var(--c-muted)]">{t("静态资源与构建输出压缩包", "Static assets and build output archive")}</div>
                      <div className="text-[10px] text-[var(--c-border2)] mt-1 font-mono">{t("包含：manifest.json, popup index.html, JS/CSS bundles, icon.png", "Includes: manifest.json, popup index.html, JS/CSS bundles, icon.png")}</div>
                    </div>

                    <a
                      href="./extension.zip"
                      download="extension.zip"
                      className="inline-flex items-center gap-3 px-8 py-3.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-sm rounded-xl shadow-md transition-all font-display active:scale-[0.98]"
                    >
                      <Download className="w-5 h-5 text-white" />
                      <span>⚡️ {t("下载 Chrome 扩展 ZIP 包 (extension.zip)", "Download Chrome extension ZIP (extension.zip)")}</span>
                    </a>

                    <p className="text-[10px] text-[var(--c-muted)] mt-3 font-mono">
                      {t("* 注：本打包文件基于最新 Vite 生成的 minified 代码包。如果您在开发环境下初次打包，请确保在终端内执行过", "* Note: This package is based on the latest Vite-generated minified build. If packaging for the first time in a dev environment, ensure you have run")} <code>npm run build</code> {t("来生成该 zip 文件。", "in the terminal to generate the zip file.")}
                    </p>

                  </div>

                </div>

              </div>

              {/* SECOND PERSPECTIVE CAUSAL ENGINE ESSENCE SHEET */}
              <div className="bg-[var(--c-white)] border border-[var(--c-border)] rounded-2xl p-6 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                <div className="flex items-center gap-2.5 mb-3 pb-2 border-b border-[var(--c-surface1)]">
                  <Brain className="w-4.5 h-4.5 text-[var(--c-accent)]" />
                  <h3 className="text-sm font-semibold font-display text-[var(--c-text)] tracking-wide">{t("第二视角因果决定论规约", "Second-perspective causal determinism protocol")}</h3>
                </div>
                <div className="text-xs text-[var(--c-secondary)] space-y-2 leading-relaxed font-mono">
                  <p>
                    {t("[逻辑拓扑]: 本智能体放弃了一切关于心理状态的概率学推理(Probabilistic Inference)，全面转换为因果决定论机制。", "[Logical Topology]: This agent abandons all probabilistic inference of psychological states, fully converting to a causal determinism mechanism.")}
                  </p>
                  <p>
                    {t("[决定论链条]: 输入事件 (E) → 认知增益 (Appraisal) → 瞬时流体映射 (Fluid Map) → 防御层级过滤 (Defense Filtration) → 压抑与隐压调节 (Repression Load) → 慢心境自更新 (Mood Dynamics) → 时间膨胀调制 (Dilation)。", "[Determinism Chain]: Input Event (E) → Cognitive Appraisal → Instantaneous Fluid Map → Defense Filtration → Repression Load → Mood Dynamics → Time Dilation.")}
                  </p>
                  <p>
                    [反事实守恒]: 任何外在认可的匮乏或羞耻的过载，都会严格导致自尊指标在微观时间尺度内以对应斜率沉降，直至引发防御壁垒或隐压雪崩破裂。
                  </p>
                </div>
              </div>

              {/* NAVIGATION BUTTON BACK */}
              <div className="flex justify-center">
                <button
                  onClick={() => setActiveTab("dashboard")}
                  className="px-6 py-2 rounded-xl bg-[var(--c-white)] border border-[var(--c-border)] text-xs text-[var(--c-muted)] hover:text-[var(--c-secondary)] font-semibold active:scale-[0.98] transition-all shadow-xs"
                >
                  {t("← 返回心理引擎状态看板", "← Back to psychological engine dashboard")}
                </button>
              </div>

            </motion.div>
          )}

        </AnimatePresence>
      </main>

      {/* ========== BOTTOM NAVIGATION: CHAT + PERSONALITY (Dashboard top-right) ========== */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[72] flex items-center gap-1 bg-[var(--c-white)]/95 backdrop-blur-md p-1 rounded-2xl border border-[var(--c-border)] shadow-lg shadow-black/10">
        <button
          onClick={() => setActiveTab("chat")}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
            activeTab === "chat"
              ? "bg-gradient-to-br from-[var(--c-accent-lt)] via-[var(--c-accent-soft)] to-[var(--c-accent)] text-white shadow-md"
              : "text-[var(--c-muted)] hover:text-[var(--c-secondary)] hover:bg-[var(--c-surface7)]"
          }`}
        >
          <Send className="w-4 h-4" />
          {t("对话", "Chat")}
        </button>

        <span className="w-px h-6 bg-[var(--c-border)] mx-0.5" aria-hidden="true" />

        <button
          onClick={openAgentList}
          title={t("人格", "Personality")}
          aria-label={t("打开智能体库", "Open agent library")}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all text-[var(--c-muted)] hover:text-[var(--c-secondary)] hover:bg-[var(--c-surface7)]"
        >
          <Users className="w-4 h-4" />
          {t("人格", "Personality")}
        </button>
      </div>

            {/* ========== AGENT LIST DRAGGABLE PANEL ========== */}
      <AnimatePresence>
        {isAgentListOpen && (
          <motion.div
            ref={agentPanelRef}
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.92 }}
            transition={{ duration: 0.2 }}
            role="dialog"
            aria-label={t("智能体库", "Agent Library")}
            className="fixed z-[65] bg-[var(--c-white)] rounded-2xl shadow-2xl shadow-black/15 border border-[var(--c-border)] flex flex-col overflow-hidden"
            style={{
              left: agentPanelPos ? `${agentPanelPos.x}px` : undefined,
              top: agentPanelPos ? `${agentPanelPos.y}px` : undefined,
              right: agentPanelPos ? undefined : 20,
              bottom: agentPanelPos ? undefined : 84,
              width: "min(92vw, 28rem)",
              maxHeight: "min(80vh, 36rem)",
            }}
          >
            {/* Header (drag handle) */}
            <div
              onMouseDown={handlePanelDragStart}
              onTouchStart={handlePanelDragStart}
              className="flex items-center justify-between px-4 py-3 border-b border-[var(--c-surface1)] bg-gradient-to-r from-[var(--c-white)] to-[var(--c-white)] select-none cursor-move touch-none"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--c-accent-lt)] via-[var(--c-accent-soft)] to-[var(--c-accent)] p-0.5 shadow-sm">
                  <div className="w-full h-full rounded-[7px] bg-[var(--c-white)] flex items-center justify-center">
                    <Users className="w-4 h-4 text-[var(--c-accent)]" />
                  </div>
                </div>
                <div>
                  <h2 className="text-xs font-bold font-display text-[var(--c-text)] tracking-wide">
                    {t("🎭 智能体库", "🎭 Agent Library")}
                  </h2>
                  <p className="text-[9px] text-[var(--c-muted)] mt-0.5">
                    {t(
                      `${getAgentsList().length} 个人格 · ${customAgents.length} 个自定义`,
                      `${getAgentsList().length} agents · ${customAgents.length} custom`
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={(e) => { e.stopPropagation(); setAgentPanelMinimized(v => !v); }}
                  onMouseDown={(e) => e.stopPropagation()}
                  onTouchStart={(e) => e.stopPropagation()}
                  aria-label={t("最小化", "Minimize")}
                  title={t("最小化", "Minimize")}
                  className="w-7 h-7 rounded-full flex items-center justify-center text-[var(--c-muted)] hover:bg-[var(--c-surface2)] hover:text-[var(--c-secondary)] transition-all"
                >
                  {agentPanelMinimized ? (
                    <ChevronRight className="w-3.5 h-3.5" />
                  ) : (
                    <Minus className="w-3.5 h-3.5" />
                  )}
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); closeAgentList(); }}
                  onMouseDown={(e) => e.stopPropagation()}
                  onTouchStart={(e) => e.stopPropagation()}
                  aria-label={t("关闭", "Close")}
                  title={t("关闭", "Close")}
                  className="w-7 h-7 rounded-full flex items-center justify-center text-[var(--c-muted)] hover:bg-[var(--c-surface2)] hover:text-[var(--c-secondary)] transition-all"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Body (hidden when minimized) */}
            {!agentPanelMinimized && (
              <>
                {/* Agent list */}
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {getAgentsList().map((preset) => {
                      const isActive = preset.id === activeAgentId;
                      const isBuiltin = !preset.isCustom;
                      const isEditing = editingAgentId === preset.id;

                      return (
                        <div key={preset.id} className="flex flex-col">
                          <div
                            onClick={() => {
                              if (isEditing) return;
                              loadAgentPreset(preset);
                              addNotification(
                                `🎭 ${t("已切换为", "Switched to")}: ${getAgentName(preset)}`,
                                "success"
                              );
                            }}
                            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between relative group ${
                              isActive
                                ? "bg-[var(--c-surface9)] border-[var(--c-accent-lt)] shadow-sm ring-1 ring-[var(--c-accent-lt)]"
                                : "bg-[var(--c-white)] border-[var(--c-border)] hover:bg-[var(--c-white)] hover:border-[var(--c-border2)]"
                            } ${isEditing ? "ring-2 ring-[var(--c-accent)]" : ""}`}
                          >
                            {/* Builtin badge */}
                            {isBuiltin && (
                              <span className="absolute top-2 left-2 text-[7px] font-bold uppercase tracking-wider text-[var(--c-muted)] bg-[var(--c-surface2)] px-1.5 py-0.5 rounded shadow-xs">
                                {t("内置", "BUILTIN")}
                              </span>
                            )}

                            {/* Action buttons */}
                            <div className="absolute top-2 right-2 flex items-center gap-0.5">
                              {!isBuiltin && (
                                <button
                                  onClick={(e) => handleStartEdit(preset, e)}
                                  title={t("编辑", "Edit")}
                                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[var(--c-accent)] hover:bg-[var(--c-surface2)] transition-all"
                                >
                                  <Edit3 className="w-3.5 h-3.5" />
                                </button>
                              )}
                              <button
                                onClick={(e) => handleExportAgent(preset, e)}
                                title={t("导出 JSON", "Export JSON")}
                                className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[var(--c-bluecyan)] hover:bg-[var(--c-bluecyan-bg2)] transition-all"
                              >
                                <Download className="w-3.5 h-3.5" />
                              </button>
                              {!isBuiltin && (
                                <button
                                  onClick={(e) => handleDeleteCustomAgent(preset.id, e)}
                                  title={t("删除", "Delete")}
                                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[var(--c-cyan)] hover:bg-[var(--c-cyan-bg)] transition-all"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>

                            <div className={isBuiltin ? "pt-4" : ""}>
                              <div className="flex justify-between items-start gap-2">
                                <span className="text-xs font-bold text-[var(--c-text)] flex items-center gap-1.5 pr-14">
                                  <Sparkles className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-[var(--c-accent-lt)] animate-pulse" : "text-[var(--c-border2)] group-hover:text-[var(--c-accent)]"}`} />
                                  {getAgentName(preset)}
                                </span>
                              </div>
                              <p className="text-[10px] text-[var(--c-secondary)] mt-1.5 leading-relaxed line-clamp-2">
                                {getAgentDescription(preset)}
                              </p>
                            </div>

                            {isActive && (
                              <div className="absolute bottom-2 right-2 flex items-center gap-1 bg-[var(--c-accent)] text-white text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">
                                {t("当前激活", "ACTIVE")}
                              </div>
                            )}
                          </div>

                          {/* Inline edit panel */}
                          <AnimatePresence>
                            {isEditing && (
                              <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                                transition={{ duration: 0.25 }}
                                className="overflow-hidden mt-2 bg-[var(--c-white)] border border-[var(--c-border)] rounded-xl p-3"
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-[10px] text-[var(--c-muted)] font-bold uppercase tracking-wider flex items-center gap-1">
                                    <Edit3 className="w-3 h-3 text-[var(--c-accent)]" />
                                    {t("编辑人格 JSON", "Edit Personality JSON")}
                                  </span>
                                </div>
                                <textarea
                                  value={editingJson}
                                  onChange={(e) => setEditingJson(e.target.value)}
                                  rows={8}
                                  className="w-full p-2.5 bg-[var(--c-white)] border border-[var(--c-border)] rounded-lg text-[10px] font-mono text-[var(--c-text)] focus:outline-none focus:border-[var(--c-accent)] shadow-inner leading-normal resize-y"
                                />
                                <div className="flex justify-end gap-2 mt-2.5">
                                  <button
                                    onClick={handleCancelEdit}
                                    className="px-3 py-1.5 border border-[var(--c-border)] text-[var(--c-muted)] hover:text-[var(--c-secondary)] font-semibold text-[10px] rounded-lg transition-all active:scale-[0.97]"
                                  >
                                    {t("取消", "Cancel")}
                                  </button>
                                  <button
                                    onClick={handleSaveEdit}
                                    className="px-3.5 py-1.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-[10px] rounded-lg transition-all shadow-sm active:scale-[0.97] flex items-center gap-1"
                                  >
                                    <Check className="w-3 h-3" />
                                    {t("保存修改", "Save Changes")}
                                  </button>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      );
                    })}
                  </div>

                  {customAgents.length === 0 && (
                    <div className="mt-4 text-center py-6 bg-[var(--c-white)] rounded-xl border border-dashed border-[var(--c-border)]">
                      <Info className="w-6 h-6 text-[var(--c-border2)] mx-auto mb-2" />
                      <p className="text-[10px] text-[var(--c-muted)] leading-relaxed">
                        {t(
                          "暂无自定义人格。前往「引擎看板」通过 JSON Sandbox 导入您自己的心理人格设定。",
                          "No custom personalities yet. Go to the Dashboard to import your own personality via the JSON Sandbox."
                        )}
                      </p>
                    </div>
                  )}
                </div>

                {/* Footer tip */}
                <div className="px-4 py-2 border-t border-[var(--c-surface1)] bg-[var(--c-white)] flex items-center justify-between">
                  <p className="text-[9px] text-[var(--c-border2)] leading-relaxed">
                    {t(
                      "💡 拖动标题栏移动 · 点击卡片切换 · ESC 关闭",
                      "💡 Drag header to move · Click card to switch · ESC to close"
                    )}
                  </p>
                  <button
                    onClick={closeAgentList}
                    className="px-3 py-1 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-[9px] rounded-md transition-all shadow-sm active:scale-[0.97]"
                  >
                    {t("完成", "Done")}
                  </button>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ========== FIRST-RUN TUTORIAL MODAL (3 steps, skippable) ========== */}
      <AnimatePresence>
        {tutorialStep !== null && (
          <motion.div
            className="fixed inset-0 z-[80] flex items-center justify-center p-5 bg-[var(--c-text)]/45 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={dismissTutorial}
          >
            <motion.div
              role="dialog"
              aria-modal="true"
              onClick={(e) => e.stopPropagation()}
              initial={{ opacity: 0, scale: 0.94, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 8 }}
              transition={{ type: "spring", stiffness: 260, damping: 24 }}
              className="relative w-full max-w-sm bg-[var(--c-white)] rounded-3xl shadow-2xl shadow-black/25 border border-[var(--c-border)] overflow-hidden"
            >
              <button
                onClick={dismissTutorial}
                aria-label={t("关闭", "Close")}
                className="absolute top-3 right-3 p-1.5 rounded-full text-[var(--c-border2)] hover:text-[var(--c-secondary)] hover:bg-[var(--c-surface7)] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="px-6 pt-7 pb-6 text-center">
                <div className="mx-auto mb-4 w-14 h-14 rounded-2xl bg-gradient-to-br from-[var(--c-accent-lt)] via-[var(--c-accent-soft)] to-[var(--c-accent)] flex items-center justify-center shadow-md">
                  {tutorialStep === 1 && <Sparkles className="w-7 h-7 text-white" />}
                  {tutorialStep === 2 && <Send className="w-7 h-7 text-white" />}
                  {tutorialStep === 3 && <Users className="w-7 h-7 text-white" />}
                </div>

                {tutorialStep === 1 && (
                  <>
                    <h2 className="text-lg font-bold font-display text-[var(--c-text)] tracking-wide">
                      {t("欢迎来到 Your Mirror", "Welcome to Your Mirror")}
                    </h2>
                    <p className="mt-2 text-sm text-[var(--c-secondary)] leading-relaxed">
                      {t(
                        "这里住着一个会聊天的 AI 人格，它的心情、语气和想法会随着你们的对话慢慢变化，就像面对一个真实的人。",
                        "A living AI personality lives here. Its mood, tone, and thoughts evolve as you talk — like talking to a real person."
                      )}
                    </p>
                  </>
                )}
                {tutorialStep === 2 && (
                  <>
                    <h2 className="text-lg font-bold font-display text-[var(--c-text)] tracking-wide">
                      {t("直接从下面开始聊", "Just start typing below")}
                    </h2>
                    <p className="mt-2 text-sm text-[var(--c-secondary)] leading-relaxed">
                      {t(
                        "在页面底部的输入框打字发送，就能和它对话了。它可能会心情好、也可能闹脾气——观察它的变化，就是最好玩的体验。",
                        "Type in the box at the bottom and hit send. It may be cheerful or moody — watching it react is half the fun."
                      )}
                    </p>
                  </>
                )}
                {tutorialStep === 3 && (
                  <>
                    <h2 className="text-lg font-bold font-display text-[var(--c-text)] tracking-wide">
                      {t("换个性格再开始", "Swap to a different personality")}
                    </h2>
                    <p className="mt-2 text-sm text-[var(--c-secondary)] leading-relaxed">
                      {t(
                        "想让它是高敏感、自恋防御，还是别的风格？点底部导航里的「人格」，就能在智能体库里来回切换，或者导入你自己的设定。",
                        "Prefer it highly sensitive, defensive, or something else? Tap the 'Personality' tab in the bottom nav to switch agents, or import your own."
                      )}
                    </p>
                    <button
                      onClick={() => { openAgentList(); dismissTutorial(); }}
                      className="mt-4 w-full py-2.5 bg-gradient-to-r from-[var(--c-accent-lt)] to-[var(--c-accent)] hover:from-[var(--c-accent3)] hover:to-[var(--c-accent-st)] text-white font-bold text-xs rounded-xl active:scale-[0.98] transition-all shadow-sm flex items-center justify-center gap-2"
                    >
                      <Users className="w-3.5 h-3.5" />
                      {t("去选个人格", "Pick a personality")}
                    </button>
                  </>
                )}

                <div className="mt-5 flex items-center justify-center gap-1.5">
                  {[1, 2, 3].map((s) => (
                    <span
                      key={s}
                      className={`h-1.5 rounded-full transition-all ${tutorialStep === s ? "w-5 bg-[var(--c-accent)]" : "w-1.5 bg-[var(--c-surface17)]"}`}
                    />
                  ))}
                </div>

                <div className="mt-5 flex items-center justify-between gap-3">
                  <button
                    onClick={dismissTutorial}
                    className="text-[11px] font-semibold text-[var(--c-border2)] hover:text-[var(--c-secondary)] transition-colors"
                  >
                    {t("跳过教程", "Skip tutorial")}
                  </button>
                  {tutorialStep < 3 ? (
                    <button
                      onClick={() => setTutorialStep(tutorialStep + 1)}
                      className="px-5 py-2.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-xs rounded-xl active:scale-[0.98] transition-all shadow-sm flex items-center gap-1.5"
                    >
                      {t("下一步", "Next")}
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button
                      onClick={dismissTutorial}
                      className="px-5 py-2.5 bg-[var(--c-accent)] hover:bg-[var(--c-accent-st)] text-white font-bold text-xs rounded-xl active:scale-[0.98] transition-all shadow-sm"
                    >
                      {t("开始使用", "Get started")}
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
