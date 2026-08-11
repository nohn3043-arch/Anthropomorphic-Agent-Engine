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
from typing import Dict, Any, List, Optional


# ================================================================
# 【语言人格模块 Language Persona】—— 表达过滤层
#
# 核心原则：internal_state ≠ spoken_text
#   心理状态（SPL Core 输出）必须先经过语言人格过滤，才能变成台词。
#   一个控制欲强、情绪不外露的角色（如祁皇英），内心恐惧 0.8，
#   不会说"我担心你"，而会说"不要再做这种无意义的冒险"。
#
# 分层：
#   LanguagePersonaNode   → 人格：决定【为什么这么说】（过滤/意图）
#   StyleProfile          → 风格：决定【怎么说】（句长/正式度/讽刺）
#   render_style()        → 渲染：把过滤后的意图变成文字指令
# ================================================================

@dataclass
class LanguagePersonaNode:
    """
    角色的语言人格——决定"心理状态如何被隐藏/扭曲后表达"。
    每个维度 [0,1]。
    """
    # 情绪表达
    emotional_exposure: float = 0.5   # 情绪外露：0.0全藏 - 1.0全露
    emotional_control: float = 0.5    # 情绪控制力（越高，情绪越被理性压制）

    # 冲突表达
    confrontation: float = 0.5        # 正面对抗倾向
    avoidance: float = 0.5            # 回避/闪躲倾向

    # 权力表达
    dominance: float = 0.5            # 权力压制（高→命令式）
    submission: float = 0.5           # 服从

    # 信息表达
    honesty: float = 0.7              # 坦诚
    concealment: float = 0.3          # 隐瞒

    # 关系表达
    intimacy_expression: float = 0.5  # 亲密表达
    dependency_expression: float = 0.5  # 依赖表达


@dataclass
class ExpressionResult:
    """
    表达过滤输出——心理状态经人格过滤后的"该怎么说/该不该说"。
    """
    expression_mode: str              # "restrained" / "direct" / "confrontational" / "evasive" / "intimate"
    emotion_hidden: float             # 心理被隐藏比例 [0,1]
    speech_intention: str             # "indirect_protection" / "direct_disclosure" / "power_assertion" / "concealment"
    should_silence: bool              # 是否触发沉默策略
    silence_hint: str = ""            # 沉默时的动作/旁白提示（should_silence=True 时使用）


class DefenseExpression:
    """
    防御机制 → 语言的模板映射（原 defense_expression.py 职责，融入本模块）。
    当检测到高防御载荷时，返回对应的台词意图模板，供渲染层参考。
    """
    # 内部心理状态 → 表面台词模板
    UTTERANCE_TEMPLATES: Dict[str, Dict[str, str]] = {
        "denial": {
            "internal": "害怕失去 / 拒绝承认",
            "intention": "indirect_protection",
            "line": "只是觉得你留下更方便。",
        },
        "rationalization": {
            "internal": "舍不得 / 不愿承认在乎",
            "intention": "concealment",
            "line": "你的能力还有利用价值。",
        },
        "projection": {
            "internal": "自己不安 / 投射到对方",
            "intention": "power_assertion",
            "line": "看来是你不相信我。",
        },
    }


