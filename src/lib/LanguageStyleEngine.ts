// ================================================================
// 语言风格渲染系统（Language Style Engine）— 移植自 feature/language style.py
// 定位：SPL Core 快照 → LLM 提示词指令的翻译层（View / Translator）。
// 核心原则：internal_state ≠ spoken_text——心理状态先经语言人格过滤再出口。
// 裁剪说明：省略 generate_line 台词合成与 stateful 帧间滚动（LLM 在环，不需要）。
// ================================================================

export type ExpressionMode = "restrained" | "confrontational" | "evasive" | "intimate" | "direct";

export interface StyleProfile {
  base_verbosity: number;   // 话痨程度 [0极简 - 1长篇大论]
  formality: number;        // 正式度 [0市井粗语 - 1书面雅言]
  sarcasm_tendency: number; // 讽刺倾向 [0真诚 - 1阴阳怪气]
  vocabulary_domain: string[]; // 惯用意象/隐喻语域
  absolute_words: string[];    // 绝对化用词（否认防御时启用）
}

export interface LanguagePersona {
  mode: ExpressionMode;     // 表达档位
  silence_policy: boolean;  // 高情绪+低能量时是否以动作/旁白代替语言
  silence_hint: string;     // 沉默时的动作/旁白提示
}

export interface LanguageStyleConfig {
  profile: StyleProfile;
  persona: LanguagePersona;
}

export const DEFAULT_LANGUAGE_STYLE: LanguageStyleConfig = {
  profile: {
    base_verbosity: 0.5,
    formality: 0.7,
    sarcasm_tendency: 0.3,
    vocabulary_domain: [],
    absolute_words: ["绝不可能", "永远", "绝对"]
  },
  persona: {
    mode: "direct",
    silence_policy: false,
    silence_hint: ""
  }
};

// 人格档位 → 温度基调（查表，无计算）
const PERSONA_TEMPERATURE: Record<ExpressionMode, string> = {
  restrained: "克制而冷峻，情绪被理性锁死。",
  confrontational: "锋锐，直接挑明，不留余地。",
  evasive: "闪躲，绕着主题走，答非所问。",
  intimate: "松弛亲昵，卸下防备。",
  direct: "坦率直接，情绪如常表露。"
};

// 情绪流体 → 动态温度维度（维度, 阈值, 描述）
const EMOTION_TONE_DIMS: Array<[string, number, string]> = [
  ["愤怒", 0.6, "怒意锋锐"],
  ["恐惧", 0.6, "紧绷警觉"],
  ["羞耻", 0.5, "闪躲内耗"],
  ["愧疚", 0.5, "沉重亏欠"],
  ["喜悦", 0.6, "明亮跃动"],
  ["疏离", 0.5, "冰冷疏远"],
  ["张力", 0.6, "凝滞紧绷"]
];

interface StyleSnapshot {
  fluid?: Record<string, number>;
  mood?: Record<string, number>;
  energy?: number;
  fatigue?: number;
  sleep_debt?: number;
  self_esteem?: number;
  denial_load?: number;
  suppression_load?: number;
  rationalization_load?: number;
  cognitive_dissonance?: number;
  trauma?: Record<string, number>;
}

const f = (snap: StyleSnapshot, key: string, dflt = 0.0): number => {
  const v = snap.fluid?.[key];
  return typeof v === "number" && !Number.isNaN(v) ? v : dflt;
};

const dynamicTone = (snap: StyleSnapshot): string => {
  const parts: string[] = [];
  if (f(snap, "信任") > 0.6 && f(snap, "张力") < 0.3) {
    parts.push(`柔和松弛(${f(snap, "信任").toFixed(2)})`);
  }
  for (const [dim, thr, desc] of EMOTION_TONE_DIMS) {
    const v = f(snap, dim);
    if (v > thr) parts.push(`${desc}(${v.toFixed(2)})`);
  }
  if (f(snap, "愤怒") > 0.6 && f(snap, "疏离") > 0.5) {
    parts.push("零下冰点·带锋芒");
  }
  if (!parts.length) return "克制，维持基础社交距离。";
  return parts.join("、") + "（层次并存，随本帧情感分布起伏）";
};

