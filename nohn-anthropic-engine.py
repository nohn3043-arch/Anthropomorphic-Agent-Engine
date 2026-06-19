import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional

# ================================================================
# 1. 外部叙事映射器（这就是你所说的“自设：偏见/世界观/价值观”）
#    用户可随意替换，无需修改核心代码。
# ================================================================
class NarrativeMapper:
    """
    世界观/价值观解释器 —— 纯外部策略。
    负责将外界事件（如“被侮辱”）翻译为核心能理解的“基础内感受向量”。
    不同的角色（乐观/悲观/厌世）只需替换此 Mapper。
    """
    @staticmethod
    def map_event(event: str, intensity: float) -> Dict[str, float]:
        """
        返回核心能消化的维度向量。
        维度仅为：归属感(belonging)、自主性(autonomy)、威胁(threat)、体力消耗(fatigue)
        """
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
            # 中性事件默认细微波动（模拟生活中不可名状的微扰）
            base = {"belonging": 0.0, "threat": 0.0}
        return base


# ================================================================
# 2. SPL 纯净流体核心 V7.3（不认识任何具体事件，只认数字向量）
# ================================================================
@dataclass
class SPLPureCoreV7_3:
    """
    SPL 纯净拟人核心 V7.3
    职责：仅处理“基础内感受向量” → 产生情绪流体、记忆印迹、能量代谢。
    所有语义（偏见/世界观）由外部 NarrativeMapper 提供。
    """

    # ========== 基础生理/心理参数 ==========
    psychological_resilience: float = 0.5          # 心理韧性（恢复力）
    energy: float = 100.0                          # 生理能量
    affinity: float = 0.5                         # 对外亲和基线
    last_time: float = field(default_factory=time.time)

    # ========== 流体情绪场（7维连续状态） ==========
    fluid: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })
    fluid_target: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })

    # ========== 创伤系统（SPL离散节点） ==========
    trauma_state: Dict[str, float] = field(default_factory=dict)  # 键为创伤维度（如"belonging_threat"）

    # ========== V7.3 核心升级：记忆痕迹 + 遗忘曲线 ==========
    memory_traces: List[Dict[str, Any]] = field(default_factory=list)
    MAX_MEMORY_TRACES: int = 64                    # 硬上限，防止O(n)灾难
    forgetting_rate: float = 0.01                  # 每单位时间衰减率（艾宾浩斯指数衰减）
    trace_importance_threshold: float = 0.01       # 低于此强度的痕迹直接遗忘

    # ========== 压抑与隐压系统 ==========
    suppression_load: float = 0.0
    latent_pressure: float = 0.0
    max_trust: float = 1.0
    time_compress_base: float = 0.0

    # ========== 雪崩保护：不应期 ==========
    eruption_cooldown: int = 0                     # 爆发后需冷却N次调用

    # ================================================================
    # 核心唯一公共入口（接受数字向量，拒绝语义字符串）
    # ================================================================
    def process_vector(self, vector: Dict[str, float], raw_intensity: float = 1.0):
        """
        参数 vector 示例: {"belonging": -0.5, "threat": 0.3, "fatigue": 0.1}
        这是核心与外界唯一的接口。
        """
        self._update_time()

        # ---- 1. 认知扭曲：核心级别的生理增益（非语义） ----
        # 纯粹基于能量和创伤激活程度，放大或衰减输入的向量强度
        perceived_vector = self._core_appraisal_gain(vector)

        # ---- 2. 记忆重巩固（触发条件：高威胁或高归属变动） ----
        if abs(perceived_vector.get("threat", 0.0)) > 0.2 or abs(perceived_vector.get("belonging", 0.0)) > 0.3:
            self._memory_reconsolidation(perceived_vector)

        # ---- 3. 创伤形成（基于威胁维度） ----
        threat_val = perceived_vector.get("threat", 0.0)
        if threat_val > (0.4 * (1.0 - self.psychological_resilience)):
            self._apply_trauma("threat", threat_val)

        # ---- 4. 信任容量腐蚀（基于归属负向冲击） ----
        if perceived_vector.get("belonging", 0.0) < -0.3:
            self._erode_trust(abs(perceived_vector["belonging"]))

        # ---- 5. 隐压累积 ----
        self._latent_pressure_accumulate(perceived_vector)

        # ---- 6. 向量 → 流体映射（纯数学投射） ----
        self._vector_to_fluid(perceived_vector)

        # ---- 7. 压抑动力学 ----
        self._suppression_dynamics()

        # ---- 8. 动态粘滞度与心理时间 ----
        self._update_dynamic_viscosity()
        psy_dt = self._psychological_dt()

        # ---- 9. 流体演化 ----
        self._fluid_dynamics(dt=psy_dt)

        # ---- 10. 流体 → 核心反馈 ----
        self._fluid_to_system_feedback()

        # ---- 11. 能量代谢 ----
        self._energy_metabolism(perceived_vector)

        # ---- 12. 遗忘曲线（核心功能） ----
        self._apply_forgetting_curve()

        # ---- 13. 冷却递减 ----
        if self.eruption_cooldown > 0:
            self.eruption_cooldown -= 1
        self.time_compress_base *= 0.95

    # ==========================================