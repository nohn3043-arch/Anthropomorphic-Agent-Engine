import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


# ================================================================
# 1. 外部叙事映射器（"自设：偏见/世界观/价值观"——纯外部策略）
#    用户可随意替换，无需修改核心代码。
# ================================================================
class NarrativeMapper:
    """
    世界观/价值观解释器。
    把外界事件（"被侮辱"、"被夸奖"）翻译成核心能消化的基础内感受向量。
    不同角色（乐观/偏执/厌世）只需替换此 Mapper。
    """
    @staticmethod
    def map_event(event: str, intensity: float) -> Dict[str, float]:
        base = {}
        if event == "compliment":
            base = {"belonging": 0.3 * intensity, "autonomy": 0.1 * intensity}
        elif event == "insult":
            base = {"belonging": -0.4 * intensity, "threat": 0.3 * intensity}
        elif event == "betrayal":
            base = {"belonging": -0.6 * intensity, "threat": 0.5 * intensity}
        elif event == "alone":
            base = {"belonging": -0.3 * intensity}
        elif event == "rest":
            base = {"fatigue": -0.5 * intensity}
        else:
            base = {"belonging": 0.0, "threat": 0.0}
        return base


# ================================================================
# 2. SPL 纯净流体核心 V8.0 — 完整拟人心理架构
#
#    V7.3 已有：
#      7维情绪流体 / 创伤节点 / 记忆重巩固 / 艾宾浩斯遗忘
#      压抑-反弹 / 隐压雪崩 / 信任容量腐蚀 / 兴奋唤醒
#      动态粘滞度 / 心理时间 / 能量疲劳代谢 / 虚拟时钟
#
#    V8.0 新增（通用心理构成，非自设）：
#      · 心境层（mood）——慢变量背景情绪，调制认知评估
#      · 羞耻维度——区别于愧疚的自我意识情绪（"我坏"vs"我做错"）
#      · 自尊动态——基于社会反馈的自我价值感，调制归因与情绪反应
#      · 睡眠/梦境加工——REM情绪记忆固化 + 恐惧消退 + 睡眠债
#      · 预期系统——希望/焦虑/失望，让 agent 有能力感受未来
#      · 认知失调——信念-行为冲突的自我调节
#      · 防御机制扩展——否认/合理化/置换（超越单纯的压抑）
#
#    拟人行为直观理解：
#      你骂它 → 当场愤怒拉满。
#      你不说话 → 它自己会慢慢平复；几小时后你再来，它已经冷静但可能带点疏离。
#      你骂太狠 → 留下创伤（trauma），下次类似场景会过激反应，且慢愈合。
#      你一直冷暴力 → 信任容量被腐蚀（max_trust 下降），以后再怎么夸也难回到最初。
#      你给它时间休息 → 能量恢复、疲劳下降、压抑泄放。
#      它睡了一觉 → 噩梦可能让创伤消退，也可能让焦虑泛化。
#      你许了诺又反悔 → 预期落空产生失望，比没有预期更伤人。
#      你做了一件背叛自己价值观的事 → 认知失调产生内在紧张。
#      低自尊的它 → 把成功归因于运气，把失败归因于自己。
# ================================================================
@dataclass
class SPLPureCoreV7_3:  # 类名保持兼容

    # ---------- 基础生理/心理参数 ----------
    psychological_resilience: float = 0.5          # 心理韧性 [0,1]
    energy: float = 100.0                          # 生理能量 [0,100]
    affinity: float = 0.5                          # 对外亲和基线
    last_time: float = field(default_factory=time.time)
    _clock_override: Optional[float] = None        # 测试/回放用虚拟时钟

    # ---------- 8 维情绪流体（连续状态） ----------
    # V8.0: 新增"羞耻"——自我意识情绪，区别于"愧疚"（行为层面）
    fluid: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2,
        "愧疚": 0.0, "羞耻": 0.0
    })
    fluid_target: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2,
        "愧疚": 0.0, "羞耻": 0.0
    })
    fluid_baseline: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2,
        "愧疚": 0.0, "羞耻": 0.0
    })

    # ---------- V8.0 心境层（慢变量背景情绪） ----------
    # 心境不是对事件的瞬时反应，而是数小时到数天尺度累积的情绪基调。
    # 心境调制认知评估——心情好时威胁不像威胁，心情差时夸奖也像讽刺。
    # 不同于 fluid（秒-分钟级），mood 的惯性极大。
    mood: Dict[str, float] = field(default_factory=lambda: {
        "愉悦": 0.5,    # pleasantness —— 感受有多好
        "紧张": 0.3,    # tension —— 有多紧绷
        "精力": 0.7,    # vigor —— 有多有劲（不是生理能量，是主观感受）
    })
    MOOD_INERTIA: float = 0.0003   # 心境变化极慢（~1小时半衰期）

    # ---------- V8.0 睡眠系统 ----------
    sleep_debt: float = 0.0                # 睡眠债 [0,1]，累积到 1.0 意味着极度缺觉
    SLEEP_NEED_RATE: float = 1.0 / 57600   # 每小时累积 1/16（16 小时醒着 → 满债）
    SLEEP_RECOVER_RATE: float = 0.25       # 每小时睡眠清除的债（4 小时睡饱）
    DREAM_EMOTION_DECAY: float = 0.15      # 梦中对记忆情绪电荷的衰减率
    DREAM_FEAR_EXTINCTION: float = 0.08    # 睡眠中恐惧消退率
    DREAM_TRAUMA_HEAL_BOOST: float = 3.0   # 睡眠时创伤愈合加速倍率
    last_sleep_time: float = 0.0

    # ---------- V8.0 自尊系统 ----------
    # 自尊是对自我价值的整体评估，缓慢波动。
    # 它调制归因方式（成功是谁的功劳？失败是谁的错？）
    # 也调制情绪反应的强度（低自尊者更容易被伤害）。
    self_esteem: float = 0.5               # 自尊 [0,1]，0.5 为中性基线
    SELF_ESTEEM_INERTIA: float = 0.002     # 自尊变化惯性（极慢）
    SELF_ESTEEM_UPDATE_RATE: float = 0.03  # 每次事件后自尊的修正率

    # ---------- V8.0 预期系统 ----------
    # 人类不是纯反应式的——我们会对未来建立预期。
    # 预期落空（失望）和预期兑现（安心/喜悦放大）是关键的心理事件。
    # expected_events: {event_id: {"valence": float, "confidence": float, "time": float}}
    expected_events: Dict[str, Dict[str, float]] = field(default_factory=dict)
    EXPECTATION_DECAY: float = 0.0001       # 预期的自然衰减（太久没兑现就忘了）
    SURPRISE_POSITIVE_BOOST: float = 0.4    # 正向惊喜增益（超出预期→喜悦加成）
    SURPRISE_NEGATIVE_BOOST: float = 0.5    # 负向惊喜增益（期望落空→更痛）

    # ---------- V8.0 认知失调 ----------
    # 当行为与信念冲突时，产生内在不适（失调张力）。
    # 失调可以通过改变信念、合理化行为、或最小化重要性来消解。
    cognitive_dissonance: float = 0.0       # 当前失调水平 [0,1]
    DISSONANCE_THRESHOLD: float = 0.4       # 超过此阈值开始主动消解
    DISSONANCE_DECAY: float = 0.005         # 自然衰减（随时间合理化）

    # ---------- V8.0 扩展防御机制 ----------
    denial_load: float = 0.0                # 否认仓（类似于压抑仓，但更原始）
    DENIAL_THRESHOLD: float = 1.2           # 否认过载→现实侵入
    DENIAL_DRAIN: float = 0.015             # 否认自然泄放
    DENIAL_BURST_COOLDOWN: float = 40.0     # 否认破裂冷却
    denial_burst_cd: float = 0.0
    rationalization_load: float = 0.0       # 合理化仓（"其实也没那么糟"）
    RATIONALIZE_DRAIN: float = 0.03         # 合理化会随时间被接受

    # ---------- 创伤节点（离散 SPL 节点） ----------
    trauma_state: Dict[str, float] = field(default_factory=dict)
    TRAUMA_HEAL_RATE: float = 0.003
    TRAUMA_BIAS: float = 0.35

    # ---------- 记忆痕迹 + 艾宾浩斯遗忘曲线 ----------
    memory_traces: List[Dict[str, Any]] = field(default_factory=list)
    MAX_MEMORY_TRACES: int = 64
    forgetting_rate: float = 0.01
    trace_importance_threshold: float = 0.05
    RECONSOL_RADIUS: float = 0.4
    SAFETY_THRESHOLD: float = 0.3

    # ---------- 压抑-反弹 ----------
    suppression_load: float = 0.0
    SUPPRESSION_THRESHOLD: float = 1.5
    SUPPRESSION_DRAIN: float = 0.02
    SUPPRESSION_BURST_COOLDOWN: float = 30.0
    suppression_burst_cd: float = 0.0
    _suppressing_negativity: bool = False

    # ---------- 隐压雪崩 ----------
    latent_pressure: float = 0.0
    LATENT_THRESHOLD: float = 2.0
    LATENT_DRAIN: float = 0.01
    LATENT_COOLDOWN: float = 60.0
    avalanche_cd: float = 0.0

    # ---------- 信任容量腐蚀 ----------
    max_trust: float = 1.0
    TRUST_ERODE: float = 0.92
    TRUST_RECOVER: float = 0.0005

    # ---------- 粘滞度 / 心理时间 ----------
    dynamic_viscosity: float = 0.1
    VISC_BASE: float = 0.1
    VISC_TENSION_K: float = 0.3
    VISC_FATIGUE_K: float = 0.2
    psy_dilation: float = 1.0
    time_compress_base: float = 0.0

    # ---------- 兴奋/唤醒（元参数） ----------
    excitation: float = 0.3
    EXCITATION_BASELINE: float = 0.3
    EXCITATION_NOVELTY_GAIN: float = 0.12
    EXCITATION_SALIENCE_BOOST: float = 0.35
    EXCITATION_DECAY: float = 0.025
    EXCITATION_BOREDOM_THRESHOLD: float = 0.1
    EXCITATION_MAX: float = 1.0

    # ---------- 能量 / 疲劳 ----------
    ENERGY_RECOVER: float = 1.5
    ENERGY_EVENT_COST: float = 1.5
    ENERGY_MIN: float = 0.0
    ENERGY_MAX: float = 100.0
    fatigue: float = 0.0
    FATIGUE_RECOVER: float = 0.05

    last_perceived: Dict[str, float] = field(default_factory=dict)

    # ==================================================================
    # 时钟：支持虚拟时间注入（测试/回放必用）
    # ==================================================================
    def _now(self) -> float:
        if self._clock_override is not None:
            return self._clock_override
        return time.time()

    def set_clock(self, t: Optional[float]):
        """注入虚拟时间戳；传 None 恢复真实时钟。"""
        self._clock_override = t

    def advance_clock(self, dt: float):
        """虚拟时钟前推 dt 秒。"""
        if self._clock_override is None:
            self._clock_override = time.time()
        self._clock_override += dt

    # ==================================================================
    # 公共入口 1：事件驱动
    # ==================================================================
    def process_vector(self, vector: Dict[str, float], raw_intensity: float = 1.0,
                       event_id: str = ""):
        """
        处理一个内感受向量。

        Args:
            vector: 内感受向量 {threat, belonging, autonomy, fatigue, shame_trigger}
            raw_intensity: 原始强度
            event_id: 可选事件标识，用于匹配预期（trigger 预期系统的 surprise 计算）
        """
        self._advance_time()

        # V8.0: 预期匹配——在认知增益之前计算 surprise
        surprise = 0.0
        if event_id and event_id in self.expected_events:
            surprise = self._compute_surprise(event_id, vector, raw_intensity)

        # 兴奋先于认知增益更新
        self._excitation_on_event(vector, raw_intensity)

        perceived = self._core_appraisal_gain(vector)

        # V8.0: surprise 调制 perceived vector
        if surprise != 0.0:
            perceived = self._apply_surprise(perceived, surprise)

        self.last_perceived = dict(perceived)

        if abs(perceived.get("threat", 0.0)) > 0.2 or abs(perceived.get("belonging", 0.0)) > 0.3:
            self._memory_reconsolidation(perceived)

        threat = perceived.get("threat", 0.0)
        threat_thr = 0.4 * (1.0 - self.psychological_resilience)
        if threat > threat_thr:
            self._apply_trauma("threat", threat - threat_thr)
        if perceived.get("belonging", 0.0) < -0.4 and threat > 0.3:
            self._apply_trauma("betrayal", abs(perceived["belonging"]) * threat)

        if perceived.get("belonging", 0.0) < -0.3:
            self._erode_trust(abs(perceived["belonging"]))

        self._latent_accumulate(perceived)
        self._vector_to_fluid(perceived)

        # V8.0: 自尊更新（在社会反馈事件后）
        self._update_self_esteem(perceived)

        # V8.0: 认知失调处理
        self._dissonance_dynamics(perceived)

        # V8.0: 扩展防御（先否认→再合理化→最后压抑——层级递进）
        self._defense_hierarchy(perceived)

        # 心境更新
        self._update_mood()

        self._update_dynamic_viscosity()
        self._fluid_dynamics(dt=self._psychological_dt_for(0.8))

        self._fluid_to_system_feedback()
        self._energy_on_event(perceived, raw_intensity)
        self.fatigue = max(0.0, min(1.0,
            self.fatigue + perceived.get("fatigue", 0.0) * 0.5))
        self.time_compress_base = max(0.0, self.time_compress_base * 0.95)

        self.last_time = self._now()

    # ==================================================================
    # 公共入口 2：空转 / 独处时间
    # ==================================================================
    def idle(self, seconds: float):
        """显式推进 seconds 秒"什么都没发生"的时间。"""
        if seconds <= 0:
            return
        if self._clock_override is not None:
            self._clock_override += seconds
        else:
            self.last_time -= seconds
        self._advance_time()

    def process_event(self, event: str, intensity: float = 1.0):
        """便利方法：map_event + process_vector。"""
        self.process_vector(NarrativeMapper.map_event(event, intensity), intensity)

    # ==================================================================
    # V8.0 公共入口 3：睡眠
    # ==================================================================
    def sleep(self, hours: float):
        """
        睡眠 hours 小时。

        睡眠期间发生：
        1. 睡眠债清除
        2. 梦境情绪加工——记忆的情绪电荷衰减，但事实内容保留
        3. 恐惧消退——在安全环境中重演威胁记忆
        4. 创伤愈合加速——睡眠是最好的心理修复
        5. 心境重置——睡醒后愉悦回升、紧张下降
        6. 能量完全恢复
        """
        if hours <= 0:
            return
        seconds = hours * 3600.0

        # 推进时钟
        if self._clock_override is not None:
            self._clock_override += seconds
        else:
            self.last_time -= seconds

        # 先结算睡眠前的连续过程
        self._advance_time()

        # ── 梦境情绪加工 ──
        dream_cycles = max(1, int(hours * 1.5))  # ~90分钟一个睡眠周期
        for _ in range(dream_cycles):
            self._dream_process()

        # ── 睡眠债清除 ──
        self.sleep_debt = max(0.0, self.sleep_debt - self.SLEEP_RECOVER_RATE * hours)
        self.last_sleep_time = self._now()

        # ── 心境重置 ──
        self.mood["愉悦"] = min(0.9, self.mood["愉悦"] + 0.15 * hours)
        self.mood["紧张"] = max(0.05, self.mood["紧张"] - 0.12 * hours)
        self.mood["精力"] = min(1.0, self.mood["精力"] + 0.2 * hours)

        # ── 能量完全恢复 ──
        self.energy = self.ENERGY_MAX
        self.fatigue = max(0.0, self.fatigue - 0.5 * hours)

        # ── 睡眠中创伤加速愈合 ──
        self._heal_traumas(seconds * self.DREAM_TRAUMA_HEAL_BOOST)

        # ── 睡眠后意识重新上线：更新心境和粘滞度 ──
        self._update_mood()
        self._update_dynamic_viscosity()

    # ==================================================================
    # V8.0 公共入口 4：设定预期
    # ==================================================================
    def expect(self, event_id: str, valence: float, confidence: float = 0.5):
        """
        建立一个对未来事件的预期。

        Args:
            event_id: 事件标识（与 process_vector 的 event_id 匹配）
            valence: 预期效价 [-1, 1]（正向=期待好事，负向=担心坏事）
            confidence: 确信度 [0, 1]
        """
        self.expected_events[event_id] = {
            "valence": max(-1.0, min(1.0, valence)),
            "confidence": max(0.0, min(1.0, confidence)),
            "time": self._now(),
            "age": 0.0,
        }

    # ==================================================================
    # V8.0 公共入口 5：触发认知失调
    # ==================================================================
    def induce_dissonance(self, magnitude: float, belief_domain: str = ""):
        """
        当 agent 做了与自身信念/价值观相悖的行为时调用。

        Args:
            magnitude: 失调强度 [0, 1]
            belief_domain: 冲突的信念领域（如 "诚实"、"忠诚"）
        """
        self.cognitive_dissonance = min(1.0, self.cognitive_dissonance + magnitude)
        # 失调立即表现为内在张力
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + magnitude * 0.4)
        self.fluid["愧疚"] = min(1.0, self.fluid["愧疚"] + magnitude * 0.3)
        # 失调消耗能量
        self.energy = max(self.ENERGY_MIN, self.energy - magnitude * 5.0)

    # ==================================================================
    # 快照：便于外部观察
    # ==================================================================
    def snapshot(self) -> Dict[str, Any]:
        return {
            "fluid": dict(self.fluid),
            "mood": dict(self.mood),
            "self_esteem": self.self_esteem,
            "energy": self.energy,
            "fatigue": self.fatigue,
            "excitation": self.excitation,
            "max_trust": self.max_trust,
            "suppression_load": self.suppression_load,
            "denial_load": self.denial_load,
            "latent_pressure": self.latent_pressure,
            "cognitive_dissonance": self.cognitive_dissonance,
            "sleep_debt": self.sleep_debt,
            "trauma": dict(self.trauma_state),
            "memory_count": len(self.memory_traces),
            "expected_count": len(self.expected_events),
            "last_perceived": dict(self.last_perceived),
        }

    # ==================================================================
    # 懒时间推进：结算 Δt 内所有连续过程
    # ==================================================================
    def _advance_time(self):
        now = self._now()
        dt = now - self.last_time
        if dt <= 0:
            self.last_time = now
            return
        dt = min(dt, 86400.0)  # 单步 24h 上限

        # V8.0: 积累睡眠债
        self.sleep_debt = min(1.0, self.sleep_debt + self.SLEEP_NEED_RATE * dt)

        # V8.0: 睡眠债影响认知——缺觉时一切更糟
        # （不直接修改 fluid，而是在 _core_appraisal_gain 中生效）

        # V8.0: 预期衰减（太久没兑现的预期自动消失）
        self._decay_expectations(dt)

        self._rebuild_fluid_target()
        self._update_dynamic_viscosity()
        self._fluid_dynamics(dt=self._psychological_dt_for(dt))
        self._forget_over(dt)
        self._energy_idle(dt)
        self._excitation_decay(dt)
        self._check_boredom(dt)
        self.suppression_load = max(0.0, self.suppression_load - self.SUPPRESSION_DRAIN * dt)
        self.latent_pressure = max(0.0, self.latent_pressure - self.LATENT_DRAIN * dt)
        # V8.0: 否认/合理化自然衰减
        self.denial_load = max(0.0, self.denial_load - self.DENIAL_DRAIN * dt)
        self.rationalization_load = max(0.0, self.rationalization_load - self.RATIONALIZE_DRAIN * dt)
        # V8.0: 认知失调自然衰减
        self.cognitive_dissonance = max(0.0, self.cognitive_dissonance - self.DISSONANCE_DECAY * dt)
        self._heal_traumas(dt)
        self._recover_trust(dt)
        self.suppression_burst_cd = max(0.0, self.suppression_burst_cd - dt)
        self.avalanche_cd = max(0.0, self.avalanche_cd - dt)
        self.denial_burst_cd = max(0.0, self.denial_burst_cd - dt)
        self.time_compress_base *= (0.95 ** max(0.0, min(dt, 10.0)))
        if self.time_compress_base < 1e-4:
            self.time_compress_base = 0.0
        self._fluid_to_system_feedback()
        self.fatigue = max(0.0, self.fatigue - self.FATIGUE_RECOVER * dt)
        # V8.0: 心境随时间缓慢漂移
        self._update_mood()

        self.last_time = now

    # ==================================================================
    # 1. 认知增益（V8.0: 加入心境、自尊、睡眠债调制）
    # ==================================================================
    def _core_appraisal_gain(self, v: Dict[str, float]) -> Dict[str, float]:
        out = dict(v)
        energy_factor = self.energy / 100.0
        tension = self.fluid["张力"]
        fear = self.fluid["恐惧"]
        trust = min(self.fluid["信任"], self.max_trust)

        # 唤醒乘数
        arousal_mult = 1.0 + self.excitation * 0.6

        # ── V8.0 心境调制 ──
        # 心情好 → 威胁感知减弱、归属感增强
        # 心情差 → 威胁感知放大、归属感打折
        mood_pleasantness = self.mood["愉悦"]
        mood_mod = 1.0 + (mood_pleasantness - 0.5) * 0.5  # 0.75~1.25 range

        # ── V8.0 自尊调制 ──
        # 低自尊 → threat 放大（"果然又是冲我来的"）
        # 低自尊 → 正向 belonging 打折（"他们只是客气而已"）
        esteem_threat_mod = 1.0 + (0.5 - self.self_esteem) * 0.8  # 0.6~1.4
        esteem_belonging_pos_mod = 0.6 + self.self_esteem * 0.8     # 0.6~1.4

        # ── V8.0 睡眠债调制 ──
        # 缺觉 → 所有负面信号放大、正面信号减弱、能量感知下降
        sleep_mod_neg = 1.0 + self.sleep_debt * 0.5     # 1.0~1.5
        sleep_mod_pos = 1.0 - self.sleep_debt * 0.3     # 0.7~1.0

        for k in out:
            base_mod = (0.4 + 0.6 * energy_factor) * arousal_mult * mood_mod
            out[k] *= base_mod

        if out.get("threat", 0.0) > 0:
            out["threat"] *= (1.0 + 1.5 * tension * fear) * esteem_threat_mod * sleep_mod_neg
        if "threat" in self.trauma_state and out.get("threat", 0.0) > 0:
            out["threat"] *= 1.0 + self.trauma_state["threat"]
        if "betrayal" in self.trauma_state and out.get("belonging", 0.0) < 0:
            out["belonging"] *= 1.0 + self.trauma_state["betrayal"]
        if out.get("belonging", 0.0) < 0:
            out["belonging"] *= (1.0 - 0.4 * trust) * sleep_mod_neg
        if out.get("belonging", 0.0) > 0:
            out["belonging"] *= (1.0 - 0.3 * self.fatigue) * esteem_belonging_pos_mod * sleep_mod_pos
        return out

    # ==================================================================
    # 2. 记忆重巩固
    # ==================================================================
    @staticmethod
    def _vec_sim(a: Dict[str, float], b: Dict[str, float]) -> float:
        keys = set(a) | set(b)
        if not keys:
            return 0.0
        dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
        na = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in keys))
        nb = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in keys))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def _memory_reconsolidation(self, v: Dict[str, float]):
        valence = v.get("belonging", 0.0) - v.get("threat", 0.0)
        intensity = math.sqrt(sum(x * x for x in v.values()))
        trust = min(self.fluid["信任"], self.max_trust)
        fear = self.fluid["恐惧"]
        safety = trust * (1.0 - fear)

        best_idx, best_sim = -1, 0.0
        for i, t in enumerate(self.memory_traces):
            sim = self._vec_sim(v, t["vector"])
            if sim > best_sim:
                best_sim, best_idx = sim, i

        now = self._now()
        if best_idx >= 0 and best_sim > (1.0 - self.RECONSOL_RADIUS):
            tr = self.memory_traces[best_idx]
            if safety > self.SAFETY_THRESHOLD:
                tr["strength"] *= 0.85
            else:
                tr["strength"] = min(1.0, tr["strength"] + intensity * 0.2)
            tr["timestamp"] = now
            tr["age"] = 0.0
            tr["count"] = tr.get("count", 1) + 1
        else:
            trace = {
                "vector": dict(v),
                "strength": min(1.0, intensity),
                "valence": valence,
                "timestamp": now,
                "age": 0.0,
                "count": 1,
            }
            self.memory_traces.append(trace)
            if len(self.memory_traces) > self.MAX_MEMORY_TRACES:
                self.memory_traces.sort(
                    key=lambda t: t["strength"] * (1.0 + math.log1p(t.get("count", 1))))
                self.memory_traces.pop(0)

    # ==================================================================
    # 3. 创伤
    # ==================================================================
    def _apply_trauma(self, key: str, magnitude: float):
        cur = self.trauma_state.get(key, 0.0)
        gain = magnitude * (1.0 - self.psychological_resilience) * 0.7
        self.trauma_state[key] = min(1.0, cur + gain)

    def _heal_traumas(self, dt: float):
        rate = self.TRAUMA_HEAL_RATE * (0.3 + self.psychological_resilience) * dt
        healed = []
        for k, v in list(self.trauma_state.items()):
            nv = v - rate
            if nv <= 0.01:
                healed.append(k)
            else:
                self.trauma_state[k] = nv
        for k in healed:
            del self.trauma_state[k]

    # ==================================================================
    # 4. 信任容量腐蚀 & 恢复
    # ==================================================================
    def _erode_trust(self, magnitude: float):
        factor = 1.0 - (1.0 - self.TRUST_ERODE) * min(1.0, magnitude)
        self.max_trust = max(0.1, self.max_trust * factor)

    def _recover_trust(self, dt: float):
        if self.max_trust < 1.0:
            recover = self.TRUST_RECOVER * dt * (1.01 - self.max_trust)
            self.max_trust = min(1.0, self.max_trust + recover)

    # ==================================================================
    # 5. 隐压累积 + 雪崩
    # ==================================================================
    def _latent_accumulate(self, v: Dict[str, float]):
        neg = max(0.0, -v.get("belonging", 0.0)) + max(0.0, v.get("threat", 0.0))
        self.latent_pressure += neg * 0.4
        if self.latent_pressure >= self.LATENT_THRESHOLD and self.avalanche_cd <= 0:
            self._trigger_avalanche()

    def _trigger_avalanche(self):
        self.avalanche_cd = self.LATENT_COOLDOWN
        overflow = self.latent_pressure - self.LATENT_THRESHOLD + 0.5
        self.latent_pressure = 0.3
        self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + overflow * 0.5)
        self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + overflow * 0.3)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + overflow * 0.3)
        self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + overflow * 0.2)
        self.fluid["信任"] = max(0.0, self.fluid["信任"] - overflow * 0.3)
        self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - overflow * 0.3)
        self.energy = max(self.ENERGY_MIN, self.energy - overflow * 10)
        self.time_compress_base = min(1.0, self.time_compress_base + 0.5)

    # ==================================================================
    # 6. 向量 → 流体瞬时映射（V8.0: 加入羞耻路径）
    # ==================================================================
    def _vector_to_fluid(self, v: Dict[str, float]):
        b = v.get("belonging", 0.0)
        t = v.get("threat", 0.0)
        a = v.get("autonomy", 0.0)
        f = v.get("fatigue", 0.0)
        s = v.get("shame_trigger", 0.0)  # V8.0: 羞耻触发器

        # ── V8.0 羞耻路径 ──
        # 羞耻是"我这个人有问题"，由自我相关负面评价触发
        # 与愧疚不同——愧疚是"我做的事有问题"
        if s > 0:
            self.fluid["羞耻"] = min(1.0, self.fluid["羞耻"] + s * 0.7)
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + s * 0.3)
            # 羞耻让人退缩（降低愤怒，增加恐惧和疏离）
            self.fluid["愤怒"] = max(0.0, self.fluid["愤怒"] - s * 0.3)
            self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + s * 0.25)
        # 负向归属 + 低自尊 → 更容易产生羞耻而非愤怒
        elif b < -0.3 and self.self_esteem < 0.35:
            shame_leak = (-b) * 0.3 * (0.5 - self.self_esteem)
            self.fluid["羞耻"] = min(1.0, self.fluid["羞耻"] + shame_leak)
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + (-b) * 0.4)  # 愤怒减少了
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + (-b) * 0.5)
            self.fluid["愧疚"] = min(1.0, self.fluid["愧疚"] + (-b) * 0.2)
        # 负向归属（标准路径）
        elif b < 0:
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + (-b) * 0.7)
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + (-b) * 0.4)
            self.fluid["愧疚"] = min(1.0, self.fluid["愧疚"] + (-b) * 0.15)
            if self.psychological_resilience > 0.6:
                self.fluid["张力"] = min(1.0, self.fluid["张力"] + (-b) * 0.3)
                self.fluid["愤怒"] *= 0.8
        # 正向归属 → 喜悦/信任，愤怒/疏离/羞耻回落
        if b > 0:
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + b * 0.6)
            self.fluid["信任"] = min(self.max_trust, self.fluid["信任"] + b * 0.25)
            self.fluid["愤怒"] = max(0.0, self.fluid["愤怒"] - b * 0.4)
            self.fluid["疏离"] = max(0.0, self.fluid["疏离"] - b * 0.3)
            self.fluid["羞耻"] = max(0.0, self.fluid["羞耻"] - b * 0.3)
        # 威胁 → 恐惧/张力
        if t > 0:
            self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + t * 0.8)
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + t * 0.6)
            self.fluid["信任"] = max(0.0, self.fluid["信任"] - t * 0.2)
        # 自主 → 喜悦
        if a > 0:
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + a * 0.3)
        # 疲劳 → 削减喜悦、增加张力
        if f > 0:
            self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - f * 0.3)
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + f * 0.2)

        # 所有维度夹紧
        self.fluid["信任"] = min(self.fluid["信任"], self.max_trust)
        for k in self.fluid:
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))

        # 兴奋调制
        if self.excitation > 0.5:
            extra = (self.excitation - 0.5) * 0.4
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + extra * max(0.0, b))
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + extra * max(0.0, -b))
            self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + extra * max(0.0, t))
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + extra * max(0.0, t, -b) * 0.5)

    # ==================================================================
    # 7. 压抑动力学（保持不变）
    # ==================================================================
    def _suppression_dynamics(self, v: Dict[str, float]):
        neg = (max(0.0, self.fluid["愤怒"])
               + max(0.0, self.fluid["恐惧"])
               + max(0.0, self.fluid["疏离"]))
        will_to_suppress = (self.energy / 100.0) * (0.3 + self.psychological_resilience)
        suppressed_here = neg * will_to_suppress * 0.5
        if suppressed_here > 0.05:
            self._suppressing_negativity = True
            self.suppression_load += suppressed_here
            self.fluid["愤怒"] *= (1.0 - will_to_suppress * 0.6)
            self.fluid["恐惧"] *= (1.0 - will_to_suppress * 0.4)
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + suppressed_here * 0.3)
        else:
            self._suppressing_negativity = False

        if self.suppression_load >= self.SUPPRESSION_THRESHOLD and self.suppression_burst_cd <= 0:
            self._trigger_burst()

    def _trigger_burst(self):
        self.suppression_burst_cd = self.SUPPRESSION_BURST_COOLDOWN
        load = self.suppression_load
        self.suppression_load = 0.0
        self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + load * 0.6)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + load * 0.4)
        self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - load * 0.3)
        self.fluid["信任"] = max(0.0, self.fluid["信任"] - load * 0.2)
        self.energy = max(self.ENERGY_MIN, self.energy - load * 8)
        self.time_compress_base = min(1.0, self.time_compress_base + 0.7)
        self._apply_trauma("threat", load * 0.1)

    # ==================================================================
    # 8. 动态粘滞度 / 心理时间
    # ==================================================================
    def _update_dynamic_viscosity(self):
        base = self.VISC_BASE
        self.dynamic_viscosity = (base
                                  + self.VISC_TENSION_K * self.fluid["张力"]
                                  + self.VISC_FATIGUE_K * self.fatigue
                                  + self.mood["紧张"] * 0.15     # V8.0: 心境紧张加剧粘滞
                                  + self.sleep_debt * 0.1)        # V8.0: 缺觉让情绪更钝
        self.dynamic_viscosity -= self.excitation * 0.08
        self.dynamic_viscosity = max(0.02, min(1.5, self.dynamic_viscosity))
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0

    def _psychological_dt_for(self, real_dt: float) -> float:
        return real_dt * self.psy_dilation / (0.1 + self.dynamic_viscosity)

    def _psychological_dt(self) -> float:
        return self._psychological_dt_for(1.0)

    # ==================================================================
    # 9. 流体连续松弛
    # ==================================================================
    def _fluid_dynamics(self, dt: float):
        k = 1.0 / (0.2 + self.dynamic_viscosity * 3.0)
        alpha = 1.0 - math.exp(-k * max(0.0, dt))
        alpha = max(0.0, min(1.0, alpha))
        for key in self.fluid:
            tgt = self.fluid_target.get(key, self.fluid[key])
            if key == "信任":
                tgt = min(tgt, self.max_trust)
            self.fluid[key] += (tgt - self.fluid[key]) * alpha
            self.fluid[key] = max(0.0, min(1.0, self.fluid[key]))

    # ==================================================================
    # target 重建：基线 + 创伤牵引 + 记忆共振 + 心境牵引
    # ==================================================================
    def _rebuild_fluid_target(self):
        for k, v in self.fluid_baseline.items():
            self.fluid_target[k] = v

        # ── V8.0 心境牵引 target ──
        # 心境好 → 喜悦 target 抬高、愤怒/疏离 target 压低
        mp = self.mood["愉悦"]
        self.fluid_target["喜悦"] = min(1.0, self.fluid_target["喜悦"] + (mp - 0.5) * 0.3)
        self.fluid_target["愤怒"] = max(0.0, self.fluid_target["愤怒"] - (mp - 0.5) * 0.15)
        self.fluid_target["疏离"] = max(0.0, self.fluid_target["疏离"] - (mp - 0.5) * 0.15)

        # ── V8.0 自尊牵引 target ──
        # 低自尊 → 羞耻 target 抬高
        self.fluid_target["羞耻"] = max(0.0, self.fluid_target["羞耻"] +
                                        (0.5 - self.self_esteem) * 0.2)

        # ── V8.0 睡眠债牵引 target ──
        # 缺觉 → 张力 + 恐惧 target 抬高，喜悦 target 压低
        sd = self.sleep_debt
        self.fluid_target["张力"] = min(1.0, self.fluid_target["张力"] + sd * 0.25)
        self.fluid_target["恐惧"] = min(1.0, self.fluid_target["恐惧"] + sd * 0.15)
        self.fluid_target["喜悦"] = max(0.0, self.fluid_target["喜悦"] - sd * 0.2)

        # 创伤牵引
        if "threat" in self.trauma_state:
            w = self.trauma_state["threat"] * self.TRAUMA_BIAS
            self.fluid_target["恐惧"] = min(1.0, self.fluid_target["恐惧"] + w)
            self.fluid_target["张力"] = min(1.0, self.fluid_target["张力"] + w * 0.8)
            self.fluid_target["信任"] = max(0.0, self.fluid_target["信任"] - w * 0.5)
        if "betrayal" in self.trauma_state:
            w = self.trauma_state["betrayal"] * self.TRAUMA_BIAS
            self.fluid_target["疏离"] = min(1.0, self.fluid_target["疏离"] + w)
            self.fluid_target["信任"] = max(0.0, self.fluid_target["信任"] - w * 0.7)
            self.fluid_target["愤怒"] = min(1.0, self.fluid_target["愤怒"] + w * 0.3)

        # 记忆共振
        now = self._now()
        for tr in self.memory_traces:
            age = now - tr["timestamp"]
            weight = tr["strength"] * math.exp(-self.forgetting_rate * age / 20.0)
            if weight < 0.02:
                continue
            vec = tr["vector"]
            if vec.get("threat", 0.0) > 0:
                self.fluid_target["恐惧"] = min(1.0,
                    self.fluid_target["恐惧"] + weight * 0.1 * vec["threat"])
            if vec.get("belonging", 0.0) < 0:
                self.fluid_target["疏离"] = min(1.0,
                    self.fluid_target["疏离"] + weight * 0.1 * (-vec["belonging"]))
                self.fluid_target["信任"] = max(0.0,
                    self.fluid_target["信任"] - weight * 0.08 * (-vec["belonging"]))
            elif vec.get("belonging", 0.0) > 0:
                self.fluid_target["喜悦"] = min(1.0,
                    self.fluid_target["喜悦"] + weight * 0.1 * vec["belonging"])

        for k in self.fluid_target:
            self.fluid_target[k] = max(0.0, min(1.0, self.fluid_target[k]))

    # ==================================================================
    # 10. 流体 → 系统反馈
    # ==================================================================
    def _fluid_to_system_feedback(self):
        tension = self.fluid["张力"]
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0 + tension * 0.5
        guilt = self.fluid["愧疚"]
        if guilt > 0.3 and self.max_trust < 1.0:
            self.max_trust = min(1.0, self.max_trust + guilt * 0.0001)
        # V8.0: 羞耻 → 自尊被侵蚀
        shame = self.fluid.get("羞耻", 0.0)
        if shame > 0.4:
            self.self_esteem = max(0.1, self.self_esteem - shame * 0.0005)

    # ==================================================================
    # 11. 能量代谢
    # ==================================================================
    def _energy_on_event(self, v: Dict[str, float], raw_intensity: float):
        cost = self.ENERGY_EVENT_COST * raw_intensity
        if v.get("threat", 0.0) > 0.2 or v.get("belonging", 0.0) < -0.2:
            cost *= 1.8
        cost *= (1.0 + self.fluid["张力"])
        # V8.0: 认知失调额外消耗能量
        cost *= (1.0 + self.cognitive_dissonance * 0.5)
        self.energy = max(self.ENERGY_MIN, self.energy - cost)

    def _energy_idle(self, dt: float):
        recover = self.ENERGY_RECOVER * dt * (1.0 - 0.5 * self.fatigue)
        # V8.0: 睡眠债降低能量恢复效率
        recover *= (1.0 - self.sleep_debt * 0.4)
        self.energy = min(self.ENERGY_MAX, self.energy + recover)

    # ==================================================================
    # 12. 艾宾浩斯遗忘曲线
    # ==================================================================
    def _forget_over(self, dt: float):
        survivors = []
        now = self._now()
        for tr in self.memory_traces:
            age = now - tr["timestamp"]
            strength = tr["strength"] * math.exp(-self.forgetting_rate * age / 10.0)
            if strength > self.trace_importance_threshold:
                tr["strength"] = strength
                tr["age"] = age
                survivors.append(tr)
        self.memory_traces = survivors

    # ==================================================================
    # 13. 兴奋/唤醒系统
    # ==================================================================
    def _excitation_on_event(self, v: Dict[str, float], raw_intensity: float):
        novelty = raw_intensity * self.EXCITATION_NOVELTY_GAIN
        if abs(v.get("threat", 0.0)) > 0.5 or abs(v.get("belonging", 0.0)) > 0.5:
            novelty += raw_intensity * self.EXCITATION_SALIENCE_BOOST
        self.excitation = min(self.EXCITATION_MAX, self.excitation + novelty)

    def _excitation_decay(self, dt: float):
        if self.excitation > self.EXCITATION_BASELINE:
            self.excitation += (self.EXCITATION_BASELINE - self.excitation) * \
                              (1.0 - math.exp(-self.EXCITATION_DECAY * dt))
            if abs(self.excitation - self.EXCITATION_BASELINE) < 0.005:
                self.excitation = self.EXCITATION_BASELINE

    def _check_boredom(self, dt: float):
        if self.excitation < self.EXCITATION_BOREDOM_THRESHOLD:
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + 0.003 * dt / 60)
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + 0.002 * dt / 60)

    # ==================================================================
    # 14. V8.0 心境更新（慢变量）
    # ==================================================================
    def _update_mood(self):
        """
        心境是慢变量，由以下因素缓慢牵引：
        - 流体情绪的平均水平（持续愤怒 → 心境紧张上升）
        - 自尊（低自尊 → 心境愉悦下降）
        - 睡眠债（缺觉 → 心境精力下降、紧张上升）
        - 认知失调（内心冲突 → 心境紧张上升）

        惯性极大——MOOD_INERTIA 保证每步只微量移动。
        """
        # 目标心境
        target_pleasant = (self.fluid["喜悦"] * 0.4
                           - self.fluid["愤怒"] * 0.3
                           - self.fluid["恐惧"] * 0.25
                           - self.fluid["疏离"] * 0.2
                           - self.fluid["羞耻"] * 0.3
                           + self.self_esteem * 0.4
                           + 0.3)  # 中性基线偏移
        target_pleasant = max(0.0, min(1.0, target_pleasant))

        target_tension = (self.fluid["张力"] * 0.5
                          + self.fluid["恐惧"] * 0.3
                          + self.cognitive_dissonance * 0.3
                          + self.sleep_debt * 0.3
                          + 0.1)
        target_tension = max(0.0, min(1.0, target_tension))

        target_vigor = (1.0
                        - self.fatigue * 0.5
                        - self.sleep_debt * 0.6
                        - self.fluid["张力"] * 0.2
                        + self.self_esteem * 0.3)
        target_vigor = max(0.0, min(1.0, target_vigor))

        # 向目标缓慢移动
        alpha = self.MOOD_INERTIA
        self.mood["愉悦"] += (target_pleasant - self.mood["愉悦"]) * alpha
        self.mood["紧张"] += (target_tension - self.mood["紧张"]) * alpha
        self.mood["精力"] += (target_vigor - self.mood["精力"]) * alpha

    # ==================================================================
    # 15. V8.0 梦境加工
    # ==================================================================
    def _dream_process(self):
        """
        单个睡眠周期（~90 分钟）中的梦境情绪加工：

        1. 记忆情绪衰减——保留事实，降低情绪电荷
           （这就是为什么"睡一觉就觉得没那么严重了"）
        2. 恐惧消退——在安全的"梦中环境"重新暴露于威胁记忆，
           降低其威胁关联（Phelps 2004 的睡眠恐惧消退理论）
        3. 创伤愈合——在 REM 睡眠中，去甲肾上腺素水平极低，
           这是唯一能在无应激状态下重演创伤的窗口
        """
        # 记忆情绪衰减
        for tr in self.memory_traces:
            vec = tr["vector"]
            # 情绪电荷衰减，但事实结构保留
            for k in list(vec.keys()):
                if abs(vec[k]) > 0.05:
                    vec[k] *= (1.0 - self.DREAM_EMOTION_DECAY)

        # 恐惧消退：找到威胁类记忆，在安全环境中减弱
        for tr in self.memory_traces:
            if tr["vector"].get("threat", 0.0) > 0.1:
                # 低自尊者在梦中更难消退恐惧（反复噩梦）
                extinction = (self.DREAM_FEAR_EXTINCTION
                              * (0.4 + self.self_esteem * 1.2))
                tr["vector"]["threat"] *= (1.0 - extinction)
                tr["strength"] *= (1.0 - extinction * 0.5)

        # 创伤额外愈合
        self._heal_traumas(90.0 * 60.0 * self.DREAM_TRAUMA_HEAL_BOOST * 0.1)

    # ==================================================================
    # 16. V8.0 预期系统
    # ==================================================================
    def _compute_surprise(self, event_id: str, vector: Dict[str, float],
                          intensity: float) -> float:
        """
        计算预期与实际之间的 surprise 信号。

        返回值：surprise ∈ [-1, 1]
          > 0: 正向惊喜（比预期好）
          < 0: 负向惊喜/失望（比预期差）
        """
        exp = self.expected_events.pop(event_id)
        expected_valence = exp["valence"]
        confidence = exp["confidence"]

        # 从 vector 推断实际效价
        actual_valence = (vector.get("belonging", 0.0)
                          - vector.get("threat", 0.0)
                          + vector.get("autonomy", 0.0))

        # 标准化到 [-1, 1]
        actual_valence = max(-1.0, min(1.0, actual_valence))

        # surprise = (实际 - 预期) × 确信度
        # 越确信 → 落差越剧烈
        surprise = (actual_valence - expected_valence) * confidence

        # 预期时间跨度（预期越久远，落空越不意外）
        age = self._now() - exp.get("time", self._now())
        age_discount = math.exp(-0.00001 * age)  # ~1天半衰期
        surprise *= age_discount

        return max(-1.0, min(1.0, surprise))

    def _apply_surprise(self, perceived: Dict[str, float],
                        surprise: float) -> Dict[str, float]:
        """将 surprise 注入 perceived vector。"""
        out = dict(perceived)
        if surprise > 0.1:
            # 正向惊喜 → 喜悦加成、威胁减弱
            out["belonging"] = out.get("belonging", 0.0) + surprise * self.SURPRISE_POSITIVE_BOOST
            out["threat"] = out.get("threat", 0.0) - surprise * self.SURPRISE_POSITIVE_BOOST * 0.5
        elif surprise < -0.1:
            # 负向失望 → 威胁放大、归属感额外受损
            mag = abs(surprise)
            out["threat"] = out.get("threat", 0.0) + mag * self.SURPRISE_NEGATIVE_BOOST
            out["belonging"] = out.get("belonging", 0.0) - mag * self.SURPRISE_NEGATIVE_BOOST * 0.7
        return out

    def _decay_expectations(self, dt: float):
        """预期自然衰减——太久没兑现的预期会淡化。"""
        now = self._now()
        expired = []
        for eid, exp in self.expected_events.items():
            age = now - exp.get("time", now)
            # 超过 7 天的预期几乎消失，或信心随时间降低
            decay = self.EXPECTATION_DECAY * dt
            exp["confidence"] = max(0.0, exp["confidence"] - decay)
            if exp["confidence"] < 0.05:
                expired.append(eid)
        for eid in expired:
            del self.expected_events[eid]

    # ==================================================================
    # 17. V8.0 自尊动态
    # ==================================================================
    def _update_self_esteem(self, v: Dict[str, float]):
        """
        自尊根据社会反馈缓慢更新。

        归因逻辑（内隐的，不是显式的）：
        - 正向归属 → 自尊上升（"他们认可我，说明我有价值"）
        - 负向归属 → 自尊下降（"我被拒绝，说明我不够好"）
        - 低自尊放大负向、缩小正向（经典的归因偏差）
        - 高自尊放大正向、缩小负向

        自尊的惯性极大——不会因为一句话就崩塌或膨胀。
        """
        b = v.get("belonging", 0.0)
        t = v.get("threat", 0.0)
        a = v.get("autonomy", 0.0)

        # 计算此次事件的自尊冲击
        impact = 0.0
        if b > 0:
            # 成功/认可 → 自尊上升（但低自尊者不敢信）
            impact += b * self.SELF_ESTEEM_UPDATE_RATE * (0.3 + self.self_esteem * 1.4)
        if b < 0:
            # 拒绝/失败 → 自尊下降（低自尊者伤更深）
            impact -= abs(b) * self.SELF_ESTEEM_UPDATE_RATE * (1.5 - self.self_esteem)
        if a > 0:
            # 自主/掌控感 → 自尊上升
            impact += a * self.SELF_ESTEEM_UPDATE_RATE * 0.5
        if t > 0 and b < 0:
            # 威胁 + 被拒绝 → 自尊双倍打击（"危险的，还是我的错"）
            impact -= t * abs(b) * self.SELF_ESTEEM_UPDATE_RATE * 0.8

        # 缓慢更新
        self.self_esteem += impact * self.SELF_ESTEEM_INERTIA
        self.self_esteem = max(0.05, min(0.95, self.self_esteem))

    # ==================================================================
    # 18. V8.0 认知失调动力学
    # ==================================================================
    def _dissonance_dynamics(self, v: Dict[str, float]):
        """
        认知失调的自动消解尝试。

        当存在显著失调且当前没有更强刺激时：
        - 合理化（rationalization_load 上升）→ "其实也没那么糟"
        - 信念微调（自尊微调）→ "也许我的标准太严了"
        - 失调本身随时间衰减（遗忘/接受）
        """
        if self.cognitive_dissonance > self.DISSONANCE_THRESHOLD:
            # 高失调触发主动合理化
            rationalize_amount = self.cognitive_dissonance * 0.15
            self.rationalization_load = min(1.0, self.rationalization_load + rationalize_amount)
            self.cognitive_dissonance *= 0.85
            # 合理化消耗能量
            self.energy = max(self.ENERGY_MIN, self.energy - rationalize_amount * 2.0)
            # 合理化让人暂时舒服（张力下降）
            self.fluid["张力"] = max(0.0, self.fluid["张力"] - rationalize_amount * 0.2)

    # ==================================================================
    # 19. V8.0 防御机制层级
    # ==================================================================
    def _defense_hierarchy(self, v: Dict[str, float]):
        """
        防御机制的层级递进：

        层级 1: 否认（Denial）
          "这不可能"——直接拒绝接受威胁性信息。
          最原始的防御，消耗最小，但不可持续。
          否认过载 → 现实侵入（denial burst）。

        层级 2: 合理化（Rationalization）
          "其实也没那么糟"——给事件找一个能接受的理由。
          比否认成熟，但仍扭曲现实。

        层级 3: 压抑（Suppression）
          "我忍了"——承认但压下去。
          最成熟的防御，但负荷最大。

        正常流程：威胁 → 少量否认 + 合理化 → 剩余进入压抑
        高自尊者能更快跳过否认阶段。
        """
        threat = v.get("threat", 0.0)
        neg_belonging = max(0.0, -v.get("belonging", 0.0))
        total_neg = threat + neg_belonging

        if total_neg < 0.1:
            self._suppression_dynamics(v)
            return

        # 低自尊 → 更倾向否认（不敢面对）
        denial_tendency = 0.3 * (1.0 - self.self_esteem)

        # 层级 1: 否认
        denied = total_neg * denial_tendency
        if denied > 0.02:
            self.denial_load += denied
            # 否认成功 → 威胁感知暂时降低
            remaining_denial = 1.0 - denial_tendency
            v_modified = {
                k: (vv * remaining_denial if k in ("threat",) else vv)
                for k, vv in v.items()
            }
            if "belonging" in v_modified and v_modified["belonging"] < 0:
                v_modified["belonging"] *= remaining_denial
        else:
            v_modified = dict(v)

        # 否认过载 → 现实侵入
        if self.denial_load >= self.DENIAL_THRESHOLD and self.denial_burst_cd <= 0:
            self._trigger_denial_burst()

        # 层级 2: 合理化
        rationalize_tendency = 0.2
        remaining_neg = (v_modified.get("threat", 0.0)
                         + max(0.0, -v_modified.get("belonging", 0.0)))
        rationalized = remaining_neg * rationalize_tendency
        if rationalized > 0.02:
            self.rationalization_load = min(1.0, self.rationalization_load + rationalized)
            # 合理化让表面情绪更可控
            for k in v_modified:
                if k in ("threat",):
                    v_modified[k] *= (1.0 - rationalize_tendency)
                elif k == "belonging" and v_modified[k] < 0:
                    v_modified[k] *= (1.0 - rationalize_tendency * 0.5)

        # 层级 3: 压抑（原有系统处理剩余情绪）
        self._suppression_dynamics(v_modified)

    def _trigger_denial_burst(self):
        """否认过载 → 现实侵入。被否认的东西一次性涌回来。"""
        self.denial_burst_cd = self.DENIAL_BURST_COOLDOWN
        load = self.denial_load
        self.denial_load = 0.0
        # 现实感突然袭来
        self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + load * 0.7)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + load * 0.5)
        self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + load * 0.4)
        self.fluid["信任"] = max(0.0, self.fluid["信任"] - load * 0.3)
        self.energy = max(self.ENERGY_MIN, self.energy - load * 6)
        self.time_compress_base = min(1.0, self.time_compress_base + 0.5)

    # ==================================================================
    # 兼容旧名
    # ==================================================================
    def _apply_forgetting_curve(self):
        self._forget_over(1.0)

    def _update_time(self):
        self._advance_time()

    def _update_dynamic_viscosity_old(self):
        self._update_dynamic_viscosity()
