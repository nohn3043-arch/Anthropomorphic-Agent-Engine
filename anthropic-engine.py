from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable
import math
import time

@dataclass
class AICharacterProfile:
    name: str
    age: int
    relationship: str
    job_identity: str

    # --- 核心人格配置 ---
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    exclusive_groups: List[List[str]] = field(default_factory=list)
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [], "fallback": []
    })
    emotion_coupling_matrix: Dict[str, Dict[str, Callable[[float, float], float]]] = field(default_factory=dict)

    # --- 生命系统变量 ---
    affinity: float = 0.0               
    energy: float = 100.0               
    last_interaction_time: float = field(default_factory=time.time)
    trauma_tags: List[str] = field(default_factory=list)  
    trauma_recovery: Dict[str, float] = field(default_factory=dict)  

    # --- 上下文环境 ---
    current_context: Dict[str, str] = field(default_factory=lambda: {
        "scene": "default",    
        "target": "default"    
    })

    # --- 流体动态系统 ---
    fluid_state: Dict[str, float] = field(default_factory=dict)
    base_viscosity: float = 0.3                                

    # ==========================================
    # 状态更新逻辑
    # ==========================================
    def update_state(self, is_intense_action: bool = False):
        current_time = time.time()
        
        # 1. 时间衰减：基础值回归
        days_passed = (current_time - self.last_interaction_time) / 86400
        decay_factor = math.exp(-0.1 * days_passed)  

        for tag, info in self.psychology_matrix.items():
            original_start = info.get('base_start', info.get('start_weight', 1.0))
            current_start = info.get('start_weight', original_start)
            info['start_weight'] = original_start + (current_start - original_start) * decay_factor

        # 2. 能量管理
        if is_intense_action:
            self.energy = max(0.0, self.energy - 25.0)
            for trauma in self.trauma_recovery:
                self.trauma_recovery[trauma] = min(1.0, self.trauma_recovery[trauma] + 0.08)
        else:
            self.energy = min(100.0, self.energy + 12.0)

        # 3. 创伤修复
        if "betrayal_trauma" in self.trauma_tags and self.trauma_recovery.get("betrayal_trauma", 0.0) >= 1.0:
            self.trauma_tags.remove("betrayal_trauma")
            print(f"✅【创伤修复】{self.name} 已重建信任。")

        self.last_interaction_time = current_time

    # ==========================================
    # 事件触发器
    # ==========================================
    def trigger_trauma(self, event_name: str):
        if event_name == "betrayal" and "betrayal_trauma" not in self.trauma_tags:
            self.trauma_tags.append("betrayal_trauma")
            self.trauma_recovery["betrayal_trauma"] = 0.0
            self.affinity = max(0.05, self.affinity - 0.4)
            print(f"⚠️【人格变异】{self.name} 经历信任危机！")
        elif event_name == "loss" and "loss_trauma" not in self.trauma_tags:
            self.trauma_tags.append("loss_trauma")

    def trigger_recovery_event(self, event_name: str):
        if event_name == "transparency_communication" and "betrayal_trauma" in self.trauma_tags:
            self.trauma_recovery["betrayal_trauma"] = min(1.0, self.trauma_recovery.get("betrayal_trauma", 0.0) + 0.15)

    def set_context(self, scene: str = "default", target: str = "default"):
        self.current_context["scene"] = scene
        self.current_context["target"] = target

    # ==========================================
    # 动态区间计算（情绪河床）
    # ==========================================
    def _get_dynamic_intervals(self, tag: str, info: Dict[str, Any]) -> tuple[float, float, float]:
        start = info.get('start_weight', 1.0)
        end = info.get('end_weight', 1.0)
        threshold = info.get('threshold', 0.0)

        # 能量挤压效应
        if self.energy < 30:
            if any(k in tag for k in ["热情", "耐心", "温柔", "克制", "信任"]):
                end *= max(0.1, self.energy / 30.0)
            if any(k in tag for k in ["暴躁", "冷漠", "自我", "戒备"]):
                threshold *= 0.5 

        # 创伤地形扭曲
        if "betrayal_trauma" in self.trauma_tags:
            recovery = self.trauma_recovery.get("betrayal_trauma", 0.0)
            impact = 1.0 - recovery
            
            if any(k in tag for k in ["信任", "依赖", "纵容"]):
                end *= (1.0 - impact * 0.8)
                threshold += 0.3 * impact
            
            if any(k in tag for k in ["高冷", "戒备", "理性"]):
                start += 1.5 * impact
                end += 2.0 * impact

        return start, end, threshold

    # ==========================================
    # 目标水位计算
    # ==========================================
    def _calculate_target_weights(self) -> Dict[str, float]:
        target_weights = {}
        current_scene = self.current_context["scene"]
        current_target = self.current_context["target"]

        for tag, info in self.psychology_matrix.items():
            effective_scenes = info.get("effective_scene", ["default"])
            forbidden_scenes = info.get("forbidden_scene", [])
            effective_targets = info.get("effective_target", ["default"])

            if current_scene in forbidden_scenes: continue
            if current_scene not in effective_scenes and "default" not in effective_scenes: continue
            if current_target not in effective_targets and "default" not in effective_targets: continue

            start, end, threshold = self._get_dynamic_intervals(tag, info)
            sensitivity = info.get('sensitivity', 1.0)

            if self.affinity < threshold:
                target_weights[tag] = 0.0
                continue

            range_width = max(0.001, 1.0 - threshold)
            progress = max(0.0, min(1.0, (self.affinity - threshold) / range_width))
            
            target = start + (end - start) * progress * sensitivity
            target_weights[tag] = round(max(0.0, target), 3)

        return target_weights

    # ==========================================
    # 流体演化核心
    # ==========================================
    def flow_psychology_fluids(self, delta_time: float = 1.0):
        target_weights = self._calculate_target_weights()
        
        # 1. 应用情绪耦合调制
        for source_tag, targets in self.emotion_coupling_matrix.items():
            source_level = self.fluid_state.get(source_tag, 0.0)
            for target_tag, mod_func in targets.items():
                if target_tag in target_weights:
                    target_weights[target_tag] = mod_func(source_level, target_weights[target_tag])

        # 2. 二阶情绪自动生成
        second_order_map = {
            "绝对占有欲": ("自我厌恶", 0.8),
            "天皇真焰": ("背德负罪感", 0.9),
            "九幽凛冰": ("天皇真焰", 0.7),
            "爱意": ("恐惧", 0.7)
        }
        for first_order, (second_order, factor) in second_order_map.items():
            if first_order in self.fluid_state and second_order in self.psychology_matrix:
                generated_level = self.fluid_state[first_order] * factor * 0.1 * delta_time
                max_level = self.psychology_matrix[second_order].get('end_weight', 1.0)
                self.fluid_state[second_order] = min(
                    max_level,
                    self.fluid_state.get(second_order, 0.0) + generated_level
                )

        # 3. 流体平滑流动
        energy_factor = max(0.1, self.energy / 100.0)
        alpha = (1.0 - self.base_viscosity) * energy_factor * delta_time
        alpha = min(1.0, max(0.01, alpha))

        for tag in self.psychology_matrix.keys():
            current_level = self.fluid_state.get(tag, 0.0)
            target_level = target_weights.get(tag, 0.0)
            new_level = current_level + alpha * (target_level - current_level)
            self.fluid_state[tag] = round(max(0.0, new_level), 3)

        # 4. 互斥组双向博弈虹吸
        self._apply_fluid_spillover()

    def _apply_fluid_spillover(self):
        for group in self.exclusive_groups:
            group_levels = {tag: self.fluid_state.get(tag, 0.0) for tag in group if tag in self.fluid_state}
            if len(group_levels) < 2: continue
            
            sorted_tags = sorted(group_levels.keys(), key=lambda x: group_levels[x], reverse=True)
            leader, follower = sorted_tags[0], sorted_tags[1]
            leader_level, follower_level = group_levels[leader], group_levels[follower]
            
            gap = leader_level - follower_level
            siphon_rate = 0.1 + 0.4 * max(0.0, gap)
            
            siphon_amount = follower_level * siphon_rate
            self.fluid_state[follower] -= siphon_amount
            self.fluid_state[leader] += siphon_amount * 0.7

    # ==========================================
    # Prompt输出
    # ==========================================
    def _get_stage_label(self) -> str:
        if self.affinity < 0.2: base = "敌对排斥 / 完全理性"
        elif self.affinity < 0.45: base = "商务社交 / 面具人格"
        elif self.affinity < 0.55: base = "基准平衡 / 内心动摇"
        elif self.affinity < 0.8: base = "情感主导 / 底线松动"
        else: base = "本能支配 / 理智下线"

        energy_state = "【精力充沛】" if self.energy > 70 else ("【身心疲惫】" if self.energy < 30 else "【状态平稳】")
        trauma_state = " ⚠️【创伤激活】" if self.trauma_tags else ""
        return f"{base} | {energy_state}{trauma_state}"

    def to_ai_prompt(self) -> str:
        self.flow_psychology_fluids(delta_time=1.0)
        
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"【当前状态】：{self._get_stage_label()} (亲密度: {self.affinity:.2f} | 能量: {self.energy:.0f}/100)",
            "【核心规则】：心理权重为流体动态水位，受场景、疲劳、创伤共同影响。数值越高，表现越强烈。矛盾情绪绝对并发不互斥。",
            "\n【实时心理水位图】"
        ]

        active_traits = {k: v for k, v in self.fluid_state.items() if v > 0.05}
        for tag, level in sorted(active_traits.items(), key=lambda item: item[1], reverse=True):
            info = self.psychology_matrix.get(tag, {})
            desc = info.get('description', '内在情绪')
            prompt.append(f"- {tag}: {level:.2f} | {desc}")

        if self.behavior_rules['fallback']:
            prompt.append("\n【行为准则】\n- " + "\n- ".join(self.behavior_rules['fallback']))
        if self.behavior_rules['forbidden']:
            prompt.append("\n【绝对禁止】\n- " + "\n- ".join(self.behavior_rules['forbidden']))

        return "\n".join(prompt)
