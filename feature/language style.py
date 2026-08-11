# ================================================================
# 语言风格渲染系统（Language Style Engine）—— 【自设模块】
# ================================================================
# 定位：MVC架构中的 View（视图层）/ Translator（翻译层）。
# 作用：监听 SPL Core V8.0 的内部状态（流体、心境、防御机制），
#      将其转化为结构化的语言学特征和 LLM 提示词指令。
# 
# 机制：
# - 能量/疲劳决定话语的长短与语速（句长、省略号频率）。
# - 压抑/否认机制决定防御性修辞（绝对否定词、辩解性连词）。
# - 情绪流体（如羞耻、愤怒）决定语气温度与社交距离。
# ================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class StyleProfile:
    """
    角色的静态语言风格基线（Static Linguistic Traits）。
    相当于角色的“默认声带和词汇库”。
    """
    base_verbosity: float = 0.5        # 默认话痨程度 [0.0极简 - 1.0长篇大论]
    formality: float = 0.7             # 默认正式度 [0.0市井粗语 - 1.0书面雅言]
    sarcasm_tendency: float = 0.3      # 默认讽刺倾向 [0.0真诚 - 1.0阴阳怪气]
    favorite_fillers: List[str] = field(default_factory=lambda: ["…", "所以", "不过"])
    absolute_words: List[str] = field(default_factory=lambda: ["绝不可能", "永远", "绝对"])


@dataclass
class RenderedStyle:
    """
    动态生成的语言风格指令（Dynamic Style Output）。
    可直接无缝转换为 LLM 的 System Prompt 或微调约束。
    """
    sentence_length: str               # 句长特征（如"极短，词组拼凑"，"长句，逻辑严密"）
    rhetorical_devices: List[str]      # 激活的修辞手法（如["反问", "讽刺", "过度辩解"]）
    punctuation_bias: str              # 标点符号倾向（如"大量使用句号"，"省略号频发"）
    tone_temperature: str              # 情感温度（如"冰冷疏离", "极度失控", "温和"）
    prompt_injection: str              # 建议直接注入 LLM Prompt 的指令