class LanguagePersonaEngine:
    """
    语言人格引擎：把 SPL Core 快照过滤成"表达方式"，而非直接翻译成台词。

    这是 internal_state ≠ spoken_text 的强制执行层：
    - 高隐藏度 + 强情绪 → 台词拐弯（indirect_protection），甚至闭嘴改动作（silence）。
    """
    def __init__(self, persona: LanguagePersonaNode = None,
                 style: "StyleProfile" = None):
        self.persona = persona or LanguagePersonaNode()
        self.style = style or StyleProfile()

    def filter_expression(self, core_snapshot: Dict[str, Any]) -> ExpressionResult:
        """
        核心过滤逻辑：解析 V8.0 快照，决定角色"该怎么说、该不该说"。
        """
        fluid = core_snapshot.get("fluid", {})
        fear = fluid.get("恐惧", 0.0)
        anger = fluid.get("愤怒", 0.0)
        shame = fluid.get("羞耻", 0.0)
        tension = fluid.get("张力", 0.0)
        denial = core_snapshot.get("denial_load", 0.0)
        suppression = core_snapshot.get("suppression_load", 0.0)
        rationalization = core_snapshot.get("rationalization_load", 0.0)
        energy = core_snapshot.get("energy", 100.0)

        # 1. 情绪隐藏度 = 心理强度 × (1 - 外露度) × 控制力
        peak_emotion = max(fear, anger, shame, tension)
        self.emotion_hidden = (
            peak_emotion
            * (1.0 - self.persona.emotional_exposure)
            * self.persona.emotional_control
        )

        # 2. 沉默决策：回避/隐瞒高 + 情绪强 + 低能量 → 闭嘴改动作
        should_silence = (
            (self.persona.avoidance > 0.6 or self.persona.concealment > 0.6)
            and peak_emotion > 0.6
            and energy < 60.0
        )
        silence_hint = ""
        if should_silence:
            # 用动作代替语言——情绪越强，动作越克制
            if shame > 0.6:
                silence_hint = "她没有回答。只是垂下眼帘，避开了目光。"
            elif fear > 0.6:
                silence_hint = "他没有回答。只是不动声色地退后半步。"
            else:
                silence_hint = "她没有回答。只是替他整理了一下衣袖。"

        # 3. 表达模式判定：冲突 + 权力 + 关系综合
        if self.persona.dominance > 0.7 and self.persona.confrontation < 0.4:
            expression_mode = "restrained"      # 高压控制，情绪不外露
            speech_intention = "power_assertion"
        elif (self.persona.confrontation > 0.7 and fear < 0.4):
            expression_mode = "confrontational"
            speech_intention = "direct_disclosure"
        elif (self.persona.avoidance > 0.6 or shame > 0.5):
            expression_mode = "evasive"
            speech_intention = "indirect_protection"
        elif (self.persona.intimacy_expression > 0.6
              and self.persona.concealment < 0.4):
            expression_mode = "intimate"
            speech_intention = "direct_disclosure"
        else:
            expression_mode = "direct"
            speech_intention = "direct_disclosure"

        # 4. 防御载荷 → 修正真实意图（覆盖上面的默认判断）
        if denial > 0.5:
            speech_intention = DefenseExpression.UTTERANCE_TEMPLATES["denial"]["intention"]
        elif rationalization > 0.5:
            speech_intention = DefenseExpression.UTTERANCE_TEMPLATES["rationalization"]["intention"]
        elif suppression > 0.6:
            speech_intention = "concealment"

        return ExpressionResult(
            expression_mode=expression_mode,
            emotion_hidden=round(min(1.0, self.emotion_hidden), 3),
            speech_intention=speech_intention,
            should_silence=should_silence,
            silence_hint=silence_hint,
        )


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
    silence_hint: str = ""             # 语言人格触发的沉默策略动作描写（默认空=正常说话）


