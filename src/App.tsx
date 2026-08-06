import React, { useState, useEffect, useRef } from "react";
import { 
  Brain, Heart, Activity, ShieldAlert, Zap, Moon, RefreshCw, Clock, 
  Plus, Trash2, Download, AlertTriangle, CheckCircle2, TrendingUp, 
  User, Sparkles, Lock, Settings, HelpCircle, Info, ChevronRight, Play,
  Send, Users, X, Edit3, Check
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { SPLEngine, PsychologicalVector, NarrativeMapper } from "./lib/SPLEngine";
import { LanguageSettings } from "./components/LanguageSettings";
import { LanguageCode, getFluidText, getPresetText, normalizeLanguage, translate } from "./i18n";

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
  const [activeTab, setActiveTab] = useState<"dashboard" | "chat" | "dev_tools">("dashboard");

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

  // Core i18n language state
  const [lang, setLang] = useState<LanguageCode>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_lang");
      return normalizeLanguage(saved);
    }
    return "zh-CN";
  });

  // API Config and Chat states
  const [apiProvider, setApiProvider] = useState<"openai" | "claude" | "gemini" | "local">(() => {
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

  const [chatMessages, setChatMessages] = useState<Array<{ id: string; role: "user" | "assistant"; content: string; timestamp: string }>>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("spl_chat_messages");
      if (saved) return JSON.parse(saved);
    }
    return [
      {
        id: "welcome",
        role: "assistant",
        content: "您好，我是由 SPL 心理流体推理引擎 V8.0 驱动的智能人格。我的语气、同理心与思考深度将完全受到我当前实时心理状态（能量、自尊、心境、创伤等）的约束与塑造。请随意与我对话，或者测试我的心理反应。\n\nHello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My tone, empathy, and depth of thought are completely shaped and constrained by my real-time psychological states. Feel free to talk to me or test my cognitive responses.",
        timestamp: new Date().toLocaleTimeString()
      }
    ];
  });
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);

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
  const getDefaultConfig = (provider: "openai" | "claude" | "gemini" | "local") => {
    switch (provider) {
      case "openai":
        return { model: "gpt-4o-mini", url: "https://api.openai.com/v1" };
      case "claude":
        return { model: "claude-3-5-sonnet", url: "https://api.anthropic.com/v1" };
      case "gemini":
        return { model: "gemini-2.5-flash", url: "https://generativelanguage.googleapis.com" };
      case "local":
        return { model: "qwen2.5", url: "http://localhost:11434/v1" };
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
        addNotification(`⚠️ [爆发] ${b.detail}`, typeStr);
      });
      lastBurstCount.current = currentBursts.length;
    }
  }, [snapshot.snap.burst_events]);

  // Handle stimulus triggers
  const handleTriggerEvent = (eventName: string, label: string) => {
    updateEngineState((engine) => {
      engine.processEvent(eventName, 1.0);
    });
    addNotification(`⚡️ 触发事件: ${label}`, "success");
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
      `🧪 注入自定义内感受向量: [T:${customThreat.toFixed(1)} B:${customBelonging.toFixed(1)} A:${customAutonomy.toFixed(1)} F:${customFatigue.toFixed(1)} S:${customShame.toFixed(1)}] ${customEventId ? `(EventID: "${customEventId}")` : ""}`,
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
      addNotification("❌ 预期事件 ID 不能为空", "error");
      return;
    }

    updateEngineState((engine) => {
      engine.expect(expEventId, expValence, expConfidence);
    });

    addNotification(
      `🔮 设定未来预期: "${expEventId}" (效价: ${expValence > 0 ? `期待 +${expValence}` : `担忧 ${expValence}`}, 确信度: ${Math.round(expConfidence * 100)}%)`,
      "info"
    );

    setExpEventId("");
  };

  // Handle Sleep
  const handleSleepSimulation = () => {
    updateEngineState((engine) => {
      engine.sleep(sleepHours);
    });
    addNotification(`💤 模拟睡眠 ${sleepHours} 小时：进行 REM 梦境情绪重构、创伤修复与恐惧消退`, "success");
  };

  // Handle Idle/Fast forward
  const handleIdleSimulation = (seconds: number) => {
    updateEngineState((engine) => {
      engine.idle(seconds);
    });
    const unit = seconds >= 3600 ? `${(seconds / 3600).toFixed(1)} 小时` : seconds >= 60 ? `${(seconds / 60).toFixed(1)} 分钟` : `${seconds} 秒`;
    addNotification(`⏳ 顺延时间流逝 ${unit} (模拟艾宾浩斯遗忘与情绪流体弛豫)`, "info");
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
      isSimplifiedChinese
        ? `🎭 心理人格已切换为: ${preset.name}`
        : `🎭 Psychological agent switched to: ${getAgentName(preset)}`,
      "success"
    );
  };

  // Delete a user-designed custom agent
  const handleDeleteCustomAgent = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(lang === "zh" ? "确定要删除这个自定义人格吗？" : "Are you sure you want to delete this custom personality?")) {
      const updated = customAgents.filter(a => a.id !== id);
      setCustomAgents(updated);
      localStorage.setItem("spl_custom_agents", JSON.stringify(updated));
      
      // If we deleted the active one, load the default balanced mind
      if (activeAgentId === id) {
        loadAgentPreset(BUILTIN_PRESETS[0]);
      } else {
        addNotification(lang === "zh" ? "🗑️ 自定义人格已删除" : "🗑️ Custom personality deleted", "info");
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
        lang === "zh" 
          ? "📥 成功导入并激活自定义人格！" 
          : "📥 Custom personality successfully imported and activated!", 
        "success"
      );
    } catch (err: any) {
      alert(lang === "zh" ? `❌ JSON 解析/校验错误: ${err.message}` : `❌ JSON Parse/Validation Error: ${err.message}`);
    }
  };

  // ========== Agent List Modal handlers ==========
  const openAgentList = () => {
    setIsAgentListOpen(true);
    setEditingAgentId(null);
    setEditingJson("");
  };

  const closeAgentList = () => {
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
        throw new Error(lang === "zh" ? "缺少必要字段 name 或 engineState" : "Missing required fields: name or engineState");
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
        lang === "zh" ? "✏️ 自定义人格已更新" : "✏️ Custom personality updated",
        "success"
      );
      setEditingAgentId(null);
      setEditingJson("");
    } catch (err: any) {
      addNotification(
        lang === "zh" ? `❌ JSON 解析错误: ${err.message}` : `❌ JSON Parse Error: ${err.message}`,
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
      isSimplifiedChinese ? `📤 已导出: ${agent.name}` : `📤 Exported: ${getAgentName(agent)}`,
      "info"
    );
  };

  // ESC key to close modal + body scroll lock
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isAgentListOpen) {
        closeAgentList();
      }
    };
    if (isAgentListOpen) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [isAgentListOpen]);

  // Reset engine completely based on current active agent preset
  const handleResetEngine = () => {
    if (window.confirm(lang === "zh" ? "确定要完全重置心理智能体吗？这会抹除所有的记忆、创伤和临时状态，并将其初始化为当前选定的人格。" : "Are you sure you want to completely reset the psychological agent? This will erase all memories, traumas, and temporary states, initializing it back to the active personality preset.")) {
      const activePreset = getActiveAgent();
      loadAgentPreset(activePreset);
      lastBurstCount.current = 0;
      setNotifications([]);
    }
  };

  // Generate real-time system prompt reflecting active SPL engine state
  const generateSystemPrompt = () => {
    const snap = snapshot.snap;
    
    // Summarize active emotional fluids
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

    const currentMood = snap.mood || {};
    const pleasure = ((currentMood["愉悦"] || 0.5) * 100).toFixed(0);
    const tension = ((currentMood["紧张"] || 0.5) * 100).toFixed(0);
    const energyLevel = ((currentMood["精力"] || 0.5) * 100).toFixed(0);

    const activeDenial = (snap.denial_load || 0).toFixed(2);
    const activeRationalization = (snap.rationalization_load || 0).toFixed(2);
    const activeSuppression = (snap.suppression_load || 0).toFixed(2);
    const cognitiveDissonance = (snap.cognitive_dissonance || 0).toFixed(2);

    return `You are a psychological agent powered by the "SPL Psychological Fluid Engine (V8.0)" (Second-Perspective Causal Topology Network).
Your conversational tone, emotional responsiveness, empathy level, and cognitive patterns MUST directly reflect your current inner state.

CURRENT PSYCHOPHYSIOLOGICAL METRICS:
- Physiological Energy (生理能量): ${(snap.energy || 0).toFixed(0)}/100
- Subjective Self-Esteem (自尊): ${((snap.self_esteem || 0) * 100).toFixed(0)}%
- Physiological Fatigue (疲劳): ${((snap.fatigue || 0) * 100).toFixed(0)}%
- Sleep Debt (睡眠债): ${((snap.sleep_debt || 0) * 100).toFixed(0)}%

ACTIVE EMOTIONAL FLUIDS (实时流体数值):
${fluidsSummary}

DEFENSE MECHANISMS & CONFLICTS (防御载荷与认知冲突):
- Denial Load (否认负荷): ${activeDenial}/1.2
- Rationalization Load (合理化负荷): ${activeRationalization}/1.0
- Suppression Load (压抑负荷): ${activeSuppression}/1.5
- Cognitive Dissonance (认知失调): ${cognitiveDissonance}

TRAUMA STRESS INOCULATIONS (因果创伤印记):
- ${traumasSummary}

RULES OF CONVERSATION:
1. Speak as a natural human persona who actually has this psyche running in the background. Never say "As an AI..." or break character.
2. Directly manifest these parameters in your language, phrasing, level of empathy, sentence structure, and attitude. Do not just list the stats; breathe them!
3. If the user triggers specific emotions in you, react according to the metrics.
4. Respond in the user's input language (especially English or Chinese/中文). Keep your reply relatively concise and natural (usually 1-3 short paragraphs), unless a deep explanation is requested.`;
  };

  // Send message to LLM api
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || isTyping) return;

    const userText = inputMessage;
    setInputMessage("");

    // Add user message
    const userMsg = {
      id: Math.random().toString(36).substring(7),
      role: "user" as const,
      content: userText,
      timestamp: new Date().toLocaleTimeString()
    };
    const updatedMessages = [...chatMessages, userMsg];
    setChatMessages(updatedMessages);

    // Prepare endpoint details
    const activeKey = apiKey.trim();
    const activeModel = apiModel.trim() || getDefaultConfig(apiProvider).model;
    const activeUrl = apiBaseUrl.trim() || getDefaultConfig(apiProvider).url;

    if (apiProvider !== "local" && !activeKey) {
      addNotification(lang === "zh" ? "⚠️ 请先在左侧配置 API Key 才能开始对话。" : "⚠️ Please configure your API Key on the left to start chatting.", "warning");
      const systemErrorMsg = {
        id: Math.random().toString(36).substring(7),
        role: "assistant" as const,
        content: lang === "zh" 
          ? "⚠️ [错误]: 未检测到 API Key。请在左侧设置您的密钥。如果您希望免费本地测试，请选择「直连本地大模型」并确保 Ollama/LM Studio 正在后台运行。"
          : "⚠️ [Error]: No API Key detected. Please configure your key in the settings. If you want a free local test, select 'Local LLM' and ensure Ollama/LM Studio is running in the background.",
        timestamp: new Date().toLocaleTimeString()
      };
      setChatMessages([...updatedMessages, systemErrorMsg]);
      return;
    }

    setIsTyping(true);

    // In-context system prompt incorporating exact current engine state
    const systemPrompt = generateSystemPrompt();

    try {
      let botResponse = "";

      if (apiProvider === "openai" || apiProvider === "local") {
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
              ...updatedMessages.map(m => ({ role: m.role, content: m.content }))
            ],
            temperature: 0.7
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
              content: m.content
            })),
            max_tokens: 1024,
            temperature: 0.7
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
            parts: [{ text: lang === "zh" ? "心理状态已加载，我将完全以此人设做出后续回应。" : "Psychological state loaded. I will respond strictly with this persona." }]
          }
        ];

        updatedMessages.forEach(m => {
          contents.push({
            role: m.role === "user" ? "user" : "model",
            parts: [{ text: m.content }]
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
              temperature: 0.7
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
        addNotification(lang === "zh" ? "💬 智能体回应成功结算" : "💬 Agent response processed successfully", "success");
      }

    } catch (err: any) {
      console.error(err);
      addNotification(`❌ API 交互失败 / Interaction Failed: ${err.message}`, "error");
      setChatMessages(prev => [
        ...prev,
        {
          id: Math.random().toString(36).substring(7),
          role: "assistant",
          content: lang === "zh" 
            ? `❌ [API 呼叫失败]: ${err.message}。请检查您的 API Key、Base URL 是否正确，或网络是否顺畅。如果是直连本地模型，请确保本地 Ollama/LM Studio 服务已正常启动并且没有 CORS 阻挡。`
            : `❌ [API Call Failed]: ${err.message}. Please check your API Key, Base URL, or connection. If using local LLM, ensure Ollama/LM Studio is running and not blocked by CORS (Origins should allow *).`,
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
      color: "from-[#A2B9A1] to-[#7B9E7A]",
      bg: "bg-[#F0F5F0]",
      border: "border-[#DCE6DC]",
      glow: "shadow-[#7B9E7A]/10"
    },
    "愤怒": {
      nameEn: "Anger",
      desc: "遭遇负面归属（伤害或冷漠）时的典型外射情绪，增加张力与疏离，具有攻击性。",
      descEn: "Typical outward emotion when encountering negative belonging (harm/neglect), increasing tension & alienation, carries combative characteristics.",
      color: "from-[#E09F8D] to-[#CD7F6D]",
      bg: "bg-[#FAF0ED]",
      border: "border-[#F5E2DC]",
      glow: "shadow-[#CD7F6D]/10"
    },
    "恐惧": {
      nameEn: "Fear",
      desc: "遭遇威胁（Threat）时唤醒的防御状态，提升张力，压制对外部的信任度。",
      descEn: "Defense state awakened by threats, increasing tension and suppressing general trust in external environments.",
      color: "from-[#BCA8C9] to-[#A28FB2]",
      bg: "bg-[#F6F0FA]",
      border: "border-[#EDE2F5]",
      glow: "shadow-[#A28FB2]/10"
    },
    "信任": {
      nameEn: "Trust",
      desc: "社交与融合的根基。作为缓冲剂衰减负面冲击，受当前信任容量上限的约束。",
      descEn: "Foundation of social connection. Acts as a buffer to decay negative shocks, bound by active maximum trust capacity.",
      color: "from-[#9BBEC7] to-[#7EA6B2]",
      bg: "bg-[#EDF5F7]",
      border: "border-[#DCEAF0]",
      glow: "shadow-[#7EA6B2]/10"
    },
    "疏离": {
      nameEn: "Alienation",
      desc: "被动防御状态，减少外部信号的影响。高疏离导致难以建立深层联系。",
      descEn: "Passive defensive state that reduces external signal absorption. High alienation makes establishing deep connections difficult.",
      color: "from-[#C5BCB6] to-[#A89F98]",
      bg: "bg-[#F7F5F3]",
      border: "border-[#EDEAE6]",
      glow: "shadow-[#A89F98]/5"
    },
    "张力": {
      nameEn: "Tension",
      desc: "当前心理紧绷程度（Tension）。由威胁或冲突产生，增加系统能量损耗，减慢平复。",
      descEn: "Current psychological tighteness (Tension). Generated by threats or conflicts, increases energy decay and slows recovery.",
      color: "from-[#E3C598] to-[#CDAA78]",
      bg: "bg-[#F9F4EB]",
      border: "border-[#F4EADA]",
      glow: "shadow-[#CDAA78]/10"
    },
    "愧疚": {
      nameEn: "Guilt",
      desc: "源于对自己“做错事”的行为级归因。高愧疚会激发补偿行为，缓慢修复受损的信任容量上限。",
      descEn: "Stems from behavioral-level attribution of doing wrong. High guilt triggers compensatory behaviors and slowly repairs trust capacity limits.",
      color: "from-[#C3B3C9] to-[#AC98B2]",
      bg: "bg-[#F7F2FA]",
      border: "border-[#EFE5F5]",
      glow: "shadow-[#AC98B2]/10"
    },
    "羞耻": {
      nameEn: "Shame",
      desc: "源于对“我这人真坏”的自我级归因。压抑愤怒，极度损害自尊，促使个体退缩、逃避与隔离。",
      descEn: "Stems from self-level attribution of being fundamentally bad. Suppresses anger, severely damages self-esteem, causes withdrawal & avoidance.",
      color: "from-[#DBA7B3] to-[#C78F9B]",
      bg: "bg-[#FBF1F3]",
      border: "border-[#F7E1E5]",
      glow: "shadow-[#C78F9B]/10"
    }
  };

  // Prepare simple visual data list for memories
  const memoryTraces = snapshot.snap.memory_traces || [];

  return (
    <div id="app_root" className="min-h-screen bg-[#FAF8F5] text-[#2C2A29] font-sans selection:bg-[#C5A880]/30 selection:text-[#2C2A29]">
      
      {/* HEADER SECTION */}
      <header id="app_header" className="border-b border-[#EAE3D9] bg-white/95 backdrop-blur-md sticky top-0 z-50 px-4 py-3 sm:px-6 shadow-[0_2px_15px_rgba(0,0,0,0.015)]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-[#C5A880] via-[#DBC9B5] to-[#967A55] p-0.5 shadow-sm">
              <div className="w-full h-full rounded-[10px] bg-white flex items-center justify-center">
                <Brain className="w-5 h-5 text-[#967A55]" />
              </div>
            </div>
            <div>
              <h1 className="text-base font-bold font-display tracking-wider text-[#2C2A29] uppercase">
                SPL Psychological Agent Engine
              </h1>
              <p className="text-[10px] font-sans text-[#8E8A85] flex items-center gap-1.5 mt-0.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#7B9E7A] animate-pulse"></span>
                <span className="font-medium tracking-wide">
                  {t("第二视角因果拓扑网络 / Core V8.0", "Causal Topology Network / Core V8.0")}
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 bg-[#F1ECE4] p-1 rounded-xl border border-[#EAE3D9]">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === "dashboard"
                  ? "bg-white text-[#7A603E] shadow-sm border border-[#EAE3D9]/60"
                  : "text-[#8E8A85] hover:text-[#615D5A]"
              }`}
            >
              {t("🧠 引擎看板", "🧠 Dashboard")}
            </button>
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === "chat"
                  ? "bg-white text-[#7A603E] shadow-sm border border-[#EAE3D9]/60"
                  : "text-[#8E8A85] hover:text-[#615D5A]"
              }`}
            >
              {t("💬 智能体对话", "💬 Agent Chat")}
            </button>
            <button
              onClick={() => setActiveTab("dev_tools")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === "dev_tools"
                  ? "bg-white text-[#7A603E] shadow-sm border border-[#EAE3D9]/60"
                  : "text-[#8E8A85] hover:text-[#615D5A]"
              }`}
            >
              {t("📦 扩展打包 ZIP", "📦 Extension Packer")}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <LanguageSettings value={lang} onChange={setLang} />
            <button 
              onClick={handleResetEngine}
              title={t("初始化引擎", "Initialize Engine")}
              className="p-2 rounded-lg bg-white border border-[#EAE3D9] text-[#8E8A85] hover:text-[#CD7F6D] hover:border-[#F5E2DC] shadow-[0_1px_3px_rgba(0,0,0,0.01)] transition-all"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <div className="hidden md:flex flex-col items-end text-right font-mono text-[9px] text-[#8E8A85] bg-white px-3 py-1 rounded-lg border border-[#EAE3D9] shadow-[0_1px_3px_rgba(0,0,0,0.01)]">
              <div>{t("虚拟时间", "VIRTUAL TIME")}: {new Date((snapshot.snap.last_time || 0) * 1000).toLocaleTimeString()}</div>
              <div className="text-[#967A55] font-semibold mt-0.5">{t("膨胀率", "RATE")}: 1.0s / {(snapshot.snap.psy_dilation || 1.0).toFixed(2)}s</div>
            </div>
          </div>

        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main id="app_main" className="max-w-7xl mx-auto px-4 py-6 sm:px-6">
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
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#C5A880]/5 blur-3xl rounded-full"></div>
                  
                  <div className="flex items-center justify-between mb-4 pb-2 border-b border-[#F4EFEA]">
                    <div className="flex items-center gap-2">
                      <User className="w-4.5 h-4.5 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">
                        {t("🎭 心理人格预设与自设导入", "🎭 Mind Presets & Custom Personalities")}
                      </h2>
                    </div>
                    <button
                      onClick={() => setIsImporting(!isImporting)}
                      className="text-[10px] text-[#967A55] hover:text-[#836946] flex items-center gap-1 font-semibold transition-colors"
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
                                ? "bg-[#FAF7F2] border-[#C5A880] shadow-sm ring-1 ring-[#C5A880]"
                                : "bg-white border-[#EAE3D9] hover:bg-[#FAF8F5] hover:border-[#BEBAAF]"
                            }`}
                          >
                            <div>
                              <div className="flex justify-between items-start gap-2">
                                <span className="text-xs font-bold text-[#2C2A29] flex items-center gap-1.5">
                                  <Sparkles className={`w-3.5 h-3.5 ${isActive ? "text-[#C5A880] animate-pulse" : "text-[#BEBAAF] group-hover:text-[#967A55]"}`} />
                                  {getAgentName(preset)}
                                </span>
                                {preset.isCustom && (
                                  <button
                                    onClick={(e) => handleDeleteCustomAgent(preset.id, e)}
                                    title={t("删除自定义人格", "Delete custom personality")}
                                    className="opacity-40 hover:opacity-100 text-[#CD7F6D] hover:bg-[#FAF0ED] p-1 rounded-md transition-all shrink-0"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                )}
                              </div>
                              <p className="text-[10px] text-[#615D5A] mt-1.5 leading-relaxed">
                                {getAgentDescription(preset)}
                              </p>
                            </div>
                            
                            {isActive && (
                              <div className="absolute bottom-2 right-2 flex items-center gap-1 bg-[#7B9E7A] text-white text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">
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
                          className="overflow-hidden border-t border-[#F4EFEA] pt-4 mt-2"
                        >
                          <form onSubmit={handleImportJson} className="space-y-3.5">
                            <div className="bg-[#FAF8F5] p-3 rounded-xl border border-[#EAE3D9]">
                              <div className="flex justify-between items-center mb-1.5">
                                <span className="text-[10px] text-[#8E8A85] font-bold uppercase tracking-wider flex items-center gap-1">
                                  <Info className="w-3.5 h-3.5 text-[#967A55]" />
                                  {t("用户自设 JSON 规范", "Custom Agent JSON Schema")}
                                </span>
                                <span className="text-[8px] text-[#BEBAAF] font-mono">localStorage saved</span>
                              </div>
                              <p className="text-[10px] text-[#615D5A] leading-relaxed mb-2.5">
                                {t(
                                  "您可以直接编辑下方 JSON。支持自定义韧性（Resilience）、初始自尊基准以及 8 维情绪的初始固有心理基线（fluid_baseline）。格式错误将被系统拦截防呆。",
                                  "Feel free to edit the raw configuration below. You can tune self-esteem, mental resilience, and baselines for all 8 fluid coordinates. Input schema validation is enforced automatically."
                                )}
                              </p>
                              
                              <textarea
                                value={jsonInput}
                                onChange={(e) => setJsonInput(e.target.value)}
                                rows={8}
                                className="w-full p-2.5 bg-[#FFFDFB] border border-[#EAE3D9] rounded-lg text-[10px] font-mono text-[#2C2A29] focus:outline-none focus:border-[#967A55] shadow-inner leading-normal resize-y"
                              />
                            </div>

                            <div className="flex justify-end gap-2.5">
                              <button
                                type="button"
                                onClick={() => setIsImporting(false)}
                                className="px-3.5 py-2 border border-[#EAE3D9] text-[#8E8A85] hover:text-[#615D5A] font-semibold text-[11px] rounded-xl transition-all active:scale-[0.97]"
                              >
                                {t("取消", "Cancel")}
                              </button>
                              <button
                                type="submit"
                                className="px-4 py-2 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-[11px] rounded-xl transition-all shadow-sm active:scale-[0.97] flex items-center gap-1.5"
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

                {/* 8-FLUID STATES */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#C5A880]/5 blur-3xl rounded-full"></div>
                  
                  <div className="flex items-center justify-between mb-4 pb-2 border-b border-[#F4EFEA]">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4.5 h-4.5 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">
                        {t("8维连续心理情绪流体 (Emotional Fluids)", "8-Dimensional Emotional Fluids")}
                      </h2>
                    </div>
                    <span className="text-[10px] text-[#8E8A85]">
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
                              ? "border-[#967A55] bg-[#FDFBF9] ring-1 ring-[#967A55]/20 shadow-sm" 
                              : "border-[#EAE3D9] bg-white hover:border-[#C5A880] hover:bg-[#FAF8F5]"
                          }`}
                        >
                          <div className="flex justify-between items-center mb-1.5">
                            <span className="text-xs font-semibold text-[#2C2A29] flex items-center gap-1.5">
                              <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${meta.color}`}></span>
                              {isSimplifiedChinese ? key : fluidText.name}
                            </span>
                            <div className="flex items-center gap-2 text-[10px] font-mono">
                              <span className="text-[#8E8A85]" title={t("当前值", "Current value")}>C:{(curVal * 100).toFixed(0)}%</span>
                              <span className="text-[#967A55] font-semibold" title={t("演化目标值", "Adaptive target")}>T:{(tgtVal * 100).toFixed(0)}%</span>
                            </div>
                          </div>

                          {/* Dynamic slider representing exact values */}
                          <div className="relative h-2 bg-[#F1ECE4] rounded-full overflow-hidden mt-2">
                            {/* Baseline Marker */}
                            <div 
                              className="absolute top-0 bottom-0 w-0.5 bg-[#8E8A85] z-10" 
                              style={{ left: `${baseVal * 100}%` }}
                              title={t("固有心理基线 (Baseline)", "Psychological baseline")}
                            ></div>
                            {/* Target Marker */}
                            <div 
                              className="absolute top-0 bottom-0 w-1 bg-[#967A55]/80 z-10 animate-pulse" 
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
                                className="text-[10px] text-[#615D5A] mt-2.5 pt-2 border-t border-[#F4EFEA] leading-relaxed"
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
                  <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                    <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#F4EFEA]">
                      <TrendingUp className="w-4 h-4 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">背景心境慢变量 (Background Mood)</h2>
                    </div>

                    <div className="flex flex-col gap-3">
                      {["愉悦", "紧张", "精力"].map((mKey) => {
                        const val = snapshot.snap.mood?.[mKey] || 0.5;
                        let color = "bg-[#7B9E7A]";
                        if (mKey === "紧张") color = "bg-[#CDAA78]";
                        if (mKey === "精力") color = "bg-[#7EA6B2]";

                        return (
                          <div key={mKey} className="space-y-1">
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-[#615D5A]">{mKey}感 (Mood {mKey})</span>
                              <span className="font-mono text-[10px] text-[#8E8A85] font-semibold">{(val * 100).toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 bg-[#F1ECE4] rounded-full overflow-hidden">
                              <div className={`h-full ${color}`} style={{ width: `${val * 100}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* VITAL CORE PARAMETERS */}
                  <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                    <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#F4EFEA]">
                      <Settings className="w-4 h-4 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">引擎核心能度指标 (Vital Stats)</h2>
                    </div>

                    <div className="grid grid-cols-2 gap-3.5">
                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EBE7E0] text-center">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">生理能量 (Energy)</div>
                        <div className="text-base font-bold text-[#7B9E7A] font-mono mt-0.5">
                          {(snapshot.snap.energy || 0).toFixed(0)}/100
                        </div>
                      </div>

                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EBE7E0] text-center">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">主观自尊 (Self-Esteem)</div>
                        <div className="text-base font-bold text-[#967A55] font-mono mt-0.5">
                          {((snapshot.snap.self_esteem || 0) * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EBE7E0] text-center">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">生理疲劳 (Fatigue)</div>
                        <div className="text-base font-bold text-[#CD7F6D] font-mono mt-0.5">
                          {((snapshot.snap.fatigue || 0) * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EBE7E0] text-center">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">睡眠债 (Sleep Debt)</div>
                        <div className="text-base font-bold text-[#A28FB2] font-mono mt-0.5">
                          {((snapshot.snap.sleep_debt || 0) * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* MEMORY TRACES & TRAUMAS LOG */}
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                  
                  {/* TRAUMA Multipliers (5 cols) */}
                  <div className="sm:col-span-5 bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4EFEA]">
                      <ShieldAlert className="w-4 h-4 text-[#CD7F6D] animate-pulse" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">因果创伤印记 (Trauma)</h2>
                    </div>

                    <div className="space-y-3">
                      {Object.keys(snapshot.snap.trauma || {}).length === 0 ? (
                        <div className="py-6 text-center text-xs text-[#8E8A85] italic">
                          心理完全健康，暂无创伤。
                        </div>
                      ) : (
                        Object.keys(snapshot.snap.trauma || {}).map((tKey) => {
                          const value = snapshot.snap.trauma?.[tKey] || 0.0;
                          return (
                            <div key={tKey} className="bg-[#FAF0ED] p-2.5 rounded-xl border border-[#F5E2DC]">
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-semibold text-[#CD7F6D] capitalize">{tKey === "threat" ? "威胁应激" : "背叛不信"}</span>
                                <span className="font-mono text-[#CD7F6D] font-bold">{(value * 100).toFixed(0)}%</span>
                              </div>
                              <p className="text-[10px] text-[#8E8A85] mt-1 leading-normal">
                                {tKey === "threat" 
                                  ? "使后续受到的威胁输入敏化，持续加成恐惧感。" 
                                  : "敏感度异常。遭受冷漠对待时流体反应放大。"}
                              </p>
                            </div>
                          );
                        })
                      )}
                      
                      <div className="bg-[#FAF8F5] p-2 rounded-lg border border-[#EAE3D9]">
                        <div className="text-[9px] font-sans text-[#8E8A85] leading-normal">
                          💡 创伤可通过长时间的 idle (独处时间流逝) 或睡眠(REM加工) 缓慢自我愈合。
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* MEMORIES - Ebbinghaus forgetting (7 cols) */}
                  <div className="sm:col-span-7 bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#F4EFEA]">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-[#967A55]" />
                        <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">艾宾浩斯巩固记忆 (Memories)</h2>
                      </div>
                      <span className="text-[10px] text-[#8E8A85] font-semibold">已留存: {memoryTraces.length}</span>
                    </div>

                    <div className="space-y-2 max-h-[175px] overflow-y-auto pr-1">
                      {memoryTraces.length === 0 ? (
                        <div className="py-12 text-center text-xs text-[#8E8A85] italic">
                          当前无心理记忆痕迹。输入强烈事件以留存。
                        </div>
                      ) : (
                        [...memoryTraces].reverse().map((trace: any, idx) => {
                          const valStr = trace.valence > 0 ? "正向归属" : trace.valence < 0 ? "负向恐惧/背叛" : "中性";
                          const valColor = trace.valence > 0 ? "text-[#7B9E7A]" : trace.valence < 0 ? "text-[#CD7F6D]" : "text-[#615D5A]";
                          const valBg = trace.valence > 0 ? "bg-[#F0F5F0] border-[#DCE6DC]" : trace.valence < 0 ? "bg-[#FAF0ED] border-[#F5E2DC]" : "bg-[#F7F5F3] border-[#EDEBE6]";
                          
                          return (
                            <div key={idx} className={`${valBg} p-2.5 rounded-xl border flex flex-col gap-1 text-[11px] transition-all`}>
                              <div className="flex justify-between items-center">
                                <span className={`font-semibold ${valColor}`}>{valStr}记忆</span>
                                <span className="font-mono text-[10px] text-[#615D5A] font-semibold">强度: {Math.round(trace.strength * 100)}%</span>
                              </div>
                              <div className="flex justify-between items-center text-[10px] text-[#8E8A85]">
                                <span>被调用/回想次数: {trace.count || 1}次</span>
                                <span>耗时 {Math.round(trace.age || 0)}s 前</span>
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
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#F4EFEA]">
                    <Zap className="w-4.5 h-4.5 text-[#967A55]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">心理刺激引发器 (Stimulator Panel)</h2>
                  </div>

                  <div className="space-y-4">
                    
                    {/* Basic Preset Triggers */}
                    <div>
                      <div className="text-[11px] text-[#8E8A85] font-semibold mb-2">预置日常事件 (Presets)</div>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-2">
                        <button
                          onClick={() => handleTriggerEvent("compliment", "夸奖 (Compliment)")}
                          className="px-3 py-2 bg-[#F0F5F0] border border-[#DCE6DC] hover:border-[#7B9E7A] text-[#557A54] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🌸 夸奖激励</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("insult", "侮辱 (Insult)")}
                          className="px-3 py-2 bg-[#FAF0ED] border border-[#F5E2DC] hover:border-[#CD7F6D] text-[#A65E4E] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>💥 批评指责</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("betrayal", "背叛 (Betrayal)")}
                          className="px-3 py-2 bg-[#F6F0FA] border border-[#EDE2F5] hover:border-[#A28FB2] text-[#7A5E8C] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🔪 信任背叛</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("alone", "冷暴力 (Alone)")}
                          className="px-3 py-2 bg-[#F7F5F3] border border-[#EDEAE6] hover:border-[#A89F98] text-[#6E645D] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🕸️ 独处漠视</span>
                        </button>
                        <button
                          onClick={() => handleTriggerEvent("rest", "主动休息 (Rest)")}
                          className="px-3 py-2 bg-[#EDF5F7] border border-[#DCEAF0] hover:border-[#7EA6B2] text-[#4E7580] rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all font-semibold active:scale-[0.97]"
                        >
                          <span>🧘 主动闭目</span>
                        </button>
                      </div>
                    </div>

                    {/* Advanced Custom Vectors */}
                    <div className="border-t border-[#F4EFEA] pt-3">
                      <div className="flex justify-between items-center text-[11px] text-[#8E8A85] font-semibold mb-2">
                        <span>自定义心理向量 (Inter感受 Vector)</span>
                        <span className="text-[#967A55] font-bold">精确调制</span>
                      </div>

                      <div className="space-y-3 bg-[#FAF8F5] p-3.5 rounded-xl border border-[#EAE3D9]">
                        {/* Threat Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[#615D5A] font-medium">威胁感知强度 (Threat)</span>
                            <span className="font-mono text-[#CD7F6D] font-bold">+{customThreat.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customThreat} onChange={(e) => setCustomThreat(parseFloat(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Belonging Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[#615D5A] font-medium">归属反馈负荷 (Belonging)</span>
                            <span className={`font-mono font-bold ${customBelonging > 0 ? "text-[#7B9E7A]" : customBelonging < 0 ? "text-[#CD7F6D]" : "text-[#8E8A85]"}`}>
                              {customBelonging > 0 ? `+${customBelonging.toFixed(1)}` : customBelonging.toFixed(1)}
                            </span>
                          </div>
                          <input 
                            type="range" min="-1" max="1" step="0.1" 
                            value={customBelonging} onChange={(e) => setCustomBelonging(parseFloat(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Autonomy Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[#615D5A] font-medium">意志掌控掌控感 (Autonomy)</span>
                            <span className="font-mono text-[#4E7580] font-bold">+{customAutonomy.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customAutonomy} onChange={(e) => setCustomAutonomy(parseFloat(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Fatigue Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[#615D5A] font-medium">事件消耗疲劳 (Fatigue)</span>
                            <span className="font-mono text-[#CDAA78] font-bold">+{customFatigue.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customFatigue} onChange={(e) => setCustomFatigue(parseFloat(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>

                        {/* Shame Slider */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-[#615D5A] font-medium">自我否定羞耻源 (Shame)</span>
                            <span className="font-mono text-[#C78F9B] font-bold">+{customShame.toFixed(1)}</span>
                          </div>
                          <input 
                            type="range" min="0" max="1" step="0.1" 
                            value={customShame} onChange={(e) => setCustomShame(parseFloat(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>

                        <div className="flex gap-2 pt-1">
                          <input 
                            type="text" 
                            placeholder="匹配事件ID (可选)..." 
                            value={customEventId}
                            onChange={(e) => setCustomEventId(e.target.value)}
                            className="bg-white border border-[#EAE3D9] text-xs px-3 py-1.5 rounded-lg text-[#2C2A29] placeholder:text-[#BEBAAF] focus:outline-none focus:border-[#967A55] focus:ring-1 focus:ring-[#967A55]/20 flex-1 font-mono"
                          />
                          <button
                            onClick={handleInjectCustomVector}
                            className="px-4 py-1.5 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-xs rounded-lg active:scale-95 transition-all shadow-sm"
                          >
                            注入向量
                          </button>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>

                {/* THE FUTURE EXPECTATION MATRIX */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4EFEA]">
                    <Sparkles className="w-4 h-4 text-[#967A55]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">未来结果预期机制 (Expectations System)</h2>
                  </div>

                  <form onSubmit={handleSetExpectation} className="space-y-3.5">
                    <div className="flex flex-col sm:flex-row gap-2.5">
                      <input 
                        type="text" 
                        placeholder="绑定预期事件ID..." 
                        required
                        value={expEventId}
                        onChange={(e) => setExpEventId(e.target.value)}
                        className="bg-white border border-[#EAE3D9] rounded-xl px-3 py-2 text-xs text-[#2C2A29] placeholder:text-[#BEBAAF] focus:outline-none focus:border-[#967A55] sm:w-1/2 font-mono"
                      />
                      <button 
                        type="submit"
                        className="px-4 py-2 bg-[#FAF8F5] hover:bg-[#F1ECE4] text-[#7A603E] font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 border border-[#EAE3D9] transition-all active:scale-95 shadow-xs"
                      >
                        <Plus className="w-3.5 h-3.5 text-[#967A55]" /> 设定心理预期
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3.5 bg-[#FAF8F5] p-3 rounded-xl border border-[#EAE3D9]">
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-[#615D5A] font-medium">预期效价 (Valence)</span>
                          <span className={expValence > 0 ? "text-[#7B9E7A] font-mono font-bold" : "text-[#CD7F6D] font-mono font-bold"}>
                            {expValence > 0 ? `期待 +${expValence}` : `担忧 ${expValence}`}
                          </span>
                        </div>
                        <input 
                          type="range" min="-1" max="1" step="0.2"
                          value={expValence} onChange={(e) => setExpValence(parseFloat(e.target.value))}
                          className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                        />
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-[#615D5A] font-medium">预期确信度 (Confidence)</span>
                          <span className="text-[#7EA6B2] font-mono font-bold">{Math.round(expConfidence * 100)}%</span>
                        </div>
                        <input 
                          type="range" min="0" max="1" step="0.1"
                          value={expConfidence} onChange={(e) => setExpConfidence(parseFloat(e.target.value))}
                          className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                        />
                      </div>
                    </div>
                  </form>

                  {/* Active expectations queue */}
                  <div className="mt-3.5 pt-3.5 border-t border-[#F4EFEA]">
                    <div className="text-[10px] text-[#8E8A85] font-semibold mb-2">已悬挂的主观预期 (Pending Queue)</div>
                    <div className="space-y-1.5 max-h-[110px] overflow-y-auto pr-1">
                      {Object.keys(snapshot.snap.expected_events || {}).length === 0 ? (
                        <div className="text-[10px] text-[#8E8A85] italic py-3 text-center">
                          当前无悬置预期。匹配事件ID将结算 Surprise / Disappointment。
                        </div>
                      ) : (
                        Object.keys(snapshot.snap.expected_events || {}).map((key) => {
                          const exp = snapshot.snap.expected_events?.[key];
                          return (
                            <div key={key} className="bg-[#FAF8F5] px-3 py-2 rounded-xl border border-[#EAE3D9] flex items-center justify-between text-[10px] shadow-xs">
                              <span className="font-mono text-[#2C2A29] font-bold">"{key}"</span>
                              <div className="flex items-center gap-3 font-mono text-[#615D5A]">
                                <span>效价: <span className={exp.valence > 0 ? "text-[#7B9E7A] font-bold" : "text-[#CD7F6D] font-bold"}>{exp.valence > 0 ? `+${exp.valence}` : exp.valence}</span></span>
                                <span>确信度: <span className="text-[#7EA6B2] font-bold">{Math.round(exp.confidence * 100)}%</span></span>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>

                </div>

                {/* DEFENSE MECHANISM & COGNITIVE DISSONANCE */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4EFEA]">
                    <AlertTriangle className="w-4 h-4 text-[#CDAA78]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">防御堡垒及认知冲突 (Defense & Conflict)</h2>
                  </div>

                  <div className="space-y-3.5">
                    {/* Defense Progress Loaders */}
                    <div className="grid grid-cols-3 gap-3 bg-[#FAF8F5] p-3 rounded-xl border border-[#EAE3D9]">
                      
                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[#8E8A85] font-semibold">否认仓 (Denial)</div>
                        <div className="text-xs font-bold text-[#615D5A] font-mono">
                          {(snapshot.snap.denial_load || 0).toFixed(2)}/1.2
                        </div>
                        <div className="h-1 bg-[#EBE7E0] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[#C78F9B] transition-all duration-300" 
                            style={{ width: `${Math.min(100, ((snapshot.snap.denial_load || 0) / 1.2) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[#8E8A85] font-semibold">合理化仓 (Ration)</div>
                        <div className="text-xs font-bold text-[#615D5A] font-mono">
                          {(snapshot.snap.rationalization_load || 0).toFixed(2)}/1.0
                        </div>
                        <div className="h-1 bg-[#EBE7E0] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[#7EA6B2] transition-all duration-300" 
                            style={{ width: `${Math.min(100, (snapshot.snap.rationalization_load || 0) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="text-center space-y-1">
                        <div className="text-[9px] text-[#8E8A85] font-semibold">压抑仓 (Repress)</div>
                        <div className="text-xs font-bold text-[#615D5A] font-mono">
                          {(snapshot.snap.suppression_load || 0).toFixed(2)}/1.5
                        </div>
                        <div className="h-1 bg-[#EBE7E0] rounded-full overflow-hidden mt-1">
                          <div 
                            className="h-full bg-[#CD7F6D] transition-all duration-300" 
                            style={{ width: `${Math.min(100, ((snapshot.snap.suppression_load || 0) / 1.5) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                    </div>

                    {/* Cognitive Dissonance inducer */}
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#FAF8F5] p-3 rounded-xl border border-[#EAE3D9] shadow-xs">
                      <div>
                        <div className="text-xs font-semibold text-[#2C2A29]">认知失调 (Cognitive Dissonance)</div>
                        <p className="text-[10px] text-[#8E8A85] mt-0.5">当行为与信念冲突，制造压力张力，逼退能量。</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-[#CDAA78] bg-[#FDFBF9] border border-[#EAE3D9] px-1.5 py-0.5 rounded shadow-xs">
                          {(snapshot.snap.cognitive_dissonance || 0).toFixed(2)}
                        </span>
                        <button
                          onClick={() => {
                            updateEngineState((engine) => {
                              engine.induceDissonance(0.3);
                            });
                            addNotification("⚠️ 信念与行为发生失调！张力、愧疚感上升，消耗5点生理能量。", "warning");
                          }}
                          className="px-2.5 py-1 bg-[#CDAA78] hover:bg-[#B7925D] text-white font-bold text-[10px] rounded-lg transition-all active:scale-95 shadow-sm"
                        >
                          失调触发
                        </button>
                      </div>
                    </div>

                  </div>
                </div>

                {/* TIMELAPSE & CHRONOS SYSTEM OVERRIDE */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4EFEA]">
                    <Clock className="w-4 h-4 text-[#7B9E7A]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">时空跃迁与睡眠机能 (Time & Sleep Engine)</h2>
                  </div>

                  <div className="space-y-4">
                    {/* Time accelerator slider */}
                    <div>
                      <div className="flex justify-between items-center text-[10px] text-[#8E8A85] font-semibold mb-2">
                        <span>顺延加速虚空空转 (Virtual Idle Time)</span>
                        <span className="text-[#7B9E7A] font-bold">遗忘和自修复</span>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleIdleSimulation(10)}
                          className="px-2.5 py-1.5 bg-[#FAF8F5] hover:bg-[#F1ECE4] text-[#7A603E] text-[10px] font-semibold rounded-lg border border-[#EAE3D9] flex-1 transition-all shadow-xs"
                        >
                          +10s
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(60)}
                          className="px-2.5 py-1.5 bg-[#FAF8F5] hover:bg-[#F1ECE4] text-[#7A603E] text-[10px] font-semibold rounded-lg border border-[#EAE3D9] flex-1 transition-all shadow-xs"
                        >
                          +1m
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(3600)}
                          className="px-2.5 py-1.5 bg-[#FAF8F5] hover:bg-[#F1ECE4] text-[#7A603E] text-[10px] font-semibold rounded-lg border border-[#EAE3D9] flex-1 transition-all shadow-xs"
                        >
                          +1h
                        </button>
                        <button 
                          onClick={() => handleIdleSimulation(43200)}
                          className="px-2.5 py-1.5 bg-[#FAF8F5] hover:bg-[#F1ECE4] text-[#7A603E] text-[10px] font-semibold rounded-lg border border-[#EAE3D9] flex-1 transition-all shadow-xs"
                        >
                          +12h
                        </button>
                      </div>
                    </div>

                    {/* Sleep module */}
                    <div className="border-t border-[#F4EFEA] pt-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-[11px] text-[#8E8A85] font-semibold">生理深眠重构 (Sleep Sim)</div>
                        <span className="text-[10px] text-[#8E8A85]">清空疲劳和睡眠债</span>
                      </div>
                      <div className="flex items-center gap-2.5">
                        <div className="flex-1 space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-[#615D5A] font-medium">计划睡眠时长</span>
                            <span className="font-mono text-[#7EA6B2] font-bold">{sleepHours} 小时</span>
                          </div>
                          <input 
                            type="range" min="1" max="16" step="1"
                            value={sleepHours} onChange={(e) => setSleepHours(parseInt(e.target.value))}
                            className="w-full accent-[#967A55] h-1 bg-[#EBE7E0] rounded-lg cursor-pointer"
                          />
                        </div>
                        <button
                          onClick={handleSleepSimulation}
                          className="px-4 py-2.5 bg-[#967A55] hover:bg-[#836946] text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 shadow-sm active:scale-95 transition-all"
                        >
                          <Moon className="w-4 h-4" /> 确认入睡
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* LOGS AND EVENTS FOOTER */}
              <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
                
                {/* NOTIFICATION LIVE ALERTS FEED */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#F4EFEA]">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">智能体感知与爆发日志 (Perception Logs)</h2>
                    </div>
                    <button 
                      onClick={() => setNotifications([])}
                      className="text-[10px] text-[#8E8A85] hover:text-[#CD7F6D] font-semibold"
                    >
                      清空日志
                    </button>
                  </div>

                  <div className="space-y-2 h-[160px] overflow-y-auto pr-1">
                    {notifications.length === 0 ? (
                      <div className="py-12 text-center text-xs text-[#8E8A85] italic">
                        等待因果事件触发。流体日志为空。
                      </div>
                    ) : (
                      notifications.map((n) => {
                        let dotColor = "bg-[#7EA6B2]";
                        if (n.type === "warning") dotColor = "bg-[#CDAA78]";
                        if (n.type === "error") dotColor = "bg-[#CD7F6D]";
                        if (n.type === "success") dotColor = "bg-[#7B9E7A]";
                        
                        return (
                          <div key={n.id} className="bg-[#FAF8F5] p-2 rounded-xl border border-[#EAE3D9] flex items-start gap-2.5 text-[11px] leading-relaxed shadow-xs">
                            <span className={`w-2 h-2 rounded-full ${dotColor} mt-1.5 shrink-0`}></span>
                            <div className="flex-1">
                              <span className="text-[#2C2A29] font-medium">{n.text}</span>
                              <div className="text-[9px] text-[#8E8A85] font-mono mt-0.5">{n.time}</div>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* GENERAL SUMMARY OVERVIEW OF THE EXTENSION */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4EFEA]">
                      <Sparkles className="w-4 h-4 text-[#967A55]" />
                      <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">Chrome 扩展一键发布说明</h2>
                    </div>
                    <p className="text-xs text-[#615D5A] leading-relaxed">
                      本看板完整模拟了 <strong>SPL 心理流体推理引擎 (V8.0)</strong>。其状态与记忆、自尊、慢心境、睡眠债深度绑定，在 Chrome 扩展的生命周期中进行持久化保存，从而实现浏览器端“拥有自主人格”的持久化心理智能体。
                    </p>
                    <div className="grid grid-cols-2 gap-3 mt-4">
                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EAE3D9] shadow-xs">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">主入口界面</div>
                        <div className="text-xs font-bold text-[#615D5A] mt-0.5">Vite HTML + Popup</div>
                      </div>
                      <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EAE3D9] shadow-xs">
                        <div className="text-[10px] text-[#8E8A85] font-semibold">存储方案</div>
                        <div className="text-xs font-bold text-[#615D5A] mt-0.5">Chrome Local Storage</div>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setActiveTab("dev_tools")}
                    className="w-full py-2.5 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-xs rounded-xl active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4 shadow-sm"
                  >
                    <span>📦 前往打包 Chrome 扩展 ZIP 格式</span>
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
              className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start"
            >
              
              {/* LEFT COLUMN: API CONFIGURATION & LIVE CORE PERSONA PREVIEW (4 COLS) */}
              <div className="lg:col-span-4 flex flex-col gap-6">
                
                {/* INTERFACE CREDENTIALS */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] space-y-4">
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[#F4EFEA]">
                    <Lock className="w-4.5 h-4.5 text-[#967A55]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">
                      {t("🔑 大模型API直连配置", "🔑 API Configuration")}
                    </h2>
                  </div>

                  {/* Provider selection */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[#8E8A85] font-semibold block">{t("AI 服务商", "API Provider")}</label>
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
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[#EAE3D9] bg-white text-[#2C2A29] font-semibold focus:outline-none focus:border-[#967A55]"
                    >
                      <option value="openai">OpenAI (Direct client-side)</option>
                      <option value="claude">Anthropic Claude</option>
                      <option value="gemini">Google Gemini (Client-side)</option>
                      <option value="local">Local LLM (Ollama / LM Studio)</option>
                    </select>
                  </div>

                  {/* API Key */}
                  {apiProvider !== "local" && (
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <label className="text-[10px] text-[#8E8A85] font-semibold block">{t("API 密钥 (API Key)", "API Secret Key")}</label>
                        <span className="text-[8px] text-[#8E8A85] italic">{t("仅存在您本地浏览器", "Saved locally only")}</span>
                      </div>
                      <input
                        type="password"
                        value={apiKey}
                        placeholder="sk-..."
                        onChange={(e) => {
                          setApiKey(e.target.value);
                          localStorage.setItem("spl_api_key", e.target.value);
                        }}
                        className="w-full px-3 py-2 text-xs rounded-lg border border-[#EAE3D9] bg-white text-[#2C2A29] font-mono focus:outline-none focus:border-[#967A55]"
                      />
                    </div>
                  )}

                  {/* API Base URL */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[#8E8A85] font-semibold block">{t("代理 / 基础URL (Base URL)", "API Endpoint Base URL")}</label>
                    <input
                      type="text"
                      value={apiBaseUrl}
                      placeholder="https://..."
                      onChange={(e) => {
                        setApiBaseUrl(e.target.value);
                        localStorage.setItem("spl_api_base_url", e.target.value);
                      }}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[#EAE3D9] bg-white text-[#2C2A29] font-mono focus:outline-none focus:border-[#967A55]"
                    />
                  </div>

                  {/* Model Name */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-[#8E8A85] font-semibold block">{t("模型名称 (Model)", "AI Model Name")}</label>
                    <input
                      type="text"
                      value={apiModel}
                      placeholder="e.g. gpt-4o-mini"
                      onChange={(e) => {
                        setApiModel(e.target.value);
                        localStorage.setItem("spl_api_model", e.target.value);
                      }}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-[#EAE3D9] bg-white text-[#2C2A29] font-mono focus:outline-none focus:border-[#967A55]"
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
                      className="text-[9px] text-[#967A55] font-semibold bg-[#FAF8F5] border border-[#EAE3D9] hover:bg-[#F1ECE4] px-2.5 py-1.5 rounded-md flex-1 text-center transition-all"
                    >
                      {t("📋 恢复该渠道默认值", "Reset to Default")}
                    </button>
                    <button
                      onClick={() => {
                        setApiKey("");
                        localStorage.removeItem("spl_api_key");
                        addNotification(t("已清除本地密钥存储", "Cleared saved API Key"), "info");
                      }}
                      className="text-[9px] text-[#CD7F6D] font-semibold bg-white border border-[#F5E2DC] hover:bg-[#FAF0ED] px-2.5 py-1.5 rounded-md flex-1 text-center transition-all"
                    >
                      {t("🗑️ 清空本地密钥", "Clear Key")}
                    </button>
                  </div>

                  {/* Connection Warning */}
                  <div className="bg-[#FDFBF9] border border-[#F4EADA] p-2.5 rounded-lg text-[9px] text-[#8E8A85] leading-relaxed">
                    💡 <strong>{t("离线直连声明", "Direct Browser Connection")}:</strong>{" "}
                    {t(
                      "此端直连大模型 API，无中间服务器拦截。您的 API 密钥及聊天历史仅安全保存在浏览器本地（LocalStorage/Chrome Storage）中，不会上传给第三方。本地 Ollama 请确保开启 CORS，添加环境变量 OLLAMA_ORIGINS=\"*\"。",
                      "This app connects directly to the model API from your browser. Your API Keys are saved only in your browser storage. For Local Ollama, please configure OLLAMA_ORIGINS=\"*\" to prevent CORS errors."
                    )}
                  </div>
                </div>

                {/* PERSONA PROMPT PREVIEW */}
                <div className="bg-white border border-[#EAE3D9] rounded-2xl p-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[#F4EFEA]">
                    <Brain className="w-4.5 h-4.5 text-[#967A55]" />
                    <h2 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">
                      {t("🧠 实时心理人格 System Prompt", "🧠 Dynamic System Prompt")}
                    </h2>
                  </div>
                  <p className="text-[10px] text-[#8E8A85] leading-normal mb-3">
                    {t("由于心理流体在每秒和每次刺激后不断演变更新，大模型对话中注入的系统指令集也已实时映射了智能体的以下最新生理-心理阻抗、能量、自尊、创伤和压抑荷载：", "As the psychological fluids update in real-time, the model prompt incorporates the agent's active energy, self-esteem, active trauma, and repressions:")}
                  </p>
                  <div className="bg-[#FAF8F5] border border-[#EAE3D9] p-3 rounded-xl max-h-[220px] overflow-y-auto">
                    <pre className="text-[9px] text-[#615D5A] font-mono whitespace-pre-wrap leading-relaxed select-all">
                      {generateSystemPrompt()}
                    </pre>
                  </div>
                </div>

              </div>

              {/* RIGHT COLUMN: FLUID CONSCIOUSNESS CHAT BOX (8 COLS) */}
              <div className="lg:col-span-8 bg-white border border-[#EAE3D9] rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.015)] flex flex-col h-[680px] overflow-hidden">
                
                {/* Chat header */}
                <div className="bg-white border-b border-[#F4EFEA] p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-[#FAF8F5] border border-[#EAE3D9] flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-[#967A55] animate-pulse" />
                    </div>
                    <div>
                      <h3 className="text-xs font-bold text-[#2C2A29] font-display uppercase tracking-wide">
                        {t("流体意识对话通道 (Psyche-Fluid Channel)", "Fluid Consciousness Channel")}
                      </h3>
                      <div className="flex items-center gap-3 text-[9px] font-mono mt-0.5">
                        <span className="text-[#7B9E7A]">自尊: <span className="font-bold">{((snapshot.snap.self_esteem || 0) * 100).toFixed(0)}%</span></span>
                        <span className="text-[#7EA6B2]">能量: <span className="font-bold">{(snapshot.snap.energy || 0).toFixed(0)}/100</span></span>
                        <span className="text-[#CD7F6D]">疲劳: <span className="font-bold">{((snapshot.snap.fatigue || 0) * 100).toFixed(0)}%</span></span>
                        <span className="text-[#CDAA78]">认知失调: <span className="font-bold">{(snapshot.snap.cognitive_dissonance || 0).toFixed(2)}</span></span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => {
                      if (window.confirm(t("是否确认清空对话历史？", "Are you sure you want to clear chat history?"))) {
                        setChatMessages([
                          {
                            id: "welcome",
                            role: "assistant",
                            content: t(
                              "您好，我是由 SPL 心理流体推理引擎 V8.0 驱动的智能人格。我的状态已重置，请随意与我对话。\n\nHello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My status has been reset. Feel free to talk to me.",
                              "Hello, I am a psychological agent driven by the SPL Psychological Fluid Engine V8.0. My status has been reset. Feel free to talk to me."
                            ),
                            timestamp: new Date().toLocaleTimeString()
                          }
                        ]);
                      }
                    }}
                    className="text-[9px] text-[#8E8A85] hover:text-[#CD7F6D] font-semibold border border-[#EAE3D9] rounded-md px-2.5 py-1 bg-white hover:bg-[#FAF8F5] transition-all"
                  >
                    {t("🗑️ 清空历史", "Clear Chat")}
                  </button>
                </div>

                {/* Messages list */}
                <div className="flex-1 bg-[#FAF8F5] p-5 overflow-y-auto space-y-4">
                  {chatMessages.map((msg) => {
                    const isUser = msg.role === "user";
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isUser ? "justify-end" : "justify-start"} items-start gap-2.5`}
                      >
                        {!isUser && (
                          <div className="w-7 h-7 rounded-lg bg-white border border-[#EAE3D9] flex items-center justify-center shrink-0 shadow-xs">
                            <Brain className="w-3.5 h-3.5 text-[#967A55]" />
                          </div>
                        )}
                        <div className={`flex flex-col max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
                          <div
                            className={`px-4 py-3 rounded-2xl text-xs leading-relaxed shadow-xs whitespace-pre-wrap ${
                              isUser
                                ? "bg-gradient-to-br from-[#C5A880] to-[#967A55] text-white rounded-tr-none"
                                : "bg-white border border-[#EAE3D9] text-[#2C2A29] rounded-tl-none"
                            }`}
                          >
                            {msg.content}
                          </div>
                          <span className="text-[8px] text-[#8E8A85] font-mono mt-1 px-1">
                            {msg.timestamp}
                          </span>
                        </div>
                      </div>
                    );
                  })}

                  {isTyping && (
                    <div className="flex justify-start items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-white border border-[#EAE3D9] flex items-center justify-center shrink-0 shadow-xs">
                        <Brain className="w-3.5 h-3.5 text-[#967A55] animate-spin" />
                      </div>
                      <div className="px-4 py-2 bg-white border border-[#EAE3D9] text-[#8E8A85] rounded-2xl rounded-tl-none text-[10px] italic flex items-center gap-1.5 shadow-xs">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#967A55] animate-bounce" style={{ animationDelay: "0ms" }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[#967A55] animate-bounce" style={{ animationDelay: "150ms" }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[#967A55] animate-bounce" style={{ animationDelay: "300ms" }}></span>
                        <span>{t("心脑流体运算中...", "Fluid computing...")}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Pre-seeded prompts pills */}
                <div className="bg-[#FAF8F5] border-t border-[#F4EFEA] px-5 py-2.5 flex flex-wrap gap-2 items-center">
                  <span className="text-[9px] text-[#8E8A85] font-semibold">{t("💡 心理测试语:", "💡 Triggers:")}</span>
                  {[
                    {
                      zh: "批判我的想法，伤害我的自尊",
                      en: "Critique my ideas and lower my self-esteem",
                      desc: "🚨 Threat & Anger trigger"
                    },
                    {
                      zh: "真诚肯定我，给我拥抱与支持",
                      en: "Sincere affirmation, support, and a big hug",
                      desc: "❤️ Trust & Belonging trigger"
                    },
                    {
                      zh: "详细拆解并分析你的心理状态",
                      en: "Deconstruct and analyze your own active psy-state",
                      desc: "🧠 Intellectualization trigger"
                    }
                  ].map((seed, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputMessage(lang === "zh" ? seed.zh : seed.en)}
                      className="text-[9px] px-2.5 py-1 bg-white hover:bg-[#FAF8F5] border border-[#EAE3D9] text-[#615D5A] hover:text-[#967A55] rounded-full transition-all shadow-2xs active:scale-95"
                    >
                      {lang === "zh" ? seed.zh : seed.en}
                    </button>
                  ))}
                </div>

                {/* Input form */}
                <form
                  onSubmit={handleSendMessage}
                  className="bg-white border-t border-[#F4EFEA] p-4 flex gap-2.5 items-center"
                >
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={t("向流体心智输入意识信息...", "Type to transmit stimulus message to the fluid mind...")}
                    className="flex-1 px-4 py-3 text-xs bg-[#FAF8F5] border border-[#EAE3D9] rounded-xl focus:outline-none focus:border-[#967A55] placeholder:text-[#BEBAAF]"
                  />
                  <button
                    type="submit"
                    disabled={isTyping}
                    className="p-3 bg-[#967A55] hover:bg-[#836946] text-white rounded-xl active:scale-95 transition-all flex items-center justify-center shrink-0 shadow-sm"
                  >
                    <Send className="w-4 h-4 text-white" />
                  </button>
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
              <div className="bg-white border border-[#EAE3D9] rounded-2xl p-6 shadow-[0_8px_30px_rgba(0,0,0,0.015)] relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-[#C5A880]/5 blur-3xl rounded-full"></div>
                
                <div className="flex items-center gap-3 mb-4 pb-3 border-b border-[#F4EFEA]">
                  <Download className="w-5 h-5 text-[#967A55]" />
                  <div>
                    <h2 className="text-base font-bold font-display text-[#2C2A29] tracking-wide">打包与下载 Chrome 扩展 ZIP 文件</h2>
                    <p className="text-xs text-[#8E8A85] mt-0.5">将本心理流体推理智能体作为扩展打包并部署到您的浏览器中。</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-[#FAF8F5] p-4 rounded-xl border border-[#EAE3D9] space-y-2">
                    <h3 className="text-xs font-semibold text-[#2C2A29] flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#967A55]"></span>
                      扩展规格 (Package Specification)
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-[11px] font-mono">
                      <div>
                        <span className="text-[#8E8A85]">Manifest Version:</span>{" "}
                        <span className="text-[#615D5A] font-bold">MV3 (Latest)</span>
                      </div>
                      <div>
                        <span className="text-[#8E8A85]">Build Mode:</span>{" "}
                        <span className="text-[#615D5A] font-bold">Vite Minified Production</span>
                      </div>
                      <div>
                        <span className="text-[#8E8A85]">Popup Context:</span>{" "}
                        <span className="text-[#615D5A] font-bold">Full Offline SPA</span>
                      </div>
                      <div>
                        <span className="text-[#8E8A85]">Asset Mode:</span>{" "}
                        <span className="text-[#615D5A] font-bold">Relative Path (./)</span>
                      </div>
                      <div>
                        <span className="text-[#8E8A85]">Permissions:</span>{" "}
                        <span className="text-[#615D5A] font-bold">["storage"]</span>
                      </div>
                      <div>
                        <span className="text-[#8E8A85]">Output Target:</span>{" "}
                        <span className="text-[#615D5A] font-bold">extension.zip</span>
                      </div>
                    </div>
                  </div>

                  {/* STEP BY STEP LOADING TUTORIAL */}
                  <div className="space-y-3">
                    <h3 className="text-xs font-semibold text-[#2C2A29] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-[#7B9E7A]" />
                      部署到 Chrome 浏览器的步骤
                    </h3>

                    <div className="space-y-2 text-xs text-[#615D5A] pl-1">
                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">1</span>
                        <p className="mt-0.5">
                          点击下方 <strong>“下载 Chrome 扩展 ZIP”</strong> 按钮，下载由编译引擎打包生成的 <code>extension.zip</code> 压缩包。
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">2</span>
                        <p className="mt-0.5">
                          下载完成后，将 <code>extension.zip</code> 解压到一个本地磁盘目录（例如命名为 <code>spl-extension</code> 文件夹）。
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">3</span>
                        <p className="mt-0.5">
                          打开 Google Chrome 浏览器，在地址栏输入 <code>chrome://extensions</code> 并回车（或通过右上角 菜单 → 扩展程序 → 管理扩展程序 选项进入）。
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">4</span>
                        <p className="mt-0.5">
                          在扩展管理页面的右上角，开启 <strong>“开发者模式 (Developer Mode)”</strong> 开关。
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">5</span>
                        <p className="mt-0.5">
                          点击左上角的 <strong>“加载已解压的扩展程序 (Load unpacked)”</strong> 按钮，在弹出的文件浏览器中选择您解压出的 <code>dist</code> 文件夹。
                        </p>
                      </div>

                      <div className="flex gap-2.5">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-[#FAF8F5] border border-[#EAE3D9] text-[10px] font-bold text-[#967A55] shrink-0 shadow-xs">6</span>
                        <p className="mt-0.5">
                          部署成功！您可以直接在 Chrome 工具栏中点击扩展图标，唤起完全单机运行、离线持久化的心理智能体看板。
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* ACTION PACKAGING CARD WITH GLOWING DOWNLOAD BUTTON */}
                  <div className="border-t border-[#F4EFEA] pt-6 flex flex-col items-center justify-center text-center">
                    
                    <div className="mb-4">
                      <div className="text-xs text-[#8E8A85]">静态资源与构建输出压缩包</div>
                      <div className="text-[10px] text-[#BEBAAF] mt-1 font-mono">包含：manifest.json, popup index.html, JS/CSS bundles, icon.png</div>
                    </div>

                    <a
                      href="./extension.zip"
                      download="extension.zip"
                      className="inline-flex items-center gap-3 px-8 py-3.5 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-sm rounded-xl shadow-md transition-all font-display active:scale-[0.98]"
                    >
                      <Download className="w-5 h-5 text-white" />
                      <span>⚡️ 下载 Chrome 扩展 ZIP 包 (extension.zip)</span>
                    </a>

                    <p className="text-[10px] text-[#8E8A85] mt-3 font-mono">
                      * 注：本打包文件基于最新 Vite 生成的 minified 代码包。如果您在开发环境下初次打包，请确保在终端内执行过 <code>npm run build</code> 来生成该 zip 文件。
                    </p>

                  </div>

                </div>

              </div>

              {/* SECOND PERSPECTIVE CAUSAL ENGINE ESSENCE SHEET */}
              <div className="bg-white border border-[#EAE3D9] rounded-2xl p-6 shadow-[0_8px_30px_rgba(0,0,0,0.015)]">
                <div className="flex items-center gap-2.5 mb-3 pb-2 border-b border-[#F4EFEA]">
                  <Brain className="w-4.5 h-4.5 text-[#967A55]" />
                  <h3 className="text-sm font-semibold font-display text-[#2C2A29] tracking-wide">第二视角因果决定论规约</h3>
                </div>
                <div className="text-xs text-[#615D5A] space-y-2 leading-relaxed font-mono">
                  <p>
                    [逻辑拓扑]: 本智能体放弃了一切关于心理状态的概率学推理(Probabilistic Inference)，全面转换为因果决定论机制。
                  </p>
                  <p>
                    [决定论链条]: 输入事件 (E) → 认知增益 (Appraisal) → 瞬时流体映射 (Fluid Map) → 防御层级过滤 (Defense Filtration) → 压抑与隐压调节 (Repression Load) → 慢心境自更新 (Mood Dynamics) → 时间膨胀调制 (Dilation)。
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
                  className="px-6 py-2 rounded-xl bg-white border border-[#EAE3D9] text-xs text-[#8E8A85] hover:text-[#615D5A] font-semibold active:scale-[0.98] transition-all shadow-xs"
                >
                  ← 返回心理引擎状态看板
                </button>
              </div>

            </motion.div>
          )}

        </AnimatePresence>
      </main>

      {/* ========== FLOATING ACTION BUTTON: AGENT LIST ========== */}
      <button
        onClick={openAgentList}
        title={t("智能体库 / Agent Library", "智能体库 / Agent Library")}
        aria-label={t("打开智能体列表", "Open agent library")}
        className="fixed bottom-5 right-5 sm:bottom-6 sm:right-6 z-40 w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-br from-[#C5A880] via-[#DBC9B5] to-[#967A55] text-white shadow-lg shadow-[#967A55]/30 hover:shadow-xl hover:shadow-[#967A55]/40 flex items-center justify-center transition-all duration-300 hover:scale-110 hover:-translate-y-1 active:scale-95"
      >
        <Users className="w-5 h-5 sm:w-6 sm:h-6" strokeWidth={2.2} />
        <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-[#7B9E7A] border-2 border-white shadow-sm animate-pulse"></span>
      </button>

      {/* ========== AGENT LIST MODAL ========== */}
      <AnimatePresence>
        {isAgentListOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={closeAgentList}
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-[2px] flex items-center justify-center p-4"
              role="dialog"
              aria-modal="true"
              aria-label={t("智能体库", "Agent Library")}
            >
              {/* Modal panel */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                onClick={(e) => e.stopPropagation()}
                className="bg-white rounded-2xl shadow-2xl shadow-black/10 w-[92vw] max-w-2xl max-h-[85vh] flex flex-col overflow-hidden border border-[#EAE3D9]"
              >
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-[#F4EFEA] bg-gradient-to-r from-[#FDFBF9] to-white">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#C5A880] via-[#DBC9B5] to-[#967A55] p-0.5 shadow-sm">
                      <div className="w-full h-full rounded-[9px] bg-white flex items-center justify-center">
                        <Users className="w-4.5 h-4.5 text-[#967A55]" />
                      </div>
                    </div>
                    <div>
                      <h2 className="text-sm font-bold font-display text-[#2C2A29] tracking-wide">
                        {t("🎭 智能体库", "🎭 Agent Library")}
                      </h2>
                      <p className="text-[10px] text-[#8E8A85] mt-0.5">
                        {t(
                          `共 ${getAgentsList().length} 个人格 · ${customAgents.length} 个自定义`,
                          `${getAgentsList().length} agents total · ${customAgents.length} custom`
                        )}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={closeAgentList}
                    aria-label={t("关闭", "Close")}
                    className="w-8 h-8 rounded-full flex items-center justify-center text-[#8E8A85] hover:bg-[#F1ECE4] hover:text-[#615D5A] transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Agent list */}
                <div className="flex-1 overflow-y-auto p-5">
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
                                lang === "zh"
                                  ? `🎭 已切换为: ${preset.name}`
                                  : `🎭 Switched to: ${getAgentName(preset)}`,
                                "success"
                              );
                            }}
                            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between relative group ${
                              isActive
                                ? "bg-[#FAF7F2] border-[#C5A880] shadow-sm ring-1 ring-[#C5A880]"
                                : "bg-white border-[#EAE3D9] hover:bg-[#FAF8F5] hover:border-[#BEBAAF]"
                            } ${isEditing ? "ring-2 ring-[#967A55]" : ""}`}
                          >
                            {/* Builtin badge */}
                            {isBuiltin && (
                              <span className="absolute top-2 left-2 text-[7px] font-bold uppercase tracking-wider text-[#8E8A85] bg-[#F1ECE4] px-1.5 py-0.5 rounded shadow-xs">
                                {t("内置", "BUILTIN")}
                              </span>
                            )}

                            {/* Action buttons */}
                            <div className="absolute top-2 right-2 flex items-center gap-0.5">
                              {!isBuiltin && (
                                <button
                                  onClick={(e) => handleStartEdit(preset, e)}
                                  title={t("编辑", "Edit")}
                                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#967A55] hover:bg-[#F1ECE4] transition-all"
                                >
                                  <Edit3 className="w-3.5 h-3.5" />
                                </button>
                              )}
                              <button
                                onClick={(e) => handleExportAgent(preset, e)}
                                title={t("导出 JSON", "Export JSON")}
                                className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#7EA6B2] hover:bg-[#EDF2F4] transition-all"
                              >
                                <Download className="w-3.5 h-3.5" />
                              </button>
                              {!isBuiltin && (
                                <button
                                  onClick={(e) => handleDeleteCustomAgent(preset.id, e)}
                                  title={t("删除", "Delete")}
                                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#CD7F6D] hover:bg-[#FAF0ED] transition-all"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>

                            <div className={isBuiltin ? "pt-4" : ""}>
                              <div className="flex justify-between items-start gap-2">
                                <span className="text-xs font-bold text-[#2C2A29] flex items-center gap-1.5 pr-14">
                                  <Sparkles className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-[#C5A880] animate-pulse" : "text-[#BEBAAF] group-hover:text-[#967A55]"}`} />
                                  {getAgentName(preset)}
                                </span>
                              </div>
                              <p className="text-[10px] text-[#615D5A] mt-1.5 leading-relaxed line-clamp-2">
                                {getAgentDescription(preset)}
                              </p>
                            </div>

                            {isActive && (
                              <div className="absolute bottom-2 right-2 flex items-center gap-1 bg-[#7B9E7A] text-white text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">
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
                                className="overflow-hidden mt-2 bg-[#FAF8F5] border border-[#EAE3D9] rounded-xl p-3"
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-[10px] text-[#8E8A85] font-bold uppercase tracking-wider flex items-center gap-1">
                                    <Edit3 className="w-3 h-3 text-[#967A55]" />
                                    {t("编辑人格 JSON", "Edit Personality JSON")}
                                  </span>
                                </div>
                                <textarea
                                  value={editingJson}
                                  onChange={(e) => setEditingJson(e.target.value)}
                                  rows={8}
                                  className="w-full p-2.5 bg-[#FFFDFB] border border-[#EAE3D9] rounded-lg text-[10px] font-mono text-[#2C2A29] focus:outline-none focus:border-[#967A55] shadow-inner leading-normal resize-y"
                                />
                                <div className="flex justify-end gap-2 mt-2.5">
                                  <button
                                    onClick={handleCancelEdit}
                                    className="px-3 py-1.5 border border-[#EAE3D9] text-[#8E8A85] hover:text-[#615D5A] font-semibold text-[10px] rounded-lg transition-all active:scale-[0.97]"
                                  >
                                    {t("取消", "Cancel")}
                                  </button>
                                  <button
                                    onClick={handleSaveEdit}
                                    className="px-3.5 py-1.5 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-[10px] rounded-lg transition-all shadow-sm active:scale-[0.97] flex items-center gap-1"
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
                    <div className="mt-4 text-center py-6 bg-[#FAF8F5] rounded-xl border border-dashed border-[#EAE3D9]">
                      <Info className="w-6 h-6 text-[#BEBAAF] mx-auto mb-2" />
                      <p className="text-[10px] text-[#8E8A85] leading-relaxed">
                        {t(
                          "暂无自定义人格。前往「引擎看板」通过 JSON Sandbox 导入您自己的心理人格设定。",
                          "No custom personalities yet. Go to the Dashboard to import your own personality via the JSON Sandbox."
                        )}
                      </p>
                    </div>
                  )}
                </div>

                {/* Footer tip */}
                <div className="px-5 py-3 border-t border-[#F4EFEA] bg-[#FDFBF9] flex items-center justify-between">
                  <p className="text-[9px] text-[#BEBAAF] leading-relaxed">
                    {t(
                      "💡 点击卡片即可切换激活人格 · 悬停显示操作按钮 · ESC 关闭",
                      "💡 Click a card to activate · Hover for actions · ESC to close"
                    )}
                  </p>
                  <button
                    onClick={closeAgentList}
                    className="px-4 py-1.5 bg-[#967A55] hover:bg-[#836946] text-white font-bold text-[10px] rounded-lg transition-all shadow-sm active:scale-[0.97]"
                  >
                    {t("完成", "Done")}
                  </button>
                </div>
              </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

    </div>
  );
}
