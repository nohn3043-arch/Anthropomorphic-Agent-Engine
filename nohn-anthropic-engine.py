from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import time
import math


@dataclass
class SPLFluidUnifiedEngineV6:
    """
    SPL × Fluid 融合人格引擎 V6.0

    核心结构：
    1. SPL层：离散事件 + 创伤 + 相变
    2. Fluid层：连续情绪流体场
    3. Coupling层：双向耦合反馈系统
    """

    # =========================
    # SPL 层（事件与创伤系统）
    # =========================
    trauma_state: Dict[str, float] = field(default_factory=dict)
    event_history: List[Dict[str, Any]] = field(default_factory=list)

    # 创伤形成阈值
    trauma_threshold: float = 0.7
    trauma_decay: float = 0.05

    # =========================
    # Fluid 层（连续情绪场）
    # =========================
    fluid: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.0,
        "愤怒": 0.0,
        "恐惧": 0.0,
        "信任": 0.5,
        "疏离": 0.2,
        "张力": 0.2
    })

    fluid_target: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2,
        "愤怒": 0.0,
        "恐惧": 0.1,
        "信任": 0.5,
        "疏离": 0.2,
        "张力": 0.2
    })

    viscosity: float = 0.35
    inertia: float = 0.8

    # =========================
    # 全局状态
    # =========================
    energy: float = 100.0
    affinity: float = 0.5
    last_time: float = field(default_factory=time.time)

    # =========================================================
    # 1. SPL层：事件注入（离散冲击）
    # =========================================================
    def process_event(self, event: str, intensity: float = 1.0):

        self._update_time()

        # 记录事件
        self.event_history.append({
            "event": event,
            "intensity": intensity,
            "t": time.time()
        })

        # ===== SPL：创伤形成（相变机制） =====
        if event in ["betrayal", "insult", "loss"] and intensity > self.trauma_threshold:
            self.trauma_state[event] = min(
                1.0,
                self.trauma_state.get(event, 0.0) + intensity * 0.4
            )

        # ===== SPL → Fluid：事件直接注入流体 =====
        self._event_to_fluid(event, intensity)

        # ===== SPL → Fluid：创伤扭曲流体目标 =====
        self._trauma_modulation()

        # ===== Fluid更新 =====
        self._fluid_dynamics()

        # ===== Fluid → SPL：状态反作用（关键耦合） =====
        self._fluid_to_spl_feedback()

        # ===== 创伤自然衰减 =====
        self._decay_trauma()

        # ===== 能量恢复/消耗 =====
        self._energy_dynamics(event, intensity)

    # =========================================================
    # 2. SPL → Fluid 映射（事件冲击）
    # =========================================================
    def _event_to_fluid(self, event, intensity):

        if event == "compliment":
            self.fluid["喜悦"] += 0.15 * intensity
            self.fluid["信任"] += 0.05 * intensity

        if event == "insult":
            self.fluid["愤怒"] += 0.2 * intensity
            self.fluid["张力"] += 0.1 * intensity

        if event == "betrayal":
            self.fluid["恐惧"] += 0.25 * intensity
            self.fluid["信任"] -= 0.3 * intensity

        if event == "alone":
            self.fluid["疏离"] += 0.1 * intensity

    # =========================================================
    # 3. 创伤对流体目标的扭曲（相变核心）
    # =========================================================
    def _trauma_modulation(self):

        total_trauma = sum(self.trauma_state.values())

        for event, strength in self.trauma_state.items():
            if event == "betrayal":
                self.fluid_target["信任"] = max(0.0, 0.5 - strength * 0.6)
                self.fluid_target["疏离"] = min(1.0, 0.2 + strength * 0.5)

            if event == "insult":
                self.fluid_target["张力"] = min(1.0, 0.2 + strength * 0.6)

        # 全局压缩效应（人格收缩）
        if total_trauma > 1.0:
            self.affinity *= 0.95

    # =========================================================
    # 4. Fluid动力学（连续场）
    # =========================================================
    def _fluid_dynamics(self):

        dt = 1.0
        alpha = (1 - self.viscosity) * (self.energy / 100.0)

        for k in self.fluid:
            target = self.fluid_target.get(k, 0.0)
            self.fluid[k] += alpha * (target - self.fluid[k]) * dt

            # clamp
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))

    # =========================================================
    # 5. Fluid → SPL反馈（情绪反推认知）
    # =========================================================
    def _fluid_to_spl_feedback(self):

        if self.fluid["恐惧"] > 0.6:
            self.fluid_target["信任"] -= 0.05

        if self.fluid["喜悦"] > 0.7:
            self.affinity += 0.02

        if self.fluid["张力"] > 0.6:
            self.energy -= 2.0

        self.affinity = max(0.0, min(1.0, self.affinity))

    # =========================================================
    # 6. 创伤衰减（慢系统）
    # =========================================================
    def _decay_trauma(self):
        for k in list(self.trauma_state.keys()):
            self.trauma_state[k] -= self.trauma_decay * 0.01
            if self.trauma_state[k] <= 0:
                del self.trauma_state[k]

    # =========================================================
    # 7. 能量系统
    # =========================================================
    def _energy_dynamics(self, event, intensity):

        if event in ["compliment", "rest"]:
            self.energy += 2.0 * intensity

        if event in ["insult", "betrayal"]:
            self.energy -= 5.0 * intensity

        self.energy = max(0.0, min(100.0, self.energy))

    # =========================================================
    # 8. 时间更新
    # =========================================================
    def _update_time(self):
        now = time.time()
        self.last_time = now

    # =========================================================
    # 输出人格状态
    # =========================================================
    def snapshot(self) -> str:

        dominant = sorted(self.fluid.items(), key=lambda x: x[1], reverse=True)

        trauma_str = ", ".join([f"{k}:{v:.2f}" for k, v in self.trauma_state.items()]) or "无"

        return "\n".join([
            "=== SPL × Fluid 人格状态 ===",
            f"能量: {self.energy:.1f} | 亲和: {self.affinity:.2f}",
            f"主导情绪: {dominant[0][0]}({dominant[0][1]:.2f})",
            f"次级状态: {dominant[1][0]}({dominant[1][1]:.2f})",
            f"创伤场: {trauma_str}"
        ])