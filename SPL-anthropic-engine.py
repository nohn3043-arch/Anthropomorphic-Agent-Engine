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
# 2. SPL 纯净流体核心 V7.3
#    - 不认识任何具体事件，只认数字向量（threat / belonging / autonomy / fatigue）
#    - 懒时间推进（lazy Δt）：不后台 tick，每次公共入口按 wall-clock Δt 一次性结算
#    - 确定性：给定相同 (t, vector) 序列，输出完全可复现
#    - 可通过 set_clock/advance_clock 注入虚拟时钟，用于测试/回放
#
#    拟人行为直观理解：
#      你骂它 → 当场愤怒拉满。
#      你不说话 → 它自己会慢慢平复；几小时后你再来，它已经冷静但可能带点疏离。
#      你骂太狠 → 留下创伤（trauma），下次类似场景会过激反应，且慢愈合。
#      你一直冷暴力 → 信任容量被腐蚀（max_trust 下降），以后再怎么夸也难回到最初。
#      你给它时间休息 → 能量恢复、疲劳下降、压抑泄放。
# ================================================================
@dataclass
class SPLPureCoreV7_3:

    # ---------- 基础生理/心理参数 ----------
    psychological_resilience: float = 0.5          # 心理韧性 [0,1]
    energy: float = 100.0                          # 生理能量 [0,100]
    affinity: float = 0.5                          # 对外亲和基线
    last_time: float = field(default_factory=time.time)
    _clock_override: Optional[float] = None        # 测试/回放用虚拟时钟

    # ---------- 7 维情绪流体（连续状态） ----------
    fluid: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })
    fluid_target: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })
    fluid_baseline: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })

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
    # 兴奋不是情绪，是情绪的"音量旋钮"——控制多快、多猛、多上头。
    # 高兴奋 → 粘滞度压低、感知增益放大、情绪映射更极端。
    # 低兴奋 → 情绪平滑；长时间过低 → 触发无聊（张力/疏离自增）。
    excitation: float = 0.3                          # 当前唤醒水平 [0,1]
    EXCITATION_BASELINE: float = 0.3                 # 静息基线
    EXCITATION_NOVELTY_GAIN: float = 0.12            # 普适事件唤醒增量
    EXCITATION_SALIENCE_BOOST: float = 0.35          # 高强度事件额外唤醒
    EXCITATION_DECAY: float = 0.025                  # 自然衰减率（/s）
    EXCITATION_BOREDOM_THRESHOLD: float = 0.1        # 低于此 → 无聊
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
    def process_vector(self, vector: Dict[str, float], raw_intensity: float = 1.0):
        self._advance_time()

        # 兴奋先于认知增益更新——任何新刺激先"点燃"唤醒度，再被认知增益加工
        self._excitation_on_event(vector, raw_intensity)

        perceived = self._core_appraisal_gain(vector)
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
        self._suppression_dynamics(perceived)

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
        """显式推进 seconds 秒"什么都没发生"的时间。
        游戏 NPC 每帧 idle(frame_dt)；聊天机器人可不调，下一次 process_vector 自动补算。"""
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
    # 快照：便于外部观察
    # ==================================================================
    def snapshot(self) -> Dict[str, Any]:
        return {
            "fluid": dict(self.fluid),
            "energy": self.energy,
            "fatigue": self.fatigue,
            "excitation": self.excitation,
            "max_trust": self.max_trust,
            "suppression_load": self.suppression_load,
            "latent_pressure": self.latent_pressure,
            "trauma": dict(self.trauma_state),
            "memory_count": len(self.memory_traces),
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
        dt = min(dt, 86400.0)  # 单步 24h 上限，防跳时爆炸

        self._rebuild_fluid_target()
        self._update_dynamic_viscosity()
        self._fluid_dynamics(dt=self._psychological_dt_for(dt))
        self._forget_over(dt)
        self._energy_idle(dt)
        self._excitation_decay(dt)
        self._check_boredom(dt)
        self.suppression_load = max(0.0, self.suppression_load - self.SUPPRESSION_DRAIN * dt)
        self.latent_pressure = max(0.0, self.latent_pressure - self.LATENT_DRAIN * dt)
        self._heal_traumas(dt)
        self._recover_trust(dt)
        self.suppression_burst_cd = max(0.0, self.suppression_burst_cd - dt)
        self.avalanche_cd = max(0.0, self.avalanche_cd - dt)
        self.time_compress_base *= (0.95 ** max(0.0, min(dt, 10.0)))
        if self.time_compress_base < 1e-4:
            self.time_compress_base = 0.0
        self._fluid_to_system_feedback()
        self.fatigue = max(0.0, self.fatigue - self.FATIGUE_RECOVER * dt)

        self.last_time = now

    # ==================================================================
    # 1. 认知增益
    # ==================================================================
    def _core_appraisal_gain(self, v: Dict[str, float]) -> Dict[str, float]:
        out = dict(v)
        energy_factor = self.energy / 100.0
        tension = self.fluid["张力"]
        fear = self.fluid["恐惧"]
        trust = min(self.fluid["信任"], self.max_trust)

        # 唤醒乘数：高兴奋 → 所有输入信号被放大（"一惊一乍"）
        arousal_mult = 1.0 + self.excitation * 0.6

        for k in out:
            out[k] *= (0.4 + 0.6 * energy_factor) * arousal_mult
        if out.get("threat", 0.0) > 0:
            out["threat"] *= 1.0 + 1.5 * tension * fear
        if "threat" in self.trauma_state and out.get("threat", 0.0) > 0:
            out["threat"] *= 1.0 + self.trauma_state["threat"]
        if "betrayal" in self.trauma_state and out.get("belonging", 0.0) < 0:
            out["belonging"] *= 1.0 + self.trauma_state["betrayal"]
        if out.get("belonging", 0.0) < 0:
            out["belonging"] *= (1.0 - 0.4 * trust)
        if out.get("belonging", 0.0) > 0:
            out["belonging"] *= (1.0 - 0.3 * self.fatigue)
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
                tr["strength"] *= 0.85         # 安全环境：旧伤被疗愈
            else:
                tr["strength"] = min(1.0, tr["strength"] + intensity * 0.2)  # 不安全：加固
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
                # 淘汰：强度×log(次数) 最小的
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
        # 对数式慢恢复，永远回不到 1.0（被伤过就是被伤过）
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
        """隐压越过阈值 → 情绪全面失控（崩溃/暴怒/恐慌）。"""
        self.avalanche_cd = self.LATENT_COOLDOWN
        overflow = self.latent_pressure - self.LATENT_THRESHOLD + 0.5
        self.latent_pressure = 0.3
        # 把隐压全部倒进流体
        self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + overflow * 0.5)
        self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + overflow * 0.3)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + overflow * 0.3)
        self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + overflow * 0.2)
        self.fluid["信任"] = max(0.0, self.fluid["信任"] - overflow * 0.3)
        self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - overflow * 0.3)
        self.energy = max(self.ENERGY_MIN, self.energy - overflow * 10)
        self.time_compress_base = min(1.0, self.time_compress_base + 0.5)  # 主观时间变慢

    # ==================================================================
    # 6. 向量 → 流体瞬时映射
    # ==================================================================
    def _vector_to_fluid(self, v: Dict[str, float]):
        b = v.get("belonging", 0.0)
        t = v.get("threat", 0.0)
        a = v.get("autonomy", 0.0)
        f = v.get("fatigue", 0.0)

        # 负向归属 → 愤怒/疏离/愧疚
        if b < 0:
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + (-b) * 0.7)
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + (-b) * 0.4)
            self.fluid["愧疚"] = min(1.0, self.fluid["愧疚"] + (-b) * 0.15)
            # 高韧性的人会更少愤怒，更多张力
            if self.psychological_resilience > 0.6:
                self.fluid["张力"] = min(1.0, self.fluid["张力"] + (-b) * 0.3)
                self.fluid["愤怒"] *= 0.8
        # 正向归属 → 喜悦/信任，愤怒/疏离回落
        if b > 0:
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + b * 0.6)
            self.fluid["信任"] = min(self.max_trust, self.fluid["信任"] + b * 0.25)
            self.fluid["愤怒"] = max(0.0, self.fluid["愤怒"] - b * 0.4)
            self.fluid["疏离"] = max(0.0, self.fluid["疏离"] - b * 0.3)
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

        # 所有维度夹紧到 [0,1]（信任受 max_trust 约束）
        self.fluid["信任"] = min(self.fluid["信任"], self.max_trust)
        for k in self.fluid:
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))

        # 兴奋调制：高兴奋时情绪映射更极端——喜悦更浓，愤怒/恐惧/张力更烈
        if self.excitation > 0.5:
            extra = (self.excitation - 0.5) * 0.4
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + extra * max(0.0, b))
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + extra * max(0.0, -b))
            self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + extra * max(0.0, t))
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + extra * max(0.0, t, -b) * 0.5)

    # ==================================================================
    # 7. 压抑动力学
    # ==================================================================
    def _suppression_dynamics(self, v: Dict[str, float]):
        """
        高压力下个体会"硬压"负情绪——但压下去的东西会在 suppression_load 里累积。
        当 load 超阈值且不在冷却期 → 爆发（情绪决堤）。
        """
        # 当下负情绪总量
        neg = (max(0.0, self.fluid["愤怒"])
               + max(0.0, self.fluid["恐惧"])
               + max(0.0, self.fluid["疏离"]))
        # 高能量+高韧性的人更可能硬压（"忍了"）
        will_to_suppress = (self.energy / 100.0) * (0.3 + self.psychological_resilience)
        suppressed_here = neg * will_to_suppress * 0.5
        if suppressed_here > 0.05:
            self._suppressing_negativity = True
            self.suppression_load += suppressed_here
            # 压下去：表面情绪回落，转入仓里
            self.fluid["愤怒"] *= (1.0 - will_to_suppress * 0.6)
            self.fluid["恐惧"] *= (1.0 - will_to_suppress * 0.4)
            # 但张力上升（"憋得慌"）
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + suppressed_here * 0.3)
        else:
            self._suppressing_negativity = False

        # 爆发判定
        if self.suppression_load >= self.SUPPRESSION_THRESHOLD and self.suppression_burst_cd <= 0:
            self._trigger_burst()

    def _trigger_burst(self):
        """压抑过载 → 情绪决堤。"""
        self.suppression_burst_cd = self.SUPPRESSION_BURST_COOLDOWN
        load = self.suppression_load
        self.suppression_load = 0.0
        # 愤怒为主轴的爆发
        self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + load * 0.6)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + load * 0.4)
        self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - load * 0.3)
        self.fluid["信任"] = max(0.0, self.fluid["信任"] - load * 0.2)
        self.energy = max(self.ENERGY_MIN, self.energy - load * 8)
        self.time_compress_base = min(1.0, self.time_compress_base + 0.7)
        # 爆发后留痕：小创伤
        self._apply_trauma("threat", load * 0.1)

    # ==================================================================
    # 8. 动态粘滞度 / 心理时间
    # ==================================================================
    def _update_dynamic_viscosity(self):
        base = self.VISC_BASE
        # 张力/疲劳越高，越"钝"——情绪更难平复
        self.dynamic_viscosity = (base
                                  + self.VISC_TENSION_K * self.fluid["张力"]
                                  + self.VISC_FATIGUE_K * self.fatigue)
        # 高兴奋 → 压低粘滞（情绪来得更快更猛）
        self.dynamic_viscosity -= self.excitation * 0.08
        self.dynamic_viscosity = max(0.02, min(1.5, self.dynamic_viscosity))
        # 心理时间：高压缩 → 主观时间慢（难受时度日如年）
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0

    def _psychological_dt_for(self, real_dt: float) -> float:
        """把物理 Δt 转成心理 Δt。粘滞度越大，每物理秒情绪流动越少。"""
        return real_dt * self.psy_dilation / (0.1 + self.dynamic_viscosity)

    # 保留旧名以兼容骨架调用
    def _psychological_dt(self) -> float:
        return self._psychological_dt_for(1.0)

    # ==================================================================
    # 9. 流体连续松弛（向 target 指数回归）
    # ==================================================================
    def _fluid_dynamics(self, dt: float):
        """每个情绪维度 x 向 target[x] 以 (1 - exp(-k·dt)) 的比例靠近。"""
        # 粘滞度 k：越大回归越快；_update_dynamic_viscosity 已设置
        k = 1.0 / (0.2 + self.dynamic_viscosity * 3.0)
        alpha = 1.0 - math.exp(-k * max(0.0, dt))
        alpha = max(0.0, min(1.0, alpha))
        for key in self.fluid:
            tgt = self.fluid_target.get(key, self.fluid[key])
            # 信任额外受 max_trust 天花板限制
            if key == "信任":
                tgt = min(tgt, self.max_trust)
            self.fluid[key] += (tgt - self.fluid[key]) * alpha
            self.fluid[key] = max(0.0, min(1.0, self.fluid[key]))

    # ==================================================================
    # target 重建：基线 + 创伤牵引 + 记忆共振
    # ==================================================================
    def _rebuild_fluid_target(self):
        # 从基线拷贝
        for k, v in self.fluid_baseline.items():
            self.fluid_target[k] = v
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
        # 记忆共振：活跃的相似记忆会稍微拉动 target
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
        # 夹紧
        for k in self.fluid_target:
            self.fluid_target[k] = max(0.0, min(1.0, self.fluid_target[k]))

    # ==================================================================
    # 10. 流体 → 系统反馈（让流体状态影响参数）
    # ==================================================================
    def _fluid_to_system_feedback(self):
        # 高张力 → 心理韧性临时下降（急的时候扛不住）
        tension = self.fluid["张力"]
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0 + tension * 0.5
        # 高愧疚 → 信任小幅修复（愧疚会驱动补偿）
        guilt = self.fluid["愧疚"]
        if guilt > 0.3 and self.max_trust < 1.0:
            self.max_trust = min(1.0, self.max_trust + guilt * 0.0001)

    # ==================================================================
    # 11. 能量代谢
    # ==================================================================
    def _energy_on_event(self, v: Dict[str, float], raw_intensity: float):
        cost = self.ENERGY_EVENT_COST * raw_intensity
        # 负向事件更耗能量
        if v.get("threat", 0.0) > 0.2 or v.get("belonging", 0.0) < -0.2:
            cost *= 1.8
        # 高张力事件更耗
        cost *= (1.0 + self.fluid["张力"])
        self.energy = max(self.ENERGY_MIN, self.energy - cost)

    def _energy_idle(self, dt: float):
        # 自然恢复，疲劳越低恢复越快
        recover = self.ENERGY_RECOVER * dt * (1.0 - 0.5 * self.fatigue)
        self.energy = min(self.ENERGY_MAX, self.energy + recover)

    # ==================================================================
    # 12. 艾宾浩斯遗忘曲线
    # ==================================================================
    def _forget_over(self, dt: float):
        """I(t) = I0 · e^(−λt)，弱痕迹直接剪枝。"""
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
        """任何事件推高唤醒——真实的人对新刺激天生敏感。"""
        novelty = raw_intensity * self.EXCITATION_NOVELTY_GAIN
        # 高强度事件额外激活
        if abs(v.get("threat", 0.0)) > 0.5 or abs(v.get("belonging", 0.0)) > 0.5:
            novelty += raw_intensity * self.EXCITATION_SALIENCE_BOOST
        self.excitation = min(self.EXCITATION_MAX, self.excitation + novelty)

    def _excitation_decay(self, dt: float):
        """无事件时指数回归基线——没人能一直嗨。"""
        if self.excitation > self.EXCITATION_BASELINE:
            self.excitation += (self.EXCITATION_BASELINE - self.excitation) * \
                              (1.0 - math.exp(-self.EXCITATION_DECAY * dt))
            if abs(self.excitation - self.EXCITATION_BASELINE) < 0.005:
                self.excitation = self.EXCITATION_BASELINE

    def _check_boredom(self, dt: float):
        """长时间低唤醒 → 内心躁动。真人独处太久会自己找事。"""
        if self.excitation < self.EXCITATION_BOREDOM_THRESHOLD:
            # 微量注入张力和疏离，模拟"待不住了"
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + 0.003 * dt / 60)
            self.fluid["疏离"] = min(1.0, self.fluid["疏离"] + 0.002 * dt / 60)

    # 兼容旧名
    def _apply_forgetting_curve(self):
        self._forget_over(1.0)

    # 兼容骨架中残留的同名空方法
    def _update_time(self):
        self._advance_time()

    def _update_dynamic_viscosity_old(self):
        self._update_dynamic_viscosity()
