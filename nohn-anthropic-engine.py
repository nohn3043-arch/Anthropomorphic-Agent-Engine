
import time
import math
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List


# ==================================================
# SPL V5：统一心理场引擎
# ==================================================

@dataclass
class SPLPsychicFieldV5:

    # =========================
    # 基础状态场（统一 state）
    # =========================
    state: Dict[str, float] = field(default_factory=lambda: {
        "energy": 100.0,          # 生理/心理能量
        "affinity": 0.5,          # 关系吸引
        "trust": 0.5,             # 信任
        "threat": 0.2,            # 威胁感
        "coherence": 0.5,         # 自洽程度
        "tension": 0.2            # 内部张力
    })

    # =========================
    # 世界模型（预测场）
    # =========================
    world_model: Dict[str, float] = field(default_factory=lambda: {
        "trust_world": 0.6,
        "stability_world": 0.6,
        "effort_reward": 0.6
    })

    # =========================
    # 创伤残余势能（不是记忆，是畸变场）
    # =========================
    trauma_field: Dict[str, float] = field(default_factory=dict)

    # =========================
    # 事件记忆（轻量）
    # =========================
    memory_trace: List[Dict[str, Any]] = field(default_factory=list)

    # =========================
    # 系统参数
    # =========================
    inertia: float = 0.85              # 人格惯性（越高越稳定）
    plasticity: float = 0.08           # 可塑性
    noise: float = 0.02                # 偏见扰动

    last_time: float = field(default_factory=time.time)

    # ==================================================
    # 主入口：心理场演化
    # ==================================================
    def process_event(self, event_type: str, intensity: float = 1.0):

        dt = self._delta_time()

        # 1. 时间衰减（系统松弛）
        self._relaxation(dt)

        # 2. 世界模型更新（预测学习）
        self._update_world_model(event_type, intensity)

        # 3. 创伤场作用（势能扰动）
        trauma_force = self._apply_trauma_field(event_type, intensity)

        # 4. 事件力计算（外界冲击）
        event_force = self._event_to_force(event_type, intensity)

        # 5. 世界预期修正（预测误差）
        expectation_force = self._expectation_error(event_type, intensity)

        # 6. 合力更新状态场（核心）
        self._apply_forces(event_force, trauma_force, expectation_force, dt)

        # 7. 生成创伤残留（如果冲击过强）
        self._maybe_form_trauma(event_type, intensity)

        # 8. 记忆记录
        self._store_memory(event_type, intensity)

        self.last_time = time.time()

    # ==================================================
    # 时间差
    # ==================================================
    def _delta_time(self):
        now = time.time()
        dt = now - self.last_time
        return min(dt, 5.0)

    # ==================================================
    # 松弛（人格惯性核心）
    # ==================================================
    def _relaxation(self, dt):
        for k in self.state:
            target = 0.5
            self.state[k] += (target - self.state[k]) * (1 - self.inertia) * dt

    # ==================================================
    # 世界模型更新
    # ==================================================
    def _update_world_model(self, event, intensity):

        if event == "betrayal":
            self.world_model["trust_world"] -= 0.1 * intensity

        if event == "help":
            self.world_model["trust_world"] += 0.05 * intensity

        if event == "success":
            self.world_model["effort_reward"] += 0.05 * intensity

        if event == "failure":
            self.world_model["effort_reward"] -= 0.05 * intensity

        # clamp
        for k in self.world_model:
            self.world_model[k] = max(0.0, min(1.0, self.world_model[k]))

    # ==================================================
    # 创伤场作用（残余势能）
    # ==================================================
    def _apply_trauma_field(self, event, intensity):

        force = {
            "trust": 0.0,
            "threat": 0.0,
            "tension": 0.0
        }

        for t, val in self.trauma_field.items():
            decay = val * 0.5

            if t == "betrayal":
                force["trust"] -= decay
                force["threat"] += decay

            if t == "insult":
                force["tension"] += decay

        return force

    # ==================================================
    # 事件力（当前冲击）
    # ==================================================
    def _event_to_force(self, event, intensity):

        f = {
            "trust": 0.0,
            "affinity": 0.0,
            "threat": 0.0,
            "tension": 0.0,
            "energy": 0.0
        }

        if event == "compliment":
            f["affinity"] += 0.05 * intensity

        if event == "insult":
            f["tension"] += 0.1 * intensity
            f["threat"] += 0.1 * intensity

        if event == "betrayal":
            f["trust"] -= 0.2 * intensity
            f["threat"] += 0.2 * intensity

        if event == "help":
            f["trust"] += 0.1 * intensity
            f["affinity"] += 0.05 * intensity

        return f

    # ==================================================
    # 预测误差（世界观驱动情绪）
    # ==================================================
    def _expectation_error(self, event, intensity):

        expected = 0.5

        if event == "betrayal":
            expected = 1.0 - self.world_model["trust_world"]

        if event == "help":
            expected = self.world_model["trust_world"]

        surprise = abs(intensity - expected)

        return {
            "trust": surprise * 0.05,
            "tension": surprise * 0.05
        }

    # ==================================================
    # 合力更新（核心动力学方程）
    # ==================================================
    def _apply_forces(self, event_f, trauma_f, exp_f, dt):

        for k in self.state:

            total = 0.0
            total += event_f.get(k, 0.0)
            total += trauma_f.get(k, 0.0)
            total += exp_f.get(k, 0.0)

            # 惯性抑制
            delta = total * self.plasticity * dt

            # 噪声（偏见）
            delta += (math.sin(time.time() * 0.01) * self.noise)

            self.state[k] += delta

            self.state[k] = max(0.0, min(1.0, self.state[k]))

    # ==================================================
    # 创伤形成
    # ==================================================
    def _maybe_form_trauma(self, event, intensity):

        if intensity < 0.7:
            return

        if event in ["betrayal", "insult"]:
            self.trauma_field[event] = min(
                1.0,
                self.trauma_field.get(event, 0.0) + intensity * 0.3
            )

    # ==================================================
    # 记忆
    # ==================================================
    def _store_memory(self, event, intensity):

        self.memory_trace.append({
            "event": event,
            "intensity": intensity,
            "t": time.time()
        })