class LanguageStyleEngine:
    """
    风格渲染引擎：将枯燥的浮点数转化为文字的张力。
    """
    def __init__(self, profile: StyleProfile = None):
        self.profile = profile or StyleProfile()

    def render_style(self, core_snapshot: Dict[str, Any],
                     expression: Optional[ExpressionResult] = None) -> RenderedStyle:
        """
        核心渲染逻辑：解析 V8.0 快照，生成当前帧的语言风格。

        Args:
            core_snapshot: SPL Core 快照
            expression: 语言人格过滤结果（LanguagePersonaEngine.filter_expression 的输出）。
                        传入时，表达模式/隐藏度会调制句式与温度（internal_state≠spoken_text）。
                        不传则退化为纯风格渲染（向后兼容）。
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
        # 1.5 语言人格调制：internal_state ≠ spoken_text
        # ==========================================
        # 传入 LanguagePersonaEngine 的过滤结果时，表达模式/隐藏度覆盖默认句长与温度。
        # 这是"人格层压制风格层"的关键——控制型角色恐惧时不会脱口而出。
        silence_hint = ""
        persona_mode = None
        persona_active = False
        if expression is not None:
            mode = expression.expression_mode
            hidden = expression.emotion_hidden
            silence_hint = expression.silence_hint

            if expression.should_silence:
                # 触发沉默：不产出台词风格，改走动作描写
                sentence_length = "（沉默）无台词，改用动作与旁白承载情绪。"
                punctuation_notes.append("无言以对，只有动作与环境描写。")
                instructions.append("角色拒绝用语言回应，情绪由动作/沉默传达。")

            # 隐藏度越高，措辞越需要"绕着说"
            if hidden > 0.7:
                sentence_length += " 极度克制，绕开情感直述，用客观事实/指令包装真实情绪。"
                instructions.append("禁止直接说出真实情绪（如'我害怕/我想你'），用关心/指令的方式拐弯表达。")
            elif hidden > 0.4:
                sentence_length += " 有所保留，不完全坦白，留白。"
                instructions.append("情绪可表露但需保留三分，不把心理活动全部说出。")

            # 记录人格表达模式，温度在情绪流体层之后统一覆盖（人格层优先）
            persona_mode = mode
            persona_active = True

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
        # 3.5 人格温度最终覆盖（人格层优先于情绪层）
        # ==========================================
        # 情绪流体层的修辞设备照常累积，但最终温度基调以人格表达模式为准。
        # 关键：控制型角色（祁皇英）即使内心羞耻/恐惧，表面温度仍是"冷峻克制"而非"闪躲内耗"。
        if persona_active:
            if persona_mode == "restrained":
                tone_temperature = "克制而冷峻，情绪被理性锁死。"
                instructions.append("用命令或公事公办的口吻，杜绝情绪化字眼。")
            elif persona_mode == "confrontational":
                tone_temperature = "锋锐，直接挑明，不留余地。"
            elif persona_mode == "evasive":
                tone_temperature = "闪躲，绕着主题走，答非所问。"
                instructions.append("避免正面回答，倾向转移话题或用反问搪塞。")
            elif persona_mode == "intimate":
                tone_temperature = "松弛亲昵，卸下防备。"
            elif persona_mode == "direct":
                tone_temperature = "坦率直接，情绪如常表露。"

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
            prompt_injection=final_prompt,
            silence_hint=silence_hint
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

    # 渲染当前帧的语言风格（不传 expression → 纯风格渲染，向后兼容）
    rendered = style_engine.render_style(mock_snapshot)

    print("=== 示例1：纯风格渲染（向后兼容）===")
    print(rendered.prompt_injection)

    # ════════════════════════════════════════════════════════════
    # 示例2：语言人格过滤——祁皇英（高压控制型，情绪深藏）
    #   内心恐惧+羞耻很高，但表达时被完全过滤，甚至触发沉默。
    # ════════════════════════════════════════════════════════════
    qihuangying_persona = LanguagePersonaNode(
        emotional_exposure=0.05,   # 几乎不外露情绪
        emotional_control=0.95,    # 极强的情绪控制
        confrontation=0.3,         # 不正面冲突
        avoidance=0.7,             # 高回避
        dominance=0.9,             # 高压控制
        submission=0.1,
        honesty=0.3,               # 不坦诚
        concealment=0.8,           # 高隐瞒
        intimacy_expression=0.2,   # 极少表达亲密
        dependency_expression=0.1,
    )
    qihuangying_style = StyleProfile(base_verbosity=0.4, formality=0.9, sarcasm_tendency=0.4)

    persona_engine = LanguagePersonaEngine(qihuangying_persona, qihuangying_style)
    expression = persona_engine.filter_expression(mock_snapshot)

    print("\n=== 示例2：语言人格过滤结果（祁皇英）===")
    print(f"表达模式      : {expression.expression_mode}")
    print(f"情绪隐藏度    : {expression.emotion_hidden}")
    print(f"真实意图      : {expression.speech_intention}")
    print(f"触发沉默      : {expression.should_silence}")
    if expression.should_silence:
        print(f"沉默动作描写  : {expression.silence_hint}")

    # 把过滤结果喂入渲染器 → 台词风格
    rendered2 = style_engine.render_style(mock_snapshot, expression=expression)
    print("\n=== 示例2：渲染后（祁皇英台词风格）===")
    print(rendered2.prompt_injection)
    if rendered2.silence_hint:
        print(f"【输出】{rendered2.silence_hint}")
