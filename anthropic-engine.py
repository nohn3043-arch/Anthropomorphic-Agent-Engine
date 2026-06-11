from dataclasses import dataclass, field
from typing import Dict, Any, List
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

    # --- 新增：流体动态与区间参数系统 ---
    fluid_state: Dict[str, float] = field(default_factory=dict)  # 记录当前情绪的真实流体水位
    base_viscosity: float = 0.3                                  # 基础情绪粘滞度 (0=瞬间改变, 接近1=极度迟缓)

    # ==========================================
    # 状态更新逻辑（时间衰减 + 疲劳 + 创伤）
    # ==========================================
    def update_state(self, is_intense_action: bool = False):
        current_time = time.time()
        
        # 1. 时间衰减：影响心理矩阵的基础值回归
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

        # 完全修复则移除创伤标记
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
    # 核心步骤 1：计算【动态区间】 (Dynamic Intervals)
    # 情绪的上限、下限和门槛，会随状态动态呼吸缩放
    # ==========================================
    def _get_dynamic_intervals(self, tag: str, info: Dict[str, Any]) -> tuple[float, float, float]:
        """返回动态调整后的 (start_weight, end_weight, threshold)"""
        start = info.get('start_weight', 1.0)
        end = info.get('end_weight', 1.0)
        threshold = info.get('threshold', 0.0)

        # --- 能量区间的动态挤压 ---
        if self.energy < 30:
            # 疲惫时，消耗能量的正面情绪上限大幅缩水
            if any(k in tag for k in ["热情", "耐心", "温柔", "克制"]):
                end *= max(0.1, self.energy / 30.0)
            # 疲惫时，负面或本能情绪的触发门槛降低
            if any(k in tag for k in ["暴躁", "冷漠", "直率", "自我"]):
                threshold *= 0.5 

        # --- 创伤区间的动态偏移 ---
        if "betrayal_trauma" in self.trauma_tags:
            recovery = self.trauma_recovery.get("betrayal_trauma", 0.0)
            impact = 1.0 - recovery  # 受创伤影响的程度
            
            # 信任类情绪的上限被死死锁住，且门槛变高
            if any(k in tag for k in ["信任", "依赖", "纵容"]):
                end *= (1.0 - impact * 0.8) # 创伤严重时，上限仅剩20%
                threshold += 0.3 * impact
            
            # 防御类情绪的基础值（下限）抬高
            if any(k in tag for k in ["高冷", "戒备", "理性"]):
                start += 1.5 * impact
                end += 2.0 * impact

        return start, end, threshold

    # ==========================================
    # 核心步骤 2：计算流体目标水位
    # ==========================================
    def _calculate_target_weights(self) -> Dict[str, float]:
        target_weights = {}
        current_scene = self.current_context["scene"]
        current_target = self.current_context["target"]

        for tag, info in self.psychology_matrix.items():
            # 场景/对象过滤
            effective_scenes = info.get("effective_scene", ["default"])
            forbidden_scenes = info.get("forbidden_scene", [])
            effective_targets = info.get("effective_target", ["default"])

            if current_scene in forbidden_scenes: continue
            if current_scene not in effective_scenes and "default" not in effective_scenes: continue
            if current_target not in effective_targets and "default" not in effective_targets: continue

            # 获取动态缩放后的区间参数
            start, end, threshold = self._get_dynamic_intervals(tag, info)
            sensitivity = info.get('sensitivity', 1.0)

            # 低于动态门槛，目标水位直接为 0
            if self.affinity < threshold:
                target_weights[tag] = 0.0
                continue

            # 进度归一化并计算最终目标值
            range_width = max(0.001, 1.0 - threshold)
            progress = max(0.0, min(1.0, (self.affinity - threshold) / range_width))
            
            target = start + (end - start) * progress * sensitivity
            target_weights[tag] = round(max(0.0, target), 3)

        return target_weights

    # ==========================================
    # 核心步骤 3：流体演化与溢出
    # ==========================================
    def flow_psychology_fluids(self, delta_time: float = 1.0):
        target_weights = self._calculate_target_weights()
        
        # 能量驱动流速：疲惫时，情绪转变会变得麻木迟缓
        energy_factor = max(0.1, self.energy / 100.0)
        alpha = (1.0 - self.base_viscosity) * energy_factor * delta_time
        alpha = min(1.0, max(0.01, alpha))

        # 流体平滑过渡逼近目标
        for tag in self.psychology_matrix.keys():
            current_level = self.fluid_state.get(tag, 0.0)
            target_level = target_weights.get(tag, 0.0)
            new_level = current_level + alpha * (target_level - current_level)
            self.fluid_state[tag] = round(max(0.0, new_level), 3)

        # 情绪溢出与互斥组连通器
        self._apply_fluid_spillover()

    def _apply_fluid_spillover(self):
        """处理互斥组的情绪连通器（次要情绪向主导情绪输送能量）"""
        for group in self.exclusive_groups:
            group_levels = {tag: self.fluid_state.get(tag, 0.0) for tag in group if tag in self.fluid_state}
            if not group_levels: continue
            
            leader = max(group_levels, key=group_levels.get)
            leader_level = group_levels[leader]
            
            for follower, level in group_levels.items():
                if follower != leader and level > 0.1:
                    siphon_amount = level * 0.3  # 虹吸现象：吸走30%
                    self.fluid_state[follower] -= siphon_amount
                    self.fluid_state[leader] += siphon_amount * 0.6 # 能量转化损耗

    # ==========================================
    # Prompt 输出组装
    # ==========================================
    def _get_stage_label(self) -> str:
        if self.affinity < 0.2: base = "敌对排斥 / 完全理性"
        elif self.affinity < 0.45: base = "商务社交 / 面具人格"
        elif self.affinity < 0.55: base = "基准平衡 / 内心动摇"
        elif self.affinity < 0.8: base = "情感主导 / 底线松动"
        else: base = "本能支配 / 理智下线"

        energy_state = "【精力充沛】" if self.energy > 70 else ("【身心疲惫】" if self.energy < 30 else "【状态平稳】")
        return f"{base} | {energy_state}"

    def to_ai_prompt(self) -> str:
        # 在输出 Prompt 前，驱动流体更新一次 (假设默认时间跨度为1)
        self.flow_psychology_fluids(delta_time=1.0)
        
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"【当前状态】：{self._get_stage_label()} (亲密度: {self.affinity:.2f} | 能量: {self.energy:.0f}/100)",
            "【核心规则】：以下心理权重受当前场景、角色疲劳度与过往创伤的流体动态影响。数值越高，表现越强烈。",
            "\n【实时心理水位图】"
        ]

        # 仅输出水池中有水（水位大于0.05）的特质
        active_traits = {k: v for k, v in self.fluid_state.items() if v > 0.05}
        # 按水位高低排序，帮助大模型抓重点
        for tag, level in sorted(active_traits.items(), key=lambda item: item[1], reverse=True):
            info = self.psychology_matrix.get(tag, {})
            desc = info.get('description', '内在情绪')
            prompt.append(f"- {tag}: {level:.2f} | {desc}")

        if self.behavior_rules['fallback']:
            prompt.append("\n【行为准则】\n- " + "\n- ".join(self.behavior_rules['fallback']))
        if self.behavior_rules['forbidden']:
            prompt.append("\n【绝对禁止】\n- " + "\n- ".join(self.behavior_rules['forbidden']))

        return "\n".join(prompt)

# --- 测试用例 (保留给你参考) ---
if __name__ == "__main__":
    profile = AICharacterProfile(
        name="林总", age=30, relationship="上司", job_identity="严格的执行官"
    )
    profile.psychology_matrix = {
        "戒备": {"start_weight": 2.0, "end_weight": 0.5, "threshold": 0.0, "description": "对下属的防备"},
        "信任": {"start_weight": 0.0, "end_weight": 3.0, "threshold": 0.3, "description": "业务上的认可"},
        "耐心": {"start_weight": 1.0, "end_weight": 2.0, "threshold": 0.1, "description": "指导工作时的态度"}
    }
    profile.exclusive_groups = [["戒备", "信任"]]

    # 模拟交互推进
    profile.set_affinity(0.4)
    print("=== 第一天：状态良好，亲密度 0.4 ===")
    print(profile.to_ai_prompt())

    print("\n=== 第二天：极度疲劳，遭遇背叛！ ===")
    profile.energy = 15  # 极度疲劳
    profile.trigger_trauma("betrayal")
    print(profile.to_ai_prompt())
