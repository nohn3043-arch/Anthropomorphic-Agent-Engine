import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple

@dataclass
class SPLUnifiedEngineV7_2:
    """
    SPL 通用流体非线性动力引擎 V7.2
    拟人非线性计算核心 —— 整合记忆重巩固、认知扭曲、压抑反噬、信任不可逆、心理时间等多稳态动力学。
    """

    # ========== 核心元变量 ==========
    psychological_resilience: float = 0.5
    energy: float = 100.0
    affinity: float = 0.5
    last_time: float = field(default_factory=time.time)

    # ========== 流体场状态空间 ==========
    trauma_state: Dict[str, float] = field(default_factory=dict)
    event_history: List[Dict[str, Any]] = field(default_factory=list)

    fluid: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })

    fluid_target: Dict[str, float] = field(default_factory=lambda: {
        "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
        "信任": 0.5, "疏离": 0.2, "张力": 0.2, "愧疚": 0.0
    })

    viscosity: float = 0.35
    inertia: float = 0.8

    # ========== V7.2 新增：拟人非线性维度 ==========
    # 记忆痕迹库
    memory_traces: List[Dict[str, Any]] = field(default_factory=list)
    # 压抑负荷 (0~1)
    suppression_load: float = 0.0
    # 信任最大容量 (初始1.0，可被创伤侵蚀)
    max_trust: float = 1.0
    # 隐式压力累积 (不直接外显，达到阈值后爆发)
    latent_pressure: float = 0.0
    # 心理时间压缩系数基准
    time_compress_base: float = 0.0

    # ========== 1. 认知评价扭曲 ==========
    def _cognitive_appraisal(self, event: str, intensity: float) -> Tuple[str, float]:
        """
        基于当前能量、韧性、创伤激活程度的认知滤镜。
        返回修正后的 (event, perceived_intensity)。
        """
        # 创伤激活总量
        activated_trauma = sum(self.trauma_state.values())
        # 能量比率
        e_ratio = self.energy / 100.0
        # 扭曲系数：低能 + 高韧性耗竭 -> 更多负向扭曲
        bias = (0.5 - e_ratio) * 2.0 + activated_trauma * 0.5
        # 使用双曲正切限制扭曲幅度在 -0.5~0.5
        distortion = 0.5 * math.tanh(bias)
        
        # 中性/轻微事件可能被重新解释
        if event in ["compliment"]:
            # 负向扭曲：可能觉得对方别有用心
            if distortion < -0.3:
                return ("insult", intensity * 0.7)
        elif event in ["insult", "betrayal"]:
            # 已经脆弱的系统会放大敌意强度
            if distortion > 0.2:
                intensity *= (1.0 + distortion * 1.5)
        elif event == "rest":
            # 高张力时休息效率打折
            if self.fluid.get("张力", 0.0) > 0.6:
                intensity *= 0.5
        
        # 通用强度扭曲
        perceived_intensity = intensity * (1.0 + distortion * 0.3)
        # 限制强度在合理范围
        perceived_intensity = max(0.0, min(2.0, perceived_intensity))
        return event, perceived_intensity

    # ========== 2. 记忆重巩固机制 ==========
    def _memory_reconsolidation(self, event: str, intensity: float):
        """
        当事件与旧伤模式匹配时，旧记忆被激活并进入不稳定状态，
        可能加剧或消退（取决于当前支持/安全感）。
        """
        current_time = self.last_time
        # 安全感指数（信任高、恐惧低）
        safety = self.fluid.get("信任", 0.5) * (1.0 - self.fluid.get("恐惧", 0.0))
        
        for trace in self.memory_traces:
            # 简单匹配：事件类型相同，且强度超过一定值
            if trace["type"] == event and intensity > 0.3:
                # 时间衰减因子：越近的记忆影响越大
                dt = current_time - trace["timestamp"]
                recency = 1.0 / (1.0 + 0.1 * dt)  # 约10秒衰减一半（可根据需要调整时间尺度）
                
                # 激活强度：原始强度 * 重现强度 * 时间因子
                activation = trace["intensity"] * intensity * recency
                
                if safety > 0.5:
                    # 有安全感时，再巩固可能让记忆消退
                    decay = activation * 0.2 * (safety - 0.5) * 2.0
                    trace["intensity"] = max(0.0, trace["intensity"] - decay)
                    # 减缓相关创伤状态
                    if trace["type"] in self.trauma_state:
                        self.trauma_state[trace["type"]] -= decay * 0.5
                        self.trauma_state[trace["type"]] = max(0.0, self.trauma_state[trace["type"]])
                else:
                    # 缺乏安全感，记忆强化
                    boost = activation * 0.3 * (0.5 - safety) * 2.0
                    trace["intensity"] = min(1.0, trace["intensity"] + boost)
                    # 强化创伤状态
                    if trace["type"] in self.trauma_state:
                        self.trauma_state[trace["type"]] = min(1.0, self.trauma_state[trace["type"]] + boost * 0.5)

                # 更新重激活时间戳
                trace["timestamp"] = current_time

    # ========== 3. 压抑–反弹机制 ==========
    def _suppression_dynamics(self):
        """
        检测流体目标与实际值的偏差，差异被压抑负荷吸收，
        负荷过高时暴力反弹释放。
        """
        # 主要针对负面情绪（愤怒、恐惧、愧疚）的压抑
        for key in ["愤怒", "恐惧", "愧疚"]:
            diff = self.fluid[key] - self.fluid_target.get(key, 0.0)
            if diff > 0.1:
                # 压抑负荷增加，同时降低外显 fluid（强行压制）
                absorb = diff * 0.4
                self.suppression_load += absorb
                self.fluid[key] -= absorb
                # 压抑耗费能量
                self.energy -= absorb * 2.0
                self.energy = max(0.0, self.energy)

        # 负荷临界值：超过阈值则爆发
        if self.suppression_load > 0.5:
            # 爆发注入到所有负面流体
            burst = self.suppression_load * 2.0
            for k in ["愤怒", "恐惧", "愧疚", "张力"]:
                self.fluid[k] = min(1.0, self.fluid[k] + burst * 0.25)
            # 爆发后快速消耗负荷
            self.suppression_load *= 0.3
            # 一次爆发大幅损耗能量
            self.energy -= burst * 3.0
            self.energy = max(0.0, self.energy)

    # ========== 4. 信任容量不可逆损伤 ==========
    def _update_max_trust(self, event: str):
        if event == "betrayal":
            # 每次背叛永久降低最大信任容量
            self.max_trust *= 0.92
            self.max_trust = max(0.1, self.max_trust)
        elif event == "compliment":
            # 正面连续互动缓慢修复容量（对数修复）
            if self.max_trust < 1.0:
                self.max_trust += 0.01 * math.log(1.0 + self.fluid.get("信任", 0.0) * 10)
                self.max_trust = min(1.0, self.max_trust)
        # 确保当前信任目标不超过容量
        if self.fluid_target["信任"] > self.max_trust:
            self.fluid_target["信任"] = self.max_trust

    # ========== 5. 隐式压力累积–雪崩爆发 ==========
    def _latent_pressure_trigger(self):
        # 日常负面事件增加隐压
        pressure_from_fluid = (self.fluid.get("张力", 0.0) + self.fluid.get("恐惧", 0.0)) * 0.3
        self.latent_pressure += pressure_from_fluid * 0.5
        # 爆发阈值：双重门槛（韧性与能量）
        threshold = 0.6 * (2.0 - self.psychological_resilience) * (self.energy / 100.0 + 0.5)
        if self.latent_pressure > threshold:
            # 雪崩：瞬间注入大量负面情绪
            self.fluid["愤怒"] = min(1.0, self.fluid["愤怒"] + self.latent_pressure * 1.5)
            self.fluid["恐惧"] = min(1.0, self.fluid["恐惧"] + self.latent_pressure * 1.2)
            self.fluid["张力"] = min(1.0, self.fluid["张力"] + self.latent_pressure * 0.8)
            self.latent_pressure = 0.1 * self.latent_pressure  # 重置但残留
            # 爆发后易激惹期：阈值临时降低（通过增大下次累积速度实现，这里简单处理）
            self.time_compress_base += 0.2  # 心理时间加速，恶化反应

    # ========== 6. 心理时间扭曲 ==========
    def _psychological_dt(self) -> float:
        """根据当前系统压力动态返回演化的心理时间步长"""
        system_pressure = self.fluid.get("张力", 0.0) + self.fluid.get("恐惧", 0.0) + self.fluid.get("愧疚", 0.0)
        # 高压力时心理时间加速
        compress = 1.0 + 0.5 * math.tanh(system_pressure * 2.0) + self.time_compress_base
        # 低能时时间变慢（行动迟钝）但情感演化可能不变，这里仅调演化速度
        if self.energy < 20.0:
            compress *= 0.7
        return max(0.3, min(3.0, compress))

    # ========== 7. 能量自然代谢 ==========
    def _natural_energy_recovery(self):
        """即便无事件，也存在缓慢的生理恢复"""
        if self.energy < 100.0:
            self.energy += 0.2 * (1.0 - self.fluid.get("张力", 0.0)) * (self.psychological_resilience)
            self.energy = min(100.0, self.energy)

    # ========== 重载原有核心算子 ==========
    def _calculate_nonlinear_trauma(self, intensity: float) -> float:
        total_trauma = sum(self.trauma_state.values())
        resilience_factor = 1.0 / (1.0 + self.psychological_resilience * 2.0)
        collapse_multiplier = 1.0 + math.exp(total_trauma * 2.0) * 0.1
        return intensity * resilience_factor * collapse_multiplier

    def _update_dynamic_viscosity(self):
        system_pressure = self.fluid.get("张力", 0.0) + self.fluid.get("恐惧", 0.0) + self.fluid.get("愧疚", 0.0)
        self.viscosity = 0.3 + 0.6 * math.tanh(system_pressure * 1.5)
        self.viscosity = min(0.95, self.viscosity)

    def _energy_dynamics(self, event: str, intensity: float):
        system_pressure = self.fluid.get("张力", 0.0) + self.fluid.get("愧疚", 0.0)
        if system_pressure > self.psychological_resilience:
            drain = math.pow((system_pressure - self.psychological_resilience) * 6.0, 2)
            self.energy -= drain

        if event in ["compliment", "rest"]:
            self.energy += 2.0 * intensity
        elif event in ["insult", "betrayal"]:
            self.energy -= 5.0 * intensity

        self.energy = max(0.0, min(100.0, self.energy))

    def _event_to_fluid(self, event: str, intensity: float):
        if event == "compliment":
            self.fluid["喜悦"] += 0.15 * intensity
            self.fluid["信任"] += 0.05 * intensity
        elif event == "insult":
            self.fluid["愤怒"] += 0.25 * intensity
            self.fluid["张力"] += 0.15 * intensity
        elif event == "betrayal":
            self.fluid["恐惧"] += 0.3 * intensity
            self.fluid["疏离"] += 0.2 * intensity
            self.fluid["信任"] -= 0.4 * intensity

        for k in self.fluid:
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))

    def _fluid_dynamics(self, dt: float = 1.0):
        alpha = (1.0 - self.viscosity) * (self.energy / 100.0)
        for k in self.fluid:
            target = self.fluid_target.get(k, 0.0)
            self.fluid[k] += alpha * (target - self.fluid[k]) * dt
            self.fluid[k] = max(0.0, min(1.0, self.fluid[k]))

    def _fluid_to_spl_feedback(self):
        if self.fluid.get("恐惧", 0.0) > 0.6:
            self.fluid_target["信任"] = max(0.0, self.fluid_target.get("信任", 0.5) - 0.05)
        if self.fluid.get("张力", 0.0) > 0.7:
            self.energy -= 3.0

    # ========== 核心因果链路 (重写) ==========
    def process_event(self, event: str, intensity: float = 1.0):
        self.last_time = time.time()
        self.event_history.append({"event": event, "intensity": intensity, "t": self.last_time})

        # ---- V7.2 前置：认知扭曲 ----
        event_actual, perceived_intensity = self._cognitive_appraisal(event, intensity)

        # ---- 记忆重巩固 (利用原始事件类型) ----
        self._memory_reconsolidation(event_actual, perceived_intensity)

        # ---- 信任容量更新 ----
        self._update_max_trust(event_actual)

        # ---- 创伤判定与非线性注入 ----
        if event_actual in ["betrayal", "insult", "loss"] and perceived_intensity > (1.0 - self.psychological_resilience):
            actual_damage = self._calculate_nonlinear_trauma(perceived_intensity)
            self.trauma_state[event_actual] = min(1.0, self.trauma_state.get(event_actual, 0.0) + actual_damage)
            # 记录到记忆痕迹库
            self.memory_traces.append({
                "type": event_actual,
                "intensity": actual_damage,
                "timestamp": self.last_time
            })

        # ---- 隐式压力累积 ----
        self._latent_pressure_trigger()

        # ---- 离散事件映射流体场 ----
        self._event_to_fluid(event_actual, perceived_intensity)

        # ---- 动态粘滞度 ----
        self._update_dynamic_viscosity()

        # ---- 压抑动态 ----
        self._suppression_dynamics()

        # ---- 心理时间步长 ----
        psy_dt = self._psychological_dt()

        # ---- 流体动力学演化 ----
        self._fluid_dynamics(dt=psy_dt)

        # ---- 流体场反馈 ----
        self._fluid_to_spl_feedback()

        # ---- 能量核算 ----
        self._energy_dynamics(event_actual, perceived_intensity)

        # ---- 自然代谢 ----
        self._natural_energy_recovery()

        # 时间系数衰减（缓慢归零）
        self.time_compress_base *= 0.95

    # ========== 状态快照 ==========
    def snapshot(self) -> str:
        dominant = sorted(self.fluid.items(), key=lambda x: x[1], reverse=True)
        trauma_str = ", ".join([f"{k}:{v:.2f}" for k, v in self.trauma_state.items()]) or "无"
        return "\n".join([
            "=== V7.2 拟人非线性拓扑状态快照 ===",
            f"物理能量: {self.energy:.1f}/100 | 动态粘滞度: {self.viscosity:.2f}",
            f"心理承受阈值(Resilience): {self.psychological_resilience:.2f}",
            f"主导流体水位: {dominant[0][0]}({dominant[0][1]:.2f}) | {dominant[1][0]}({dominant[1][1]:.2f})",
            f"深层创伤节点: {trauma_str}",
            f"压抑负荷: {self.suppression_load:.2f} | 信任最大容量: {self.max_trust:.2f}",
            f"隐式压力: {self.latent_pressure:.2f} | 心理时间压缩: {self.time_compress_base:.2f}",
            f"记忆痕迹数: {len(self.memory_traces)} | 近5条创伤: {[t['type']+'('+str(round(t['intensity'],2))+')' for t in self.memory_traces[-5:]]}"
        ])