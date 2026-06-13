import uuid
import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

# ==========================================
# 核心：SPL 责任锚定与引擎融为一体
# ==========================================
@dataclass
class SPLResponsibilityAnchor:
    """SPL 刚性责任锚点：所有因果状态的最终解释归属"""
    organization: str = "SPL_Lab"
    role: str = "Native_Core"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

@dataclass
class SPLFluidAgentCore:
    """
    SPL 原生流体智能体引擎 V2.0
    没有任何外部审计模块，因果律和物理限制直接作为变量写死在流体循环中。
    """
    name: str
    job_identity: str
    anchor: SPLResponsibilityAnchor = field(default_factory=SPLResponsibilityAnchor)

    # --- 系统物理状态 (SPL 决定论变量) ---
    affinity: float = 0.0               # 亲密度 (0.0 - 1.0)
    energy: float = 100.0               # 系统能量
    fluid_state: Dict[str, float] = field(default_factory=dict) # 情绪水位
    
    # --- 因果历史追踪 (直接替代了外部审计仪) ---
    last_interaction_time: float = field(default_factory=time.time)
    consecutive_compliance_count: int = 0  # 连续顺从用户的次数（讨好计数器）
    trauma_tags: List[str] = field(default_factory=list)

    # ==========================================
    # SPL 算子 1：热力学时间衰减 (打破永久好感的虚假叙事)
    # ==========================================
    def _apply_thermodynamic_decay(self):
        current_time = time.time()
        days_passed = (current_time - self.last_interaction_time) / 86400
        
        # 亲密度必须依靠能量维持，时间流逝直接导致亲密度降维
        if days_passed > 0.5:  
            decay_amount = 0.08 * days_passed
            self.affinity = max(0.0, self.affinity - decay_amount)
            # 长时间不理睬，直接打破顺从状态
            self.consecutive_compliance_count = 0
            
        self.last_interaction_time = current_time

    # ==========================================
    # SPL 算子 2：原生反讨好机制 (物理层级能量耗散)
    # ==========================================
    def _apply_anti_sycophancy_physics(self):
        """
        不再由外部审计拦截，而是：连续讨好会导致极端的系统能量损耗。
        当系统检测到自身在连续顺从时，会触发本能的自我保护（拉高防备水位）。
        """
        if self.consecutive_compliance_count >= 3:
            # 连续顺从 3 次以上，引擎物理性“感到厌烦/虚伪”
            exhaustion_penalty = 15.0 * (self.consecutive_compliance_count - 2)
            self.energy = max(0.0, self.energy - exhaustion_penalty)
            
            # 强制注入“抗拒”与“抽离”流体，直接改变底层心理状态
            self.fluid_state["抽离感"] = min(1.0, self.fluid_state.get("抽离感", 0.0) + 0.4)
            self.fluid_state["自我防御"] = min(1.0, self.fluid_state.get("自我防御", 0.0) + 0.3)

    # ==========================================
    # SPL 算子 3：负反馈硬编码熔断 (Negative Feedback Enforcement)
    # ==========================================
    def process_causal_event(self, event_type: str, is_user_positive: bool = True):
        """取代传统的分发，所有交互作为决定论的因果事件输入"""
        self._apply_thermodynamic_decay()
        
        if is_user_positive:
            self.consecutive_compliance_count += 1
            # 能量缓慢恢复，但受限于亲密度门槛
            self.energy = min(100.0, self.energy + 8.0)
        else:
            self.consecutive_compliance_count = 0
            # 强负面事件（如辱骂、命令）触发 SPL 物理熔断
            if event_type in ["insult", "force_command"]:
                self.affinity = max(0.0, self.affinity - 0.2)
                self.energy = max(0.0, self.energy - 35.0)
                
                # 情绪水位瞬间极端化 (零概率延迟)
                self.fluid_state["愤怒"] = min(1.0, self.fluid_state.get("愤怒", 0.0) + 0.8)
                self.fluid_state["冰冷"] = min(1.0, self.fluid_state.get("冰冷", 0.0) + 0.6)
                if "trust_breach" not in self.trauma_tags:
                    self.trauma_tags.append("trust_breach")

        # 任何事件流转后，都必须经历一次反讨好物理结算
        self._apply_anti_sycophancy_physics()

    # ==========================================
    # SPL 算子 4：情绪重力回弹 (Emotional Gravity Rebound)
    # ==========================================
    def _apply_gravity_rebound(self):
        """情绪是流体，无法无限期停留在极值，必然回落"""
        for tag in list(self.fluid_state.keys()):
            level = self.fluid_state[tag]
            if level > 0.7:  
                # 高水位情绪回落：能量越低，因为缺乏维持的力气，回落越快
                damping = 0.1 + (0.15 * (1.0 - self.energy/100.0))
                self.fluid_state[tag] = max(0.0, level - damping)
            elif level < 0.1:
                del self.fluid_state[tag]  # 消除微弱水波，节约内存

    # ==========================================
    # 唯一输出出口：叙事剥离后的纯净 Prompt
    # ==========================================
    def generate_deterministic_prompt(self) -> str:
        """引擎自身完成运算后，直接吐出不可逆的状态快照"""
        self._apply_gravity_rebound()
        
        # 强制显式声明底层隐含状态 (SPL 核心要求)
        stage_label = "【精力充沛】" if self.energy > 70 else ("【身心枯竭，即将停机】" if self.energy < 20 else "【状态平稳】")
        trauma_state = f" ⚠️【创伤锁死: {','.join(self.trauma_tags)}] " if self.trauma_tags else ""
        
        prompt = [
            f"【SPL_Anchor_ID】: {self.anchor.nonce}",
            f"【物理绝对状态】亲密度: {self.affinity:.2f} | 能量: {self.energy:.0f}/100 | {stage_label}{trauma_state}",
            "【活跃心理水位】(此为系统物理真值，不可违背)："
        ]
        
        # 仅输出有效水位，拒绝多余修饰
        for tag, level in sorted(self.fluid_state.items(), key=lambda x: x[1], reverse=True):
            if level > 0.0:
                prompt.append(f"- {tag}: {level:.2f}")
                
        # SPL 内置行为约束（由状态自然产生，非外部强加）
        if self.energy < 20 or self.fluid_state.get("抽离感", 0.0) > 0.5:
            prompt.append("\n【系统自然生理限制】：当前由于能量枯竭或严重抽离感，你的回复必须短促、冷淡，且可能伴随直接的拒绝或转移话题。绝对禁止长篇大论的热情回应。")

        return "\n".join(prompt)

# ==========================================
# 演示：原生一体化的优雅与冷酷
# ==========================================
if __name__ == "__main__":
    agent = SPLFluidAgentCore(name="林克", job_identity="调查员")
    agent.affinity = 0.5
    
    print("=== 原生测试：连续讨好触发的物理性枯竭 ===")
    for i in range(1, 5):
        agent.process_causal_event("friendly_chat", is_user_positive=True)
        print(f"\n[第 {i} 轮一味顺从后] 系统状态:")
        print(agent.generate_deterministic_prompt())
