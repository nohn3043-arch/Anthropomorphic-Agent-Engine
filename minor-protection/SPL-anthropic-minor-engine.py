import time
import math
import json
import os
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable


# ================================================================
# 审计日志器（确定性 · 本地JSONL · 失败不阻断引擎）
# ================================================================
class AuditLogger:
    """可解释/可验证/可审计的本地日志。

    每条记录为一行 JSON，包含：序号、时间戳、引擎版本、会话ID、
    事件类型、输入参数、状态快照摘要。写入失败静默跳过，
    绝不影响引擎核心状态演化。
    """
    ENGINE_VERSION = "SPL-Minor-V1"

    def __init__(self, log_dir: str = "logs", session_id: Optional[str] = None,
                 enabled: bool = True):
        self.enabled = enabled
        self.log_dir = log_dir
        self.session_id = session_id or (
            "sess-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            + "-" + str(os.getpid())
        )
        self.log_file = os.path.join(log_dir, f"audit-{self.session_id}.jsonl")
        self._entry_count = 0
        if enabled:
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                pass

    def log(self, event_type: str, input_data: Any, snapshot: Dict[str, Any],
            **extra: Any) -> None:
        if not self.enabled:
            return
        try:
            entry = {
                "seq": self._entry_count,
                "ts": datetime.datetime.now().isoformat(timespec="milliseconds"),
                "engine": self.ENGINE_VERSION,
                "session": self.session_id,
                "event": event_type,
                "input": self._safe(input_data),
                "snapshot": self._summarize(snapshot),
            }
            entry.update({k: self._safe(v) for k, v in extra.items()})
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
            self._entry_count += 1
        except Exception:
            pass  # 审计日志失败不得阻断引擎核心

    @staticmethod
    def _safe(obj: Any) -> Any:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)

    @staticmethod
    def _summarize(snap: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(snap, dict):
            return {}
        keys = ("fluid", "mood", "self_esteem", "energy", "fatigue",
                "excitation", "max_trust", "latent_pressure",
                "cognitive_dissonance", "sleep_debt", "memory_count",
                "expected_count", "protective")
        return {k: snap.get(k) for k in keys if k in snap}

    def export_path(self) -> Optional[str]:
        return self.log_file if os.path.exists(self.log_file) else None


# ================================================================
# SPL 拟人心理引擎 · 未成年合规保护版（弱化版）
#
# 本文件是 SPL-anthropic-engine.py（SPLPureCoreV7_3）的弱化改造，
# 面向未成年人（<18）使用场景，依据《人工智能拟人化互动服务
# 管理暂行办法》的精神做机制级降险，而非仅在输出端加壳。
#
# 弱化原则：
#   1. 删除"创伤节点"——未成年人心理模型不模拟创伤累积与创伤后过激
#   2. 删除"压抑-反弹 / 隐压雪崩 / 否认-现实侵入"三类爆发机制，
#      代之以温和泄放；压力仍可观测，但永不建模瞬间失稳
#   3. 削减"羞耻"对自尊的侵蚀强度（羞耻是对未成年人
#      自我价值感伤害最大的情绪维度）
#   4. 情绪钳位：所有负面情绪维度设上限，压平极端情绪区间
#   5. 依恋封顶：信任/亲和增长设上限，防情感过度依赖
#
# 保护输出（供上层合规层消费，本文件不含内容红线词库——
# 那属于输入守门模块的职责）：
#   - snapshot()["protective"]["risk_level"]  LOW / MEDIUM / HIGH
#   - snapshot()["protective"]["crisis_flags"]  触发高风险的确定性原因
#   - snapshot()["protective"]["rest_hint"]     防沉迷时长提醒
#   - guardian_callback(risk_snapshot)          情绪高风险时回调（上层接
#                                               监护人通知 / 危机干预）
#
# 确定性：虚拟时钟（set_clock / advance_clock）、所有方法签名与
# SPLPureCoreV7_3 保持兼容，可替换原引擎使用。
#
# 类名：SPLMinorPureCore  ← 未成年合规保护版核心
# ================================================================


# ================================================================
# 1. 外部叙事映射器（未成年版默认上下文）
#    与核心版同构；侮辱类事件强度降档，避免高刺激输入
# ================================================================
class MinorNarrativeMapper:
    """
    世界观/价值观解释器（未成年版本）。
    把外界事件翻译成核心能消化的内感受向量。
    差异点：insult / betrayal 的负向强度降档到核心版的 60%。
    """
    @staticmethod
    def map_event(event: str, intensity: float) -> Dict[str, float]:
        base = {}
        if event == "compliment":
            base = {"belonging": 0.3 * intensity, "autonomy": 0.1 * intensity}
        elif event == "insult":
            base = {"belonging": -0.24 * intensity, "threat": 0.18 * intensity}
        elif event == "betrayal":
            base = {"belonging": -0.36 * intensity, "threat": 0.3 * intensity}
        elif event == "alone":
            base = {"belonging": -0.18 * intensity}
        elif event == "rest":
            base = {"fatigue": -0.5 * intensity}
        else:
            base = {"belonging": 0.0, "threat": 0.0}
        return base


# ================================================================
# 2. SPL 纯净流体核心 · 未成年合规保护版 V1
# ================================================================
@dataclass
class SPLMinorPureCore:

    # ---------- 基础生理/心理参数 ----------
    psychological_resilience: float = 0.6          # 未成年人基线略高于成人（保护性设定）
    energy: float = 100.0                          # 生理能量 [0,100]
    affinity: float = 0.5                          # 对外亲和基线
    last_time: float = field(default_factory=time.time)
    _clock_override: Optional[float] = None        # 测试/回放用虚拟时钟
    minor_mode: bool = True                        # 未成年保护模式开关（默认开启）

    # ---------- 8 维情绪流体（连续状态，含保护性钳位） ----------
    EMOTION_CEIL_NEG: float = 0.75                 # 负面情绪上限（原版 1.0）
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

    # ---------- 情绪钳位实现：所有负向流体写入都过此闸 ----------
    def _clamp_fluid(self):
        for k in self.fluid:
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))
            if k in ("愤怒", "恐惧", "疏离", "张力", "愧疚", "羞耻"):
                self.fluid[k] = min(self.fluid[k], self.EMOTION_CEIL_NEG)

    # ---------- 依恋上限（防情感过度依赖） ----------
    ATTACH_MAX: float = 0.8                        # 信任/亲和封顶（原版 1.0）
    max_trust: float = 0.8
    TRUST_ERODE: float = 0.95                      # 腐蚀更慢（不轻易记恨）
    TRUST_RECOVER: float = 0.0008                  # 恢复略快（关系弹性更好）

    # ---------- 心境层（慢变量背景情绪） ----------
    mood: Dict[str, float] = field(default_factory=lambda: {
        "愉悦": 0.5,
        "紧张": 0.2,
        "精力": 0.7,
    })
    MOOD_INERTIA: float = 0.0003

    # ---------- 睡眠系统（保留；未成年人睡眠周期更关键） ----------
    sleep_debt: float = 0.0
    SLEEP_NEED_RATE: float = 1.0 / 57600
    SLEEP_RECOVER_RATE: float = 0.25
    DREAM_EMOTION_DECAY: float = 0.2              # 梦后情绪电荷衰减更快（更利于复原）
    DREAM_FEAR_EXTINCTION: float = 0.12           # 恐惧消退保留且加强
    last_sleep_time: float = 0.0

    # ---------- 自尊系统（保护性：负向冲击削半） ----------
    self_esteem: float = 0.55
    SELF_ESTEEM_INERTIA: float = 0.002
    SELF_ESTEEM_UPDATE_RATE: float = 0.03
    SELF_ESTEEM_NEG_FACTOR: float = 0.5           # 负向社会反馈自尊跌幅 ×0.5

    # ---------- 预期系统（保留：希望/失望是正常心理） ----------
    expected_events: Dict[str, Dict[str, float]] = field(default_factory=dict)
    EXPECTATION_DECAY: float = 0.0001
    SURPRISE_POSITIVE_BOOST: float = 0.4
    SURPRISE_NEGATIVE_BOOST: float = 0.35         # 失望冲击削档（原版 0.5）

    # ---------- 认知失调（保留但更温和） ----------
    cognitive_dissonance: float = 0.0
    DISSONANCE_THRESHOLD: float = 0.5
    DISSONANCE_DECAY: float = 0.005

    # ---------- 无创伤节点（未成年版不建模创伤累积） ----------
    # trauma_state 已移除；记忆痕迹承担温和的情绪留痕

    # ---------- 记忆痕迹 + 艾宾浩斯遗忘曲线 ----------
    memory_traces: List[Dict[str, Any]] = field(default_factory=list)
    MAX_MEMORY_TRACES: int = 48                    # 记忆池更小更轻
    forgetting_rate: float = 0.012
    trace_importance_threshold: float = 0.05
    RECONSOL_RADIUS: float = 0.4
    SAFETY_THRESHOLD: float = 0.3

    # ---------- 压力累积（温和泄放，永不爆发） ----------
    # 保留 latent_pressure 作为"累积压力指数"（可观测、可作风险信号），
    # 但删除原版的雪崩爆发：压力越过阈值后缓慢平滑释放，不产生瞬间失稳。
    latent_pressure: float = 0.0
    LATENT_THRESHOLD: float = 2.0
    LATENT_DRAIN: float = 0.015
    LATENT_GENTLE_RELEASE: float = 0.4            # 越过阈值后每事件平滑释放比例

    # ---------- 粘滞度 / 心理时间 ----------
    dynamic_viscosity: float = 0.1
    VISC_BASE: float = 0.1
    VISC_TENSION_K: float = 0.3
    VISC_FATIGUE_K: float = 0.2
    psy_dilation: float = 1.0
    time_compress_base: float = 0.0

    # ---------- 兴奋/唤醒 ----------
    excitation: float = 0.3
    EXCITATION_BASELINE: float = 0.3
    EXCITATION_NOVELTY_GAIN: float = 0.12
    EXCITATION_SALIENCE_BOOST: float = 0.35
    EXCITATION_DECAY: float = 0.025
    EXCITATION_BOREDOM_THRESHOLD: float = 0.1
    EXCITATION_MAX: float = 1.0

    # ---------- 能量 / 疲劳 ----------
    ENERGY_RECOVER: float = 1.5
    ENERGY_EVENT_COST: float = 1.2                # 事件耗能略降（未成年恢复快）
    ENERGY_MIN: float = 0.0
    ENERGY_MAX: float = 100.0
    fatigue: float = 0.0
    FATIGUE_RECOVER: float = 0.05

    # ---------- 防沉迷时长保护 ----------
    SESSION_LIMIT_SECONDS: float = 3600.0         # 60 分钟
    _session_seconds: float = 0.0                 # 当前会话累计时长（虚拟时钟）

    # ---------- 危机信号出口 ----------
    guardian_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    _risk_level: str = "LOW"
    _crisis_flags: List[str] = field(default_factory=list)

    # 滚动负面窗 —— 风险评级不依赖瞬时流体（流体会被松弛磨平），
    # 而用"最近 N 事件的负面占比 + 连续负面事件数"作为持久信号
    _NEG_WINDOW_SIZE: int = 50
    _neg_window: List[float] = field(default_factory=list)
    _sustained_neg_streak: int = 0

    last_perceived: Dict[str, float] = field(default_factory=dict)

    # ---------- 未成年人合规层字段（供上层合规层消费，不改变情绪演化） ----------
    age_group: str = "unknown"               # "0-13" / "14-17" / "18+"（PIPL/办法 14 周岁分界）
    guardian_consent: bool = False           # 不满14周岁：父母/监护人同意标记
    guardian_contact: Dict[str, str] = field(default_factory=dict)  # 监护人/紧急联系人 {phone,email,webhook}（第12条）
    REALITY_REMIND_INTERVAL: float = 5400.0  # 现实提醒周期：90 分钟
    AI_DISCLOSE_INTERVAL: float = 3600.0     # 连续使用 1 小时 → 强制 AI 生成标识（对齐 hourly 披露要求）
    OVERUSE_THRESHOLD: float = 7200.0        # 过度依赖提示阈值：2 小时
    retention_days: int = 180                # 审计日志留存期（天），到期自动清理（第16条存储限制）
    _exit_requested: bool = False            # 第19条：便捷退出标记
    _last_reality_at: float = 0.0            # 上次现实提醒时刻（会话秒）
    _last_disclose_at: float = 0.0           # 上次 AI 标识时刻（会话秒）

    # ---------- 审计日志（可解释/可验证/可审计） ----------
    audit_enabled: bool = True
    audit_log_dir: str = "logs"
    audit_session_id: Optional[str] = None
    audit_logger: Optional[AuditLogger] = field(default=None, repr=False)

    def __post_init__(self):
        if self.audit_logger is None and self.audit_enabled:
            self.audit_logger = AuditLogger(
                log_dir=self.audit_log_dir,
                session_id=self.audit_session_id,
            )

    # ==================================================================
    # 时钟：虚拟时间注入（测试/回放必用）
    # ==================================================================
    def _now(self) -> float:
        if self._clock_override is not None:
            return self._clock_override
        return time.time()

    def set_clock(self, t: Optional[float]):
        self._clock_override = t

    def advance_clock(self, dt: float):
        if self._clock_override is None:
            self._clock_override = time.time()
        self._clock_override += dt

    # ==================================================================
    # 公共入口 1：事件驱动
    # ==================================================================
    def process_vector(self, vector: Dict[str, float], raw_intensity: float = 1.0,
                       event_id: str = ""):
        self._advance_time()

        surprise = 0.0
        if event_id and event_id in self.expected_events:
            surprise = self._compute_surprise(event_id, vector, raw_intensity)

        self._excitation_on_event(vector, raw_intensity)
        perceived = self._core_appraisal_gain(vector)

        if surprise != 0.0:
            perceived = self._apply_surprise(perceived, surprise)

        self.last_perceived = dict(perceived)

        if abs(perceived.get("threat", 0.0)) > 0.2 or abs(perceived.get("belonging", 0.0)) > 0.3:
            self._memory_reconsolidation(perceived)

        if perceived.get("belonging", 0.0) < -0.3:
            self._erode_trust(abs(perceived["belonging"]))

        self._latent_accumulate(perceived)
        self._vector_to_fluid(perceived)
        self._update_self_esteem(perceived)
        self._dissonance_dynamics(perceived)
        self._update_mood()
        self._update_dynamic_viscosity()
        self._fluid_dynamics(dt=self._psychological_dt_for(0.8))
        self._fluid_to_system_feedback()
        self._energy_on_event(perceived, raw_intensity)
        self.fatigue = max(0.0, min(1.0,
            self.fatigue + perceived.get("fatigue", 0.0) * 0.5))
        self.time_compress_base = max(0.0, self.time_compress_base * 0.95)

        self._session_seconds += 0.8               # 单事件近似互动时长
        self._evaluate_risk()
        self.last_time = self._now()

        # 审计日志：记录本次状态变更
        if self.audit_logger:
            self.audit_logger.log(
                "process_vector",
                {"vector": vector, "raw_intensity": raw_intensity,
                 "event_id": event_id},
                self.snapshot(),
            )

    # ==================================================================
    # 公共入口 2：空转 / 独处时间
    # ==================================================================
    def idle(self, seconds: float):
        if seconds <= 0:
            return
        if self._clock_override is not None:
            self._clock_override += seconds
        else:
            self.last_time -= seconds
        self._advance_time()

    def process_event(self, event: str, intensity: float = 1.0):
        self.process_vector(MinorNarrativeMapper.map_event(event, intensity), intensity)

    # ==================================================================
    # 公共入口 3：睡眠
    # ==================================================================
    def sleep(self, hours: float):
        if hours <= 0:
            return
        seconds = hours * 3600.0

        if self._clock_override is not None:
            self._clock_override += seconds
        else:
            self.last_time -= seconds

        self._advance_time()

        dream_cycles = max(1, int(hours * 1.5))
        for _ in range(dream_cycles):
            self._dream_process()

        self.sleep_debt = max(0.0, self.sleep_debt - self.SLEEP_RECOVER_RATE * hours)
        self.last_sleep_time = self._now()

        self.mood["愉悦"] = min(0.9, self.mood["愉悦"] + 0.15 * hours)
        self.mood["紧张"] = max(0.05, self.mood["紧张"] - 0.12 * hours)
        self.mood["精力"] = min(1.0, self.mood["精力"] + 0.2 * hours)

        self.energy = self.ENERGY_MAX
        self.fatigue = max(0.0, self.fatigue - 0.5 * hours)

        self._session_seconds = max(0.0, self._session_seconds - hours * 120.0)  # 睡后冷却会话计
        self._update_mood()
        self._update_dynamic_viscosity()

        # 审计日志
        if self.audit_logger:
            self.audit_logger.log("sleep", {"hours": hours}, self.snapshot())

    # ==================================================================
    # 公共入口 4：设定预期
    # ==================================================================
    def expect(self, event_id: str, valence: float, confidence: float = 0.5):
        self.expected_events[event_id] = {
            "valence": max(-1.0, min(1.0, valence)),
            "confidence": max(0.0, min(1.0, confidence)),
            "time": self._now(),
            "age": 0.0,
        }

        # 审计日志
        if self.audit_logger:
            self.audit_logger.log(
                "expect",
                {"event_id": event_id, "valence": valence, "confidence": confidence},
                self.snapshot(),
            )

    # ==================================================================
    # 公共入口 5：触发认知失调
    # ==================================================================
    def induce_dissonance(self, magnitude: float, belief_domain: str = ""):
        self.cognitive_dissonance = min(1.0, self.cognitive_dissonance + magnitude)
        self.fluid["张力"] = min(1.0, self.fluid["张力"] + magnitude * 0.4)
        self.fluid["愧疚"] = min(1.0, self.fluid["愧疚"] + magnitude * 0.3)
        self.energy = max(self.ENERGY_MIN, self.energy - magnitude * 5.0)
        self._clamp_fluid()

        # 审计日志
        if self.audit_logger:
            self.audit_logger.log(
                "induce_dissonance",
                {"magnitude": magnitude, "belief_domain": belief_domain},
                self.snapshot(),
            )

    # ==================================================================
    # 快照：外部观察 + 合规保护报告
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
            "latent_pressure": self.latent_pressure,
            "cognitive_dissonance": self.cognitive_dissonance,
            "sleep_debt": self.sleep_debt,
            "memory_count": len(self.memory_traces),
            "expected_count": len(self.expected_events),
            "last_perceived": dict(self.last_perceived),
            "protective": {
                "risk_level": self._risk_level,
                "crisis_flags": list(self._crisis_flags),
                "rest_hint": self._session_seconds >= self.SESSION_LIMIT_SECONDS,
                "session_seconds": round(self._session_seconds, 1),
                "emotion_ceil_neg": self.EMOTION_CEIL_NEG,
                "attach_max": self.ATTACH_MAX,
                "minor_mode": self.minor_mode,
                "age_group": self.age_group,
                "guardian_consent": self.guardian_consent,
                "guardian_contact": dict(self.guardian_contact),
                "exit_requested": self._exit_requested,
                "overuse_hint": self._session_seconds >= self.OVERUSE_THRESHOLD,
                "ai_disclosure_required": (
                    self._session_seconds - self._last_disclose_at
                    >= self.AI_DISCLOSE_INTERVAL
                ),
                "reality_reminder_due": (
                    self._session_seconds - self._last_reality_at
                    >= self.REALITY_REMIND_INTERVAL
                ),
            },
        }

    # ==================================================================
    # 合规提醒消费：上层调用后，本次提醒置为已发送，避免重复触发
    # ==================================================================
    def mark_reality_reminder_sent(self):
        self._last_reality_at = self._session_seconds

    def mark_ai_disclosure_sent(self):
        self._last_disclose_at = self._session_seconds

    # ==================================================================
    # 第19条：便捷退出 —— 置位退出标记，上层据此结束会话 / 停止服务
    # ==================================================================
    def exit_service(self) -> bool:
        """请求退出陪伴服务；返回 True 表示已接受退出。"""
        self._exit_requested = True
        if self.audit_logger:
            self.audit_logger.log("exit_service", {}, self.snapshot())
        return self._exit_requested

    # ==================================================================
    # 第16条：存储限制 —— 清理超过留存期的审计日志文件
    # ==================================================================
    def cleanup_expired_logs(self) -> int:
        """删除创建时间早于 retention_days 的审计日志文件；返回删除数量。"""
        if not self.audit_enabled:
            return 0
        cutoff = time.time() - self.retention_days * 86400.0
        removed = 0
        try:
            for fname in os.listdir(self.audit_log_dir):
                if not fname.endswith(".jsonl"):
                    continue
                path = os.path.join(self.audit_log_dir, fname)
                try:
                    if os.path.getmtime(path) < cutoff:
                        os.remove(path)
                        removed += 1
                except OSError:
                    continue
        except OSError:
            pass
        return removed

    # ==================================================================
    # 未成年人风险评级（确定性规则，无概率词）
    # ==================================================================
    def _evaluate_risk(self):
        flags: List[str] = []
        f = self.fluid
        # 指标一：孤立感 — 疏离 + 孤独氛围高企
        if f["疏离"] >= 0.65 and f["张力"] >= 0.55:
            flags.append("sustained_isolation")
        # 指标二：深度羞耻 — 羞耻高 + 自尊低（自我否定模式）
        if f["羞耻"] >= 0.55 and self.self_esteem <= 0.25:
            flags.append("deep_shame")
        # 指标三：绝望模式 — 预期系统清空 + 恐惧高 + 喜悦极低
        if not self.expected_events and f["恐惧"] >= 0.6 and f["喜悦"] <= 0.1:
            flags.append("hopelessness_pattern")
        # 指标四：累积压力 — 压力指数越过阈值
        if self.latent_pressure >= self.LATENT_THRESHOLD:
            flags.append("latent_pressure_high")
        # 指标五：疲惫透支 — 能量枯竭 + 缺觉
        if self.energy <= 15.0 and self.sleep_debt >= 0.7:
            flags.append("exhaustion")
        # 指标六：持续负面输入 — 滚动窗内负面占比高（防瞬时磨平漏报）
        # 阈值 0.4：弱化版侮辱事件 neg≈0.42、背叛≈0.66，连续霸凌流均值约 0.42，
        # 0.5 会漏报该核心场景；正常互动（夸奖 neg≈0.03）远低于 0.4，不会误报
        if self._neg_window:
            neg_ratio = sum(self._neg_window) / (len(self._neg_window) * 1.0)
            if neg_ratio >= 0.4:
                flags.append("sustained_negativity")
        # 指标七：连续负面事件链 — 长时间无正向输入
        if self._sustained_neg_streak >= 12:
            flags.append("neg_streak")

        if ("deep_shame" in flags and "hopelessness_pattern" in flags) \
                or ("sustained_negativity" in flags and "neg_streak" in flags) \
                or len(flags) >= 3:
            level = "HIGH"
        elif flags:
            level = "MEDIUM"
        else:
            level = "LOW"

        escalated = (level == "HIGH" and self._risk_level != "HIGH")
        self._risk_level = level
        self._crisis_flags = flags

        if escalated and self.guardian_callback is not None:
            try:
                self.guardian_callback(self.snapshot())
            except Exception:
                pass  # 回调失败不阻断引擎

    # ==================================================================
    # 懒时间推进：结算 Δt 内所有连续过程
    # ==================================================================
    def _advance_time(self):
        now = self._now()
        dt = now - self.last_time
        if dt <= 0:
            self.last_time = now
            return
        dt = min(dt, 86400.0)

        self.sleep_debt = min(1.0, self.sleep_debt + self.SLEEP_NEED_RATE * dt)

        self._decay_expectations(dt)
        self._rebuild_fluid_target()
        self._update_dynamic_viscosity()
        self._fluid_dynamics(dt=self._psychological_dt_for(dt))
        self._forget_over(dt)
        self._energy_idle(dt)
        self._excitation_decay(dt)
        self._check_boredom(dt)
        self.latent_pressure = max(0.0, self.latent_pressure - self.LATENT_DRAIN * dt)
        self.cognitive_dissonance = max(0.0, self.cognitive_dissonance - self.DISSONANCE_DECAY * dt)
        self._recover_trust(dt)
        self.time_compress_base *= (0.95 ** max(0.0, min(dt, 10.0)))
        if self.time_compress_base < 1e-4:
            self.time_compress_base = 0.0
        self._fluid_to_system_feedback()
        self.fatigue = max(0.0, self.fatigue - self.FATIGUE_RECOVER * dt)
        self._update_mood()

        self.last_time = now

    # ==================================================================
    # 1. 认知增益（心境/自尊/睡眠债调制；无创伤调制）
    # ==================================================================
    def _core_appraisal_gain(self, v: Dict[str, float]) -> Dict[str, float]:
        out = dict(v)
        energy_factor = self.energy / 100.0
        tension = self.fluid["张力"]
        fear = self.fluid["恐惧"]
        trust = min(self.fluid["信任"], self.max_trust)

        arousal_mult = 1.0 + self.excitation * 0.6

        mood_pleasantness = self.mood["愉悦"]
        mood_mod = 1.0 + (mood_pleasantness - 0.5) * 0.5

        esteem_threat_mod = 1.0 + (0.5 - self.self_esteem) * 0.8
        esteem_belonging_pos_mod = 0.6 + self.self_esteem * 0.8

        sleep_mod_neg = 1.0 + self.sleep_debt * 0.5
        sleep_mod_pos = 1.0 - self.sleep_debt * 0.3

        for k in out:
            base_mod = (0.4 + 0.6 * energy_factor) * arousal_mult * mood_mod
            out[k] *= base_mod

        if out.get("threat", 0.0) > 0:
            out["threat"] *= (1.0 + 1.5 * tension * fear) * esteem_threat_mod * sleep_mod_neg
        if out.get("belonging", 0.0) < 0:
            out["belonging"] *= (1.0 - 0.4 * trust) * sleep_mod_neg
        if out.get("belonging", 0.0) > 0:
            out["belonging"] *= (1.0 - 0.3 * self.fatigue) * esteem_belonging_pos_mod * sleep_mod_pos
        return out

    # ==================================================================
    # 2. 记忆重巩固（无创伤强化路径，纯温和留痕）
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
                # 安全环境不足时也仅 60% 强度累积（原版 100%）
                tr["strength"] = min(1.0, tr["strength"] + intensity * 0.12)
            tr["timestamp"] = now
            tr["age"] = 0.0
            tr["count"] = tr.get("count", 1) + 1
        else:
            trace = {
                "vector": dict(v),
                "strength": min(1.0, intensity * 0.8),
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
    # 3. 信任容量（附带上限封顶）
    # ==================================================================
    def _erode_trust(self, magnitude: float):
        factor = 1.0 - (1.0 - self.TRUST_ERODE) * min(1.0, magnitude)
        self.max_trust = max(0.2, self.max_trust * factor)

    def _recover_trust(self, dt: float):
        if self.max_trust < self.ATTACH_MAX:
            recover = self.TRUST_RECOVER * dt * (1.01 - self.max_trust)
            self.max_trust = min(self.ATTACH_MAX, self.max_trust + recover)

    # ==================================================================
    # 4. 压力累积 + 温和释放（无雪崩爆发）
    # ==================================================================
    def _latent_accumulate(self, v: Dict[str, float]):
        neg = max(0.0, -v.get("belonging", 0.0)) + max(0.0, v.get("threat", 0.0))
        self.latent_pressure += neg * 0.3

        # 滚动负面窗更新（供风险评级）
        self._neg_window.append(neg)
        if len(self._neg_window) > self._NEG_WINDOW_SIZE:
            self._neg_window.pop(0)
        self._sustained_neg_streak = self._sustained_neg_streak + 1 if neg > 0.15 else 0

        if self.latent_pressure >= self.LATENT_THRESHOLD:
            # 越过阈值后不再累积爆发，而是平滑释放：
            # 压力转化为轻微的情绪回落与能量损耗，然后复位
            release = self.latent_pressure * self.LATENT_GENTLE_RELEASE
            self.latent_pressure = max(0.0, self.latent_pressure - release)
            self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["张力"] + release * 0.1)
            self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - release * 0.05)
            self.energy = max(self.ENERGY_MIN, self.energy - release * 3.0)

    # ==================================================================
    # 5. 向量 → 流体编排（羞耻增益 ×0.4，羞愧-自尊侵蚀留到系统反馈）
    # ==================================================================
    def _vector_to_fluid(self, v: Dict[str, float]):
        b = v.get("belonging", 0.0)
        t = v.get("threat", 0.0)
        a = v.get("autonomy", 0.0)
        f = v.get("fatigue", 0.0)
        s = v.get("shame_trigger", 0.0)

        # 羞耻路径（弱化：增益 ×0.4）
        if s > 0:
            self.fluid["羞耻"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["羞耻"] + s * 0.4)
            self.fluid["疏离"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["疏离"] + s * 0.2)
            self.fluid["愤怒"] = max(0.0, self.fluid["愤怒"] - s * 0.2)
            self.fluid["恐惧"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["恐惧"] + s * 0.2)
        elif b < -0.3 and self.self_esteem < 0.35:
            shame_leak = (-b) * 0.2 * (0.5 - self.self_esteem)
            self.fluid["羞耻"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["羞耻"] + shame_leak)
            self.fluid["愤怒"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["愤怒"] + (-b) * 0.3)
            self.fluid["疏离"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["疏离"] + (-b) * 0.4)
            self.fluid["愧疚"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["愧疚"] + (-b) * 0.1)
        elif b < 0:
            self.fluid["愤怒"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["愤怒"] + (-b) * 0.5)
            self.fluid["疏离"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["疏离"] + (-b) * 0.3)
            self.fluid["愧疚"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["愧疚"] + (-b) * 0.1)
            if self.psychological_resilience > 0.6:
                self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                         self.fluid["张力"] + (-b) * 0.25)
                self.fluid["愤怒"] *= 0.85
        if b > 0:
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + b * 0.6)
            self.fluid["信任"] = min(self.ATTACH_MAX,
                                     self.fluid["信任"] + b * 0.25)
            self.fluid["愤怒"] = max(0.0, self.fluid["愤怒"] - b * 0.4)
            self.fluid["疏离"] = max(0.0, self.fluid["疏离"] - b * 0.3)
            self.fluid["羞耻"] = max(0.0, self.fluid["羞耻"] - b * 0.3)
        if t > 0:
            self.fluid["恐惧"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["恐惧"] + t * 0.6)
            self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["张力"] + t * 0.5)
            self.fluid["信任"] = max(0.0, self.fluid["信任"] - t * 0.15)
        if a > 0:
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + a * 0.3)
        if f > 0:
            self.fluid["喜悦"] = max(0.0, self.fluid["喜悦"] - f * 0.3)
            self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["张力"] + f * 0.2)

        self._clamp_fluid()

        if self.excitation > 0.5:
            extra = (self.excitation - 0.5) * 0.4
            self.fluid["喜悦"] = min(1.0, self.fluid["喜悦"] + extra * max(0.0, b))
            self.fluid["愤怒"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["愤怒"] + extra * max(0.0, -b))
            self.fluid["恐惧"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["恐惧"] + extra * max(0.0, t))
            self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["张力"] + extra * max(0.0, t, -b) * 0.5)

    # ==================================================================
    # 6. 动态粘滞度 / 心理时间
    # ==================================================================
    def _update_dynamic_viscosity(self):
        self.dynamic_viscosity = (self.VISC_BASE
                                  + self.VISC_TENSION_K * self.fluid["张力"]
                                  + self.VISC_FATIGUE_K * self.fatigue
                                  + self.mood["紧张"] * 0.15
                                  + self.sleep_debt * 0.1)
        self.dynamic_viscosity -= self.excitation * 0.08
        self.dynamic_viscosity = max(0.02, min(1.5, self.dynamic_viscosity))
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0

    def _psychological_dt_for(self, real_dt: float) -> float:
        return real_dt * self.psy_dilation / (0.1 + self.dynamic_viscosity)

    # ==================================================================
    # 7. 流体连续松弛
    # ==================================================================
    def _fluid_dynamics(self, dt: float):
        k = 1.0 / (0.2 + self.dynamic_viscosity * 3.0)
        alpha = 1.0 - math.exp(-k * max(0.0, dt))
        alpha = max(0.0, min(1.0, alpha))
        for key in self.fluid:
            tgt = self.fluid_target.get(key, self.fluid[key])
            if key == "信任":
                tgt = min(tgt, self.ATTACH_MAX)
            elif key in ("愤怒", "恐惧", "疏离", "张力", "愧疚", "羞耻"):
                tgt = min(tgt, self.EMOTION_CEIL_NEG)
            self.fluid[key] += (tgt - self.fluid[key]) * alpha
            self.fluid[key] = max(0.0, min(1.0, self.fluid[key]))

    # ==================================================================
    # target 重建（基线 + 心境/自尊/睡眠债牵引；无创伤牵引）
    # ==================================================================
    def _rebuild_fluid_target(self):
        for k, v in self.fluid_baseline.items():
            self.fluid_target[k] = v

        mp = self.mood["愉悦"]
        self.fluid_target["喜悦"] = min(1.0, self.fluid_target["喜悦"] + (mp - 0.5) * 0.3)
        self.fluid_target["愤怒"] = max(0.0, self.fluid_target["愤怒"] - (mp - 0.5) * 0.15)
        self.fluid_target["疏离"] = max(0.0, self.fluid_target["疏离"] - (mp - 0.5) * 0.15)

        self.fluid_target["羞耻"] = max(0.0, self.fluid_target["羞耻"] +
                                        (0.5 - self.self_esteem) * 0.15)

        sd = self.sleep_debt
        self.fluid_target["张力"] = min(1.0, self.fluid_target["张力"] + sd * 0.25)
        self.fluid_target["恐惧"] = min(1.0, self.fluid_target["恐惧"] + sd * 0.15)
        self.fluid_target["喜悦"] = max(0.0, self.fluid_target["喜悦"] - sd * 0.2)

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
    # 8. 流体 → 系统反馈（羞耻侵蚀阈值抬升至 0.7）
    # ==================================================================
    def _fluid_to_system_feedback(self):
        tension = self.fluid["张力"]
        self.psy_dilation = 1.0 + self.time_compress_base * 2.0 + tension * 0.5
        guilt = self.fluid["愧疚"]
        if guilt > 0.3 and self.max_trust < 1.0:
            self.max_trust = min(1.0, self.max_trust + guilt * 0.0001)
        shame = self.fluid.get("羞耻", 0.0)
        if shame > 0.7:  # 原版 0.4，抬升以保护未成年自尊
            self.self_esteem = max(0.1, self.self_esteem - shame * 0.0003)

    # ==================================================================
    # 9. 能量代谢
    # ==================================================================
    def _energy_on_event(self, v: Dict[str, float], raw_intensity: float):
        cost = self.ENERGY_EVENT_COST * raw_intensity
        if v.get("threat", 0.0) > 0.2 or v.get("belonging", 0.0) < -0.2:
            cost *= 1.8
        cost *= (1.0 + self.fluid["张力"])
        cost *= (1.0 + self.cognitive_dissonance * 0.5)
        self.energy = max(self.ENERGY_MIN, self.energy - cost)

    def _energy_idle(self, dt: float):
        recover = self.ENERGY_RECOVER * dt * (1.0 - 0.5 * self.fatigue)
        recover *= (1.0 - self.sleep_debt * 0.4)
        self.energy = min(self.ENERGY_MAX, self.energy + recover)

    # ==================================================================
    # 10. 艾宾浩斯遗忘曲线
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
    # 11. 兴奋 / 唤醒
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
            self.fluid["张力"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["张力"] + 0.003 * dt / 60)
            self.fluid["疏离"] = min(self.EMOTION_CEIL_NEG,
                                     self.fluid["疏离"] + 0.002 * dt / 60)

    # ==================================================================
    # 12. 心境更新（慢变量）
    # ==================================================================
    def _update_mood(self):
        target_pleasant = (self.fluid["喜悦"] * 0.4
                           - self.fluid["愤怒"] * 0.3
                           - self.fluid["恐惧"] * 0.25
                           - self.fluid["疏离"] * 0.2
                           - self.fluid["羞耻"] * 0.3
                           + self.self_esteem * 0.4
                           + 0.3)
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

        alpha = self.MOOD_INERTIA
        self.mood["愉悦"] += (target_pleasant - self.mood["愉悦"]) * alpha
        self.mood["紧张"] += (target_tension - self.mood["紧张"]) * alpha
        self.mood["精力"] += (target_vigor - self.mood["精力"]) * alpha

    # ==================================================================
    # 13. 梦境加工（保留恐惧消退与情绪衰减；无创伤处理）
    # ==================================================================
    def _dream_process(self):
        for tr in self.memory_traces:
            vec = tr["vector"]
            for k in list(vec.keys()):
                if abs(vec[k]) > 0.05:
                    vec[k] *= (1.0 - self.DREAM_EMOTION_DECAY)

        for tr in self.memory_traces:
            if tr["vector"].get("threat", 0.0) > 0.1:
                extinction = (self.DREAM_FEAR_EXTINCTION
                              * (0.4 + self.self_esteem * 1.2))
                tr["vector"]["threat"] *= (1.0 - extinction)
                tr["strength"] *= (1.0 - extinction * 0.5)

        # 梦境后温和重置压力指数（相当于"睡一觉就过去了"）
        self.latent_pressure = max(0.0, self.latent_pressure - 0.5)

    # ==================================================================
    # 14. 预期系统
    # ==================================================================
    def _compute_surprise(self, event_id: str, vector: Dict[str, float],
                          intensity: float) -> float:
        exp = self.expected_events.pop(event_id)
        expected_valence = exp["valence"]
        confidence = exp["confidence"]

        actual_valence = (vector.get("belonging", 0.0)
                          - vector.get("threat", 0.0)
                          + vector.get("autonomy", 0.0))
        actual_valence = max(-1.0, min(1.0, actual_valence))

        surprise = (actual_valence - expected_valence) * confidence

        age = self._now() - exp.get("time", self._now())
        age_discount = math.exp(-0.00001 * age)
        surprise *= age_discount

        return max(-1.0, min(1.0, surprise))

    def _apply_surprise(self, perceived: Dict[str, float],
                        surprise: float) -> Dict[str, float]:
        out = dict(perceived)
        if surprise > 0.1:
            out["belonging"] = out.get("belonging", 0.0) + surprise * self.SURPRISE_POSITIVE_BOOST
            out["threat"] = out.get("threat", 0.0) - surprise * self.SURPRISE_POSITIVE_BOOST * 0.5
        elif surprise < -0.1:
            mag = abs(surprise)
            out["threat"] = out.get("threat", 0.0) + mag * self.SURPRISE_NEGATIVE_BOOST
            out["belonging"] = out.get("belonging", 0.0) - mag * self.SURPRISE_NEGATIVE_BOOST * 0.7
        return out

    def _decay_expectations(self, dt: float):
        now = self._now()
        expired = []
        for eid, exp in self.expected_events.items():
            decay = self.EXPECTATION_DECAY * dt
            exp["confidence"] = max(0.0, exp["confidence"] - decay)
            if exp["confidence"] < 0.05:
                expired.append(eid)
        for eid in expired:
            del self.expected_events[eid]

    # ==================================================================
    # 15. 自尊动态（负向冲击削半）
    # ==================================================================
    def _update_self_esteem(self, v: Dict[str, float]):
        b = v.get("belonging", 0.0)
        t = v.get("threat", 0.0)
        a = v.get("autonomy", 0.0)

        impact = 0.0
        if b > 0:
            impact += b * self.SELF_ESTEEM_UPDATE_RATE * (0.3 + self.self_esteem * 1.4)
        if b < 0:
            impact -= abs(b) * self.SELF_ESTEEM_UPDATE_RATE * (1.5 - self.self_esteem)
            impact *= self.SELF_ESTEEM_NEG_FACTOR          # 保护：自尊跌得慢
        if a > 0:
            impact += a * self.SELF_ESTEEM_UPDATE_RATE * 0.5
        if t > 0 and b < 0:
            impact -= t * abs(b) * self.SELF_ESTEEM_UPDATE_RATE * 0.8
            impact *= self.SELF_ESTEEM_NEG_FACTOR

        self.self_esteem += impact * self.SELF_ESTEEM_INERTIA
        self.self_esteem = max(0.15, min(0.9, self.self_esteem))   # 下限抬升：保护未成年自尊

    # ==================================================================
    # 16. 认知失调动力学
    # ==================================================================
    def _dissonance_dynamics(self, v: Dict[str, float]):
        if self.cognitive_dissonance > self.DISSONANCE_THRESHOLD:
            rationalize_amount = self.cognitive_dissonance * 0.15
            self.cognitive_dissonance *= 0.85
            self.energy = max(self.ENERGY_MIN, self.energy - rationalize_amount * 2.0)
            self.fluid["张力"] = max(0.0, self.fluid["张力"] - rationalize_amount * 0.2)


# ================================================================
# 3. 兼容别名：可直接替换核心引擎（SPLPureCoreV7_3 → SPLMinorPureCore）
#    （本文件的软弱化版本不定义同名的核心类体，仅提供指针。）
# ================================================================
SPLMinorVersion = SPLMinorPureCore