import time
import math
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class SPLPsychicFieldV5_3:
    """
    V5.3 核心升级：
    = 引入「解释记忆塑形机制」
    = 人格开始具有“历史偏好结构”
    """

    # =========================
    # 基础状态
    # =========================
    state: Dict[str, float] = field(default_factory=lambda: {
        "energy": 100.0,
        "affinity": 0.5,
        "trust": 0.5,
        "threat": 0.2,
        "tension": 0.2,
        "coherence": 0.6
    })

    relax_target: Dict[str, float] = field(default_factory=lambda: {
        "energy": 100.0,
        "affinity": 0.5,
        "trust": 0.5,
        "threat": 0.1,
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
    # 创伤场
    # =========================
    trauma_field: Dict[str, float] = field(default_factory=dict)

    # =========================
    # 🧠 解释偏好记忆（V5.3核心）
    # =========================
    interpretation_memory: Dict[str, float] = field(default_factory=lambda: {
        "benevolent": 0.25,
        "threat": 0.25,
        "defensive": 0.25,
        "neutral": 0.25
    })

    # =========================
    # 事件记忆
    # =========================
    memory: List[Dict[str, Any]] = field(default_factory=list)

    # =========================
    # 参数
    # =========================
    inertia: float = 0.82
    plasticity: float = 0.1
    memory_plasticity: float = 0.05   # ⭐解释学习率（核心新增）
    noise: float = 0.015

    last_time: float = field(default_factory=time.time)

    # ==================================================
    # 主入口
    # ==================================================
    def process_event(self, event: str, intensity: float = 1.0, delta_time: float = None):
        dt = delta_time if delta_time is not None else self._dt()
        dt = min(dt, 5.0)

        # 1. 松弛
        self._relax(dt)

        # 2. 能量恢复
        self._recover(dt)

        # 3. 创伤衰减
        self._decay_trauma(dt)

        # 4. 世界更新
        self._update_world(event, intensity)

        # 5. 🧠 解释竞争（加入历史偏好）
        interpretation = self._interpret(event, intensity)

        # 6. 状态更新
        self._apply_interpretation(interpretation, dt)

        # 7. ⭐解释记忆更新（人格形成关键）
        self._update_interpretation_memory(interpretation, event, intensity)

        # 8. 创伤形成
        self._maybe_trauma(event, intensity)

        # 9. 记忆记录
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
            target = self.relax_target[k]
            self.state[k] += (target - self.state[k]) * (1 - self.inertia) * dt
            self.state[k] = self._clip(k, self.state[k])

    # ==================================================
    # 能量恢复
    # ==================================================
    def _recover(self, dt):
        self.state["energy"] = min(
            100.0,
            self.state["energy"] + 0.4 * dt
        )

    # ==================================================
    # 创伤衰减
    # ==================================================
    def _decay_trauma(self, dt):
        for k in list(self.trauma_field.keys()):
            self.trauma_field[k] -= 0.08 * dt
            if self.trauma_field[k] <= 0:
                del self.trauma_field[k]

    # ==================================================
    # 世界模型
    # ==================================================
    def _update_world(self, event, intensity):
        if event == "betrayal":
            self.world_model["trust_world"] -= 0.08 * intensity
        if event == "help":
            self.world_model["trust_world"] += 0.04 * intensity

        for k in self.world_model:
            self.world_model[k] = self._clip01(self.world_model[k])

    # ==================================================
    # 🧠 解释竞争（加入人格偏好）
    # ==================================================
    def _interpret(self, event, intensity):

        trust_world = self.world_model["trust_world"]
        trauma_bias = sum(self.trauma_field.values())

        # ⭐引入“人格偏好修正”
        pref = self.interpretation_memory

        candidates = {
            "benevolent": trust_world * intensity * pref["benevolent"],
            "threat": (1 - trust_world) * intensity * pref["threat"] + trauma_bias * 0.3,
            "neutral": 0.5 * (1 - intensity) * pref["neutral"],
            "defensive": trauma_bias * intensity * pref["defensive"]
        }

        return self._softmax(candidates)

    # ==================================================
    # 状态更新
    # ==================================================
    def _apply_interpretation(self, interp, dt):

        w_b = interp["benevolent"]
        w_t = interp["threat"]
        w_d = interp["defensive"]

        self.state["trust"] += (w_b * 0.1 - w_t * 0.15) * dt
        self.state["affinity"] += (w_b * 0.08 - w_t * 0.05) * dt
        self.state["threat"] += (w_t * 0.1 + w_d * 0.12) * dt
        self.state["tension"] += (w_t * 0.1 + w_d * 0.08) * dt
        self.state["coherence"] -= w_t * 0.05 * dt

        # energy消耗 = 解释冲突
        conflict = self._entropy(interp)
        self.state["energy"] -= conflict * 2.0 * dt

        for k in self.state:
            self.state[k] = self._clip(k, self.state[k])

    # ==================================================
    # 🧠 V5.3核心：解释记忆更新（人格形成机制）
    # ==================================================
    def _update_interpretation_memory(self, interp, event, intensity):

        # 找最大解释
        winner = max(interp.items(), key=lambda x: x[1])[0]

        # ⭐赢家强化（赫布学习）
        self.interpretation_memory[winner] += self.memory_plasticity * intensity

        # ⭐非赢家衰减
        for k in self.interpretation_memory:
            if k != winner:
                self.interpretation_memory[k] -= self.memory_plasticity * 0.3 * intensity

        # clip
        for k in self.interpretation_memory:
            self.interpretation_memory[k] = self._clip01(self.interpretation_memory[k])

    # ==================================================
    # 创伤形成
    # ==================================================
    def _maybe_trauma(self, event, intensity):
        if intensity < 0.7:
            return
        if event in ["betrayal", "insult"]:
            self.trauma_field[event] = min(
                1.0,
                self.trauma_field.get(event, 0.0) + intensity * 0.25
            )

    # ==================================================
    # 记忆
    # ==================================================
    def _store(self, event, intensity):
        self.memory.append({
            "event": event,
            "intensity": intensity,
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

    def _entropy(self, d):
        return -sum(p * math.log(p + 1e-9) for p in d.values())

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
            "【SPL V5.3 心理场】",
            f"energy={self.state['energy']:.2f}",
            f"trust={self.state['trust']:.2f}",
            f"affinity={self.state['affinity']:.2f}",
            f"threat={self.state['threat']:.2f}",
            f"tension={self.state['tension']:.2f}",
            f"coherence={self.state['coherence']:.2f}",
            "",
            "【解释偏好（人格结构核）】",
            str(self.interpretation_memory),
            "",
            "【创伤】",
            str(self.trauma_field)
        ])