class LanguageStyleEngine:
    """
    风格渲染引擎：将枯燥的浮点数转化为文字的张力。
    """
    def __init__(self, profile: StyleProfile = None):
        self.profile = profile or StyleProfile()

    def render_style(self, core_snapshot: Dict[str, Any]) -> RenderedStyle:
        """
        核心渲染逻辑：解析 V8.0 快照，生成当前帧的语言风格。
        """
        # 提取核心状态
        fluid = core_snapshot.get("fluid", {})
        mood = core_snapshot.get("mood", {})
        energy = core_snapshot.get("energy", 100.0)
        fatigue = core_snapshot.get("fatigue", 0.0)
        
        # 提取防御与失调机制
        suppression = core_snapshot.get("suppression_load", 0.0)
        denial = core_snapshot.get("denial_load", 0.0)
        rationalization = core_snapshot.get("rationalization_load", 0.0)
        dissonance = core_snapshot.get("cognitive_dissonance", 0.0)
        sleep_debt = core_snapshot.get("sleep_debt", 0.0)

        # 初始化输出特征
        rhetorical_devices = []
        instructions = []
        # 标点/风格倾向用列表累积，最后合并——避免物理层与防御层互相覆盖。
        punctuation_notes = []

        # ==========================================
        # 1. 物理层：能量与疲劳计算句长与连贯性
        # ==========================================
        current_verbosity = self.profile.base_verbosity - (fatigue * 0.4) - (sleep_debt * 0.2)
        if energy < 20.0 or fatigue > 0.8:
            sentence_length = "极度简短，多用单字或短词，缺乏完整主谓宾。"
            punctuation_notes.append("高频使用句号和省略号，语气虚弱断续。")
            instructions.append("角色处于低能耗状态，拒绝长篇大论，能不说话就不说话。")
        elif mood.get("紧张", 0.0) > 0.7:
            sentence_length = "句子破碎，节奏极快，语无伦次。"
            punctuation_notes.append("几乎没有逗号，直接短句拼接，偶尔出现破折号打断。")
        else:
            if current_verbosity > 0.6:
                sentence_length = "长句为主，从句嵌套多，愿意详细解释。"
            else:
                sentence_length = "句长适中，结构规整。"
            punctuation_notes.append("常规标点。")

        # ── formality 消费：正式度调制句长与措辞基调 ──
        # 低正式度 → 允许俚语、口语缩略、市井粗语；高正式度 → 书面雅言、禁口语缩略。
        # 仅在非极端状态（非低能耗、非紧张破碎）下叠加，避免与紧急状态抢戏。
        if energy >= 20.0 and fatigue <= 0.8 and mood.get("紧张", 0.0) <= 0.7:
            if self.profile.formality > 0.75:
                sentence_length += " 措辞书面化，多用敬语与严谨句式，禁口语缩略与俚语。"
            elif self.profile.formality < 0.35:
                sentence_length += " 措辞口语化，允许俚语、网络用语与市井粗语，句式松散。"
            else:
                sentence_length += " 措辞中性，书面与口语的边界随情绪浮动。"

        # ==========================================
        # 2. 防御机制层：最核心的“修辞扭曲”
        # ==========================================
        # 注意：以下阈值是【语言倾向起点】，并非核心引擎的过载点。
        # 核心引擎过载语义为：denial>=1.2 / suppression>=1.5 触发现实侵入或爆发；
        # 此处取过载点的比例（约 40%~50%）作为“话语已开始出现防御倾向”的阈值，
        # 使语言风格先于心理爆发显现，两者语义不冲突。
        # 否认可达性常数（对应核心 DENIAL_THRESHOLD=1.2）
        DENIAL_OVERLOAD = 1.2
        # 压抑可过载常数（对应核心 SUPPRESSION_THRESHOLD=1.5）
        SUPPRESSION_OVERLOAD = 1.5

        # 否认仓 (Denial) 倾向：绝对化词汇防御
        if denial > DENIAL_OVERLOAD * 0.4:  # ~0.48
            rhetorical_devices.append("绝对否定")
            instructions.append(f"强制使用绝对化词汇（如：{', '.join(self.profile.absolute_words)}）来掩饰内心的动摇。")
            punctuation_notes.append("感叹号频率上升，带有强制结束对话的意味。")

        # 合理化仓 (Rationalization) 倾向：过度辩解
        if rationalization > 0.5 or dissonance > 0.4:
            rhetorical_devices.append("过度辩解(Over-explaining)")
            rhetorical_devices.append("让步状语")
            instructions.append("频繁使用转折和因果连词（‘其实’、‘毕竟’、‘反正’），表现出强烈的自我说服欲，话语显得啰嗦。")

        # 压抑仓 (Suppression) 倾向：被动攻击与字面顺从
        if suppression > SUPPRESSION_OVERLOAD * 0.4:  # ~0.6
            rhetorical_devices.append("被动攻击(Passive-Aggressive)")
            instructions.append("话语字面挑不出毛病，极度礼貌或极度简短（如‘好的’、‘没关系’），但潜台词充满压抑的攻击性。")

        # ==========================================
        # 3. 情绪流体层：温度与态度
        # ==========================================
        # 羞耻 (Shame) 驱动：回避与自嘲
        if fluid.get("羞耻", 0.0) > 0.5:
            rhetorical_devices.append("生硬转移话题")
            rhetorical_devices.append("防御性自嘲")
            instructions.append("避免正面回答问题，倾向于用自贬或自嘲来建立护城河。")
            tone_temperature = "闪躲，内耗，带着自弃的冰冷。"
        
        # 愤怒 (Anger) 与 疏离 (Detachment) 的组合
        elif fluid.get("愤怒", 0.0) > 0.6 and fluid.get("疏离", 0.0) > 0.5:
            rhetorical_devices.append("冰冷反问")
            if self.profile.sarcasm_tendency > 0.4:
                rhetorical_devices.append("冷嘲热讽")
            tone_temperature = "零下冰点，极度疏远且带有锋芒。"
            instructions.append("禁止使用任何情绪化的字眼，用最客气、最理智的词汇说出最扎心的话。")
            
        # 正常状态 / 信任状态
        elif fluid.get("信任", 0.0) > 0.6 and fluid.get("张力", 0.0) < 0.3:
            tone_temperature = "温和，卸下防备，留有余地。"
            instructions.append("语气松弛，允许流露真实的脆弱或温柔，减少心理防御词汇。")
        else:
            tone_temperature = "克制，维持基础的社交距离。"

        # ==========================================
        # 4. 组装 Prompt Injection
        # ==========================================
        # 合并所有标点/风格倾向：物理层（基线）在前，防御层/情绪层追加在后。
        punctuation_bias = "；".join(dict.fromkeys(punctuation_notes))

        final_prompt = (
            f"【动态语言限制】\n"
            f"- 情感温度：{tone_temperature}\n"
            f"- 句式特征：{sentence_length}\n"
            f"- 标点偏好：{punctuation_bias}\n"
            f"- 激活修辞：{', '.join(rhetorical_devices) if rhetorical_devices else '无特殊修辞'}\n"
            f"- 核心表演指导：{' '.join(instructions)}"
        )

        return RenderedStyle(
            sentence_length=sentence_length,
            rhetorical_devices=rhetorical_devices,
            punctuation_bias=punctuation_bias,
            tone_temperature=tone_temperature,
            prompt_injection=final_prompt
        )


# ================================================================
# 运行示例
# ================================================================
if __name__ == "__main__":
    # 模拟一个 V8.0 核心在经历了“熬夜+被戳中痛点（高否认+高羞耻）”后的快照
    mock_snapshot = {
        "fluid": {"羞耻": 0.7, "愤怒": 0.4, "疏离": 0.6, "信任": 0.1, "张力": 0.8},
        "mood": {"紧张": 0.8},
        "energy": 40.0,
        "fatigue": 0.6,
        "sleep_debt": 0.5,
        "denial_load": 0.8,         # 极力否认现状
        "suppression_load": 0.2,
        "rationalization_load": 0.1,
        "cognitive_dissonance": 0.2
    }

    # 实例化一个基础角色风格（比如一个平时比较正式、有轻微嘲讽倾向的人）
    base_profile = StyleProfile(base_verbosity=0.6, formality=0.8, sarcasm_tendency=0.5)
    style_engine = LanguageStyleEngine(base_profile)
    
    # 渲染当前帧的语言风格
    rendered = style_engine.render_style(mock_snapshot)
    
    print("=== 当前语言风格渲染结果 ===")
    print(rendered.prompt_injection)