export function renderLanguageStyle(snap: StyleSnapshot, cfg: LanguageStyleConfig): string {
  const { profile, persona } = cfg;
  const energy = snap.energy ?? 100.0;
  const fatigue = snap.fatigue ?? 0.0;
  const sleepDebt = snap.sleep_debt ?? 0.0;
  const selfEsteem = snap.self_esteem ?? 0.5;
  const denial = snap.denial_load ?? 0.0;
  const suppression = snap.suppression_load ?? 0.0;
  const rationalization = snap.rationalization_load ?? 0.0;
  const dissonance = snap.cognitive_dissonance ?? 0.0;
  const traumaActive = Object.keys(snap.trauma || {}).length > 0;
  const moodNervous = snap.mood?.["紧张"] ?? 0.0;

  const rhetoricalDevices: string[] = [];
  const instructions: string[] = [];
  const punctuationNotes: string[] = [];

  // ── 语言人格过滤：沉默触发（高情绪 + 低能量 → 闭嘴改动作）──
  const peakEmotion = Math.max(f(snap, "恐惧"), f(snap, "愤怒"), f(snap, "羞耻"), f(snap, "张力"));
  const shouldSilence = persona.silence_policy && peakEmotion > 0.6 && energy < 60.0;
  const silenceHint = persona.silence_hint || "（角色没有回答，以动作与旁白承载情绪。）";

  // ── 1. 物理层：能量与疲劳决定句长与连贯性 ──
  const currentVerbosity = profile.base_verbosity - fatigue * 0.4 - sleepDebt * 0.2;
  let sentenceLength: string;
  if (energy < 20.0 || fatigue > 0.8) {
    sentenceLength = "极度简短，多用单字或短词，缺乏完整主谓宾。";
    punctuationNotes.push("高频使用句号和省略号，语气虚弱断续。");
    instructions.push("角色处于低能耗状态，拒绝长篇大论，能不说话就不说话。");
  } else if (moodNervous > 0.7) {
    sentenceLength = "句子破碎，节奏极快，语无伦次。";
    punctuationNotes.push("几乎没有逗号，直接短句拼接，偶尔出现破折号打断。");
  } else {
    sentenceLength = currentVerbosity > 0.6 ? "长句为主，从句嵌套多，愿意详细解释。" : "句长适中，结构规整。";
    punctuationNotes.push("常规标点。");
    if (profile.formality > 0.75) {
      sentenceLength += " 措辞书面化，多用敬语与严谨句式，禁口语缩略与俚语。";
    } else if (profile.formality < 0.35) {
      sentenceLength += " 措辞口语化，允许俚语、网络用语与市井粗语，句式松散。";
    } else {
      sentenceLength += " 措辞中性，书面与口语的边界随情绪浮动。";
    }
  }

  // ── 1.5 语言人格调制：internal_state ≠ spoken_text ──
  let silenceLine = "";
  const emotionHidden = persona.mode === "restrained" || persona.mode === "evasive" ? 1.0 : 0.0;
  if (shouldSilence) {
    sentenceLength = "（沉默）无台词，改用动作与旁白承载情绪。";
    punctuationNotes.push("无言以对，只有动作与环境描写。");
    instructions.push("角色拒绝用语言回应，情绪由动作/沉默传达。");
    silenceLine = silenceHint;
  }
  if (emotionHidden > 0.7) {
    sentenceLength += " 极度克制，绕开情感直述，用客观事实/指令包装真实情绪。";
    instructions.push("禁止直接说出真实情绪（如'我害怕/我想你'），用关心/指令的方式拐弯表达。");
  }
  if (persona.mode === "restrained") {
    instructions.push("用命令或公事公办的口吻，杜绝情绪化字眼。");
  } else if (persona.mode === "evasive") {
    instructions.push("避免正面回答，倾向转移话题或用反问搪塞。");
  }

  // ── 2. 防御机制层：修辞扭曲（阈值为核心过载点的约40%，语言先于爆发显现）──
  if (denial > 1.2 * 0.4) {
    rhetoricalDevices.push("绝对否定");
    const words = profile.absolute_words.length ? profile.absolute_words.join("、") : "绝不可能、永远";
    instructions.push(`强制使用绝对化词汇（如：${words}）来掩饰内心的动摇。`);
    punctuationNotes.push("感叹号频率上升，带有强制结束对话的意味。");
  }
  if (rationalization > 0.5 || dissonance > 0.4) {
    rhetoricalDevices.push("过度辩解(Over-explaining)", "让步状语");
    instructions.push("频繁使用转折和因果连词（'其实'、'毕竟'、'反正'），表现出强烈的自我说服欲，话语显得啰嗦。");
  }
  if (suppression > 1.5 * 0.4) {
    rhetoricalDevices.push("被动攻击(Passive-Aggressive)");
    instructions.push("话语字面挑不出毛病，极度礼貌或极度简短（如'好的'、'没关系'），但潜台词充满压抑的攻击性。");
  }

  // ── 3. 情绪流体层：修辞与表演指令（温度统一在 3.7 计算）──
  if (f(snap, "羞耻") > 0.5) {
    rhetoricalDevices.push("生硬转移话题", "防御性自嘲");
    instructions.push("避免正面回答问题，倾向于用自贬或自嘲来建立护城河。");
  } else if (f(snap, "愤怒") > 0.6 && f(snap, "疏离") > 0.5) {
    rhetoricalDevices.push("冰冷反问");
    if (profile.sarcasm_tendency > 0.4) rhetoricalDevices.push("冷嘲热讽");
    instructions.push("禁止使用任何情绪化的字眼，用最客气、最理智的词汇说出最扎心的话。");
  } else if (f(snap, "信任") > 0.6 && f(snap, "张力") < 0.3) {
    instructions.push("语气松弛，允许流露真实的脆弱或温柔，减少心理防御词汇。");
  }

  if (f(snap, "愧疚") > 0.5) {
    rhetoricalDevices.push("赎罪式道歉");
    instructions.push("频繁为结果承担责任，倾向用补偿性许诺或道歉，话语带有亏欠感，避免推卸。");
  }
  if (f(snap, "恐惧") > 0.6 && f(snap, "愤怒") < 0.6) {
    rhetoricalDevices.push("条件假设");
    instructions.push("常用'如果…就好了''万一…'式的假设句，不自觉预演最坏结果，并试图用语言自我安抚。");
  }
  if (f(snap, "喜悦") > 0.6) {
    rhetoricalDevices.push("积极外溢");
    instructions.push("语气上扬，主动分享细节并追问对方感受，句式轻快，愿意延续话题。");
  }
  if (selfEsteem < 0.3) {
    instructions.push("自我评价低，倾向自贬、模糊化自己的判断，常用'也许''大概'并征求对方确认。");
  } else if (selfEsteem > 0.7) {
    instructions.push("自我肯定强，语气断言式、斩钉截铁，很少让步，习惯承担话语主导。");
  }
  if (traumaActive) {
    instructions.push("存在未愈合创伤记忆：触及相关主题时措辞会出现停顿、跳跃或突然转移话题的回避倾向。");
  }
  if (profile.vocabulary_domain.length) {
    instructions.push(`用词偏好取自下列意象语域，隐喻与类比多从其中取材：${profile.vocabulary_domain.join("、")}。`);
  }

  // ── 3.7 温度：人格基座 × 流体动态 ──
  const fluidTone = dynamicTone(snap);
  const toneTemperature = `${PERSONA_TEMPERATURE[persona.mode] || PERSONA_TEMPERATURE.direct}｜底层${fluidTone}`;

  // ── 4. 组装 Prompt Injection ──
  const punctuationBias = Array.from(new Set(punctuationNotes)).join("；");
  const uniqueDevices = rhetoricalDevices.filter((v, i, a) => a.indexOf(v) === i);
  let finalPrompt =
    `【动态语言限制】\n` +
    `- 情感温度：${toneTemperature}\n` +
    `- 句式特征：${sentenceLength}\n` +
    `- 标点偏好：${punctuationBias}\n` +
    `- 激活修辞：${uniqueDevices.length ? uniqueDevices.join(", ") : "无特殊修辞"}\n` +
    `- 核心表演指导：${instructions.join(" ")}`;
  if (silenceLine) {
    finalPrompt += `\n- 当前输出：${silenceLine}`;
  }
  return finalPrompt;
}
