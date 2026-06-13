import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class SPLPsychicFieldV5_5:
    """
    V5.5 核心升级：
    = 人格函数化（Personality = Function Space）
    = 状态只是函数的输出
    """

    # =========================
    # 状态场（仍然存在，但降级为“输出层”）
    # =========================
    state: Dict[str, float] = field(default_factory=lambda: {
        "energy": 100.0,
        "affinity": 0.5,
        "trust": 0.5,
        "threat": 0.2,
        "tension": 0.2,
        "coherence": 0.6
    })

    # =========================
    # 世界模型
    # =========================
    world_model: Dict[str, float] = field(default_factory=lambda: {
        "trust_world": 0.6,
        "hostility_world": 0.4
    })

    # =========================
    # 创伤场（扰动函数）
    # =========================
    trauma_field: Dict[str, float] = field(default_factory=dict)

    # =========================
    # 🧠 人格函数参数（核心）
    # =========================
    personality_curves: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "trust":   {"k": 2.0, "bias": 0.0, "threshold": 0.5},
        "threat":  {"k": 3.0, "bias": 0.1, "threshold": 0.3},
        "affinity":{"k": 1.5, "bias": 0.0, "threshold": 0.4},
        "tension": {"k": 2.5, "bias": 0.1, "threshold": 0.5},
    })

    # =========================
    # 解释记忆（人格偏置来源）
    # =========================
    interpretation_bias: Dict[str, float] = field(default_factory=lambda: {
        "benevolent": 0.25,
        "threat": 0.25,
        "defensive": 0.25,
        "neutral": 0.25
    })

    memory: List[Dict[str, Any]] = field(default_factory=list)

    inertia: float = 0.82
    plasticity: float = 0.1
    memory_learning_rate: float = 0.04

    last_time: float = field(default_factory=time.time)

    # ==================================================
    # 主入口
    # ==================================================
    def process_event(self, event: str, intensity: float = 1.0, delta_time: float = None):
        dt = delta_time if delta_time is not None else self._dt()
        dt = min(dt, 5.0)

        self._relax(dt)
        self._recover_energy(dt)
        self._decay_trauma(dt)
        self._update_world(event, intensity)

        # 🧠 解释竞争
        interp = self._interpret(event, intensity)

        # 🧠 核心：函数驱动状态更新
        self._apply_nonlinear_dynamics(interp, event, intensity, dt)

        # 🧠 人格函数学习（V5.5核心）
        self._update_personality_curves(interp, event, intensity)

        self._store(event, intensity)
        self.last_time = time.time()

    # ==================================================
    # 时间
    # ==================================================
    def _dt(self):
        return max(0.0, time.time() - self.last_time)

    # ==================================================
    # 松弛
    # ==================================================
    def _relax(self, dt):
        for k in self.state:
            target = 0.5
            if k == "energy":
                target = 100.0

            self.state[k] += (target - self.state[k]) * (1 - self.inertia) * dt
            self.state[k] = self._clip(k, self.state[k])

    # ==================================================
    # 能量恢复
    # ==================================================
    def _recover_energy(self, dt):
        self.state["energy"] = min(100.0, self.state["energy"] + 0.35 * dt)

    # ==================================================
    # 创伤衰减
    # ==================================================
    def _decay_trauma(self, dt):
        for k in list(self.trauma_field.keys()):
            self.trauma_field[k] -= 0.06 * dt
            if self.trauma_field[k] <= 0:
                del self.trauma_field[k]

    # ==================================================
    # 世界模型
    # ==================================================
    def _update_world(self, event, intensity):
        if event == "betrayal":
            self.world_model["trust_world"] -= 0.07 * intensity
        if event == "help":
            self.world_model["trust_world"] += 0.04 * intensity

        for k in self.world_model:
            self.world_model[k] = self._clip01(self.world_model[k])

    # ==================================================
    # 🧠 解释竞争（简化版）
    # ==================================================
    def _interpret(self, event, intensity):
        trust_w = self.world_model["trust_world"]
        trauma = sum(self.trauma_field.values())

        raw = {
            "benevolent": trust_w * intensity,
            "threat": (1 - trust_w) * intensity + trauma * 0.3,
            "defensive": trauma * intensity,
            "neutral": 0.5 * (1 - intensity)
        }

        return self._softmax(raw)

    # ==================================================
    # 🧠 非线性人格动力系统（核心）
    # ==================================================
    def _apply_nonlinear_dynamics(self, interp, event, intensity, dt):

        def curve(x, params):
            k = params["k"]
            bias = params["bias"]
            threshold = params["threshold"]

            # 🧠 非线性核心函数（人格曲率）
            y = math.tanh(k * (x + bias))

            # 🧠 阈值机制（创伤触发）
            if x < threshold:
                y *= 0.3

            return y

        # trust
        self.state["trust"] += curve(interp["benevolent"], self.personality_curves["trust"]) * dt
        self.state["trust"] -= curve(interp["threat"], self.personality_curves["trust"]) * dt

        # threat
        self.state["threat"] += curve(interp["threat"], self.personality_curves["threat"]) * dt

        # affinity
        self.state["affinity"] += curve(interp["benevolent"], self.personality_curves["affinity"]) * dt

        # tension
        self.state["tension"] += curve(interp["threat"], self.personality_curves["tension"]) * dt

        # energy cost = conflict curvature
        conflict = sum([abs(v - 0.25) for v in interp.values()])
        self.state["energy"] -= conflict * 1.5 * dt

        # clip
        for k in self.state:
            self.state[k] = self._clip(k, self.state[k])

    # ==================================================
    # 🧠 人格函数学习（核心升级点）
    # ==================================================
    def _update_personality_curves(self, interp, event, intensity):

        winner = max(interp.items(), key=lambda x: x[1])[0]

        # winner强化
        self.interpretation_bias[winner] += self.memory_learning_rate * intensity

        # loser衰减
        for k in self.interpretation_bias:
            if k != winner:
                self.interpretation_bias[k] -= self.memory_learning_rate * 0.2 * intensity

        # clip
        for k in self.interpretation_bias:
            self.interpretation_bias[k] = self._clip01(self.interpretation_bias[k])

    # ==================================================
    # 创伤形成
    # ==================================================
    def _store(self, event, intensity):
        self.memory.append({
            "e": event,
            "i": intensity,
            "t": time.time()
        })
        self.memory = self.memory[-100:]

    # ==================================================
    # 工具
    # ==================================================
    def _softmax(self, d):
        m = max(d.values())
        exps = {k: math.exp(v - m) for k, v in d.items()}
        s = sum(exps.values())
        return {k: v / s for k, v in exps.items()}

    def _clip(self, k, v):
        if k == "energy":
            return max(0.0, min(100.0, v))
        return max(0.0, min(1.0, v))

    def _clip01(self, v):
        return max(0.0, min(1.0, v))

    # ==================================================
    # 输出
    # ==================================================
    def generate_prompt(self):
        return "\n".join([
            "【SPL V5.5 非线性人格系统】",
            f"energy={self.state['energy']:.2f}",
            f"trust={self.state['trust']:.2f}",
            f"affinity={self.state['affinity']:.2f}",
            f"threat={self.state['threat']:.2f}",
            f"tension={self.state['tension']:.2f}",
            "",
            "【人格函数参数】",
            str(self.personality_curves),
            "",
            "【解释偏好】",
            str(self.interpretation_bias),
            "",
            "【创伤】",
            str(self.trauma_field)
        ])