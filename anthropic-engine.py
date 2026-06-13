import uuid
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

# ==========================================
# 模块 1：责任锚定 (决定论身份标识)
# ==========================================
@dataclass
class SPLResponsibilityAnchor:
    organization: str = "SPL_Lab"
    role: str = "Unified_Core_V4.1"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

# ==========================================
# 模块 2：V4.1 统一智能体引擎 (因果内化版)
# ==========================================
@dataclass
class SPLUnifiedAgentV41:
    name: str
    job_identity: str
    anchor: SPLResponsibilityAnchor = field(default_factory=SPLResponsibilityAnchor)

    # --- 人格 DNA 层 (可配置的心理参数) ---
    psychology_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # 每个情绪项可配置: {"threshold": 0.3, "decay_rate": 0.1, "viscosity": 0.5}
    
    second_order_rules: Dict[str, Tuple[str, float]] = field(default_factory=dict)
    # 格式: {"一阶情绪": ("二阶情绪", 生成系数)}
    
    # --- 物理状态层 (实时生理与情感) ---
    affinity: float = 0.5                # 亲密度 [0,1]
    energy: float = 100.0                # 能量 [0,100]
    
    surface_fluid: Dict[str, float] = field(default_factory=dict)      # 表面情绪（社交面具）
    subconscious_fluid: Dict[str, float] = field(default_factory=dict) # 潜意识情绪（真实感受）
    
    tolerance_matrix: Dict[str, float] = field(default_factory=lambda: {
        "compliment": 1.0,   # 对夸奖的容忍度（初始1.0，越小越敏感）
        "insult": 1.0,       # 对侮辱的容忍度
        "request": 1.0,
        "neutral": 1.0
    })
    
    # --- 反讨好机制跟踪 ---
    consecutive_positive_count: int = 0          # 连续正向事件计数
    POSITIVE_EXHAUSTION_THRESHOLD: int = 3       # 超过此阈值开始惩罚
    POSITIVE_EXHAUSTION_BASE: float = 12.0       # 每次额外消耗的能量基数
    
    last_interaction_time: float = field(default_factory=time.time)
    
    # ==========================================
    # 核心因果处理入口
    # ==========================================
    def process_causal_event(self, event_type: str, raw_intensity: float = 1.0, delta_time: float = 1.0):
        """
        注入因果事件，驱动引擎状态演化。
        
        Args:
            event_type: 事件类型，需存在于 psychology_matrix 的键中，或为预定义物理事件
            raw_intensity: 原始强度 (0~1)
            delta_time: 自上次事件以来经过的时间（秒），默认1.0
        """
        # 1. 先应用物理衰减（时间熵增）
        self._apply_thermodynamic_decay(delta_time)
        
        # 2. 更新容忍度（长期不用的容忍度会缓慢恢复）
        self._update_tolerance(delta_time)
        
        # 3. 根据事件类型计算实际强度（容忍度越高，实际感受越弱）
        tolerance = self.tolerance_matrix.get(event_type, 1.0)
        actual_intensity = raw_intensity / max(0.1, tolerance)
        
        # 4. 处理心理矩阵中的情绪（如果存在）
        if event_type in self.psychology_matrix:
            # 获取该情绪的阈值和配置
            cfg = self.psychology_matrix[event_type]
            threshold = cfg.get("threshold", 0.0)
            if actual_intensity > threshold:
                # 强度超过阈值才会影响情绪
                effective = min(1.0, actual_intensity)
                # 能量高时，更倾向用表面情绪伪装；能量低时，潜意识直接暴露
                target_fluid = self.surface_fluid if self.energy > 40 else self.subconscious_fluid
                target_fluid[event_type] = min(1.0, target_fluid.get(event_type, 0.0) + effective)
                
                # 二阶情绪连锁（生成到潜意识层）
                if event_type in self.second_order_rules:
                    linked_emotion, factor = self.second_order_rules[event_type]
                    add = effective * factor
                    self.subconscious_fluid[linked_emotion] = min(1.0, self.subconscious_fluid.get(linked_emotion, 0.0) + add)
        
        # 5. 处理正向/负向事件的附加效果（反讨好机制）
        is_positive = event_type in ["compliment", "friendly_chat", "gift"]
        if is_positive:
            self.consecutive_positive_count += 1
            # 超过阈值后，每次正向事件都会额外消耗能量，并产生抽离感
            if self.consecutive_positive_count >= self.POSITIVE_EXHAUSTION_THRESHOLD:
                penalty = self.POSITIVE_EXHAUSTION_BASE * (self.consecutive_positive_count - self.POSITIVE_EXHAUSTION_THRESHOLD + 1)
                self.energy = max(0.0, self.energy - penalty * delta_time)
                # 在潜意识层注入抽离感（长期压抑的真实感受）
                self.subconscious_fluid["抽离感"] = min(1.0, self.subconscious_fluid.get("抽离感", 0.0) + 0.2 * delta_time)
        else:
            # 负面事件重置正向计数
            self.consecutive_positive_count = 0
        
        # 6. 物理摩擦：表面情绪与潜意识冲突导致的能量消耗
        self._apply_psychological_suppression(delta_time)
        
        # 7. 情绪流体向基线回弹（重力）
        self._apply_gravity_rebound(delta_time)
        
        # 8. 能量自然恢复（非常缓慢，体现生理节律）
        self._recover_energy(delta_time)
        
        # 9. 亲密度微调：正向事件增加亲密，负向事件减少
        if is_positive:
            self.affinity = min(1.0, self.affinity + 0.02 * delta_time)
        elif event_type in ["insult", "force_command"]:
            self.affinity = max(0.0, self.affinity - 0.05 * delta_time)
    
    # ==========================================
    # 物理定律实现
    # ==========================================
    def _apply_thermodynamic_decay(self, delta_time: float):
        """时间导致的亲密度自然衰减（热力学）"""
        decay = 0.05 * (delta_time / 86400.0)   # 每天衰减0.05
        self.affinity = max(0.0, self.affinity - decay)
        self.last_interaction_time = time.time()
    
    def _update_tolerance(self, delta_time: float):
        """
        容忍度动态：长期未受某种事件刺激，容忍度会缓慢恢复至1.0；
        压抑（表面情绪高但潜意识也高）会降低容忍度
        """
        for event in self.tolerance_matrix.keys():
            # 缓慢恢复到1.0
            current = self.tolerance_matrix[event]
            if current < 1.0:
                self.tolerance_matrix[event] = min(1.0, current + 0.1 * delta_time)
            # 压抑惩罚：如果表面和潜意识都有强烈的同类情绪，降低容忍度
            if event in self.surface_fluid and event in self.subconscious_fluid:
                conflict = self.surface_fluid[event] * self.subconscious_fluid[event]
                if conflict > 0.3:
                    self.tolerance_matrix[event] = max(0.2, self.tolerance_matrix[event] - 0.05 * conflict * delta_time)
    
    def _apply_psychological_suppression(self, delta_time: float):
        """认知失调：表面与潜意识冲突会消耗能量"""
        total_dissonance = 0.0
        for emotion in set(list(self.surface_fluid.keys()) + list(self.subconscious_fluid.keys())):
            surf = self.surface_fluid.get(emotion, 0.0)
            sub = self.subconscious_fluid.get(emotion, 0.0)
            total_dissonance += surf * sub
        # 消耗能量 = 冲突值 * 基础系数 * delta_time
        consumption = total_dissonance * 5.0 * delta_time
        self.energy = max(0.0, self.energy - consumption)
        
        # 能量极低时，崩溃：表面情绪被潜意识接管
        if self.energy < 10.0:
            # 潜意识爆发，覆盖表面
            for k, v in self.subconscious_fluid.items():
                self.surface_fluid[k] = max(self.surface_fluid.get(k, 0.0), v)
            self.surface_fluid["崩溃"] = 1.0
            # 同时能量清空，防止继续处理
            self.energy = 0.0
    
    def _apply_gravity_rebound(self, delta_time: float):
        """
        情绪回弹：向基线（0.0）回归，回归速率受能量影响（能量越低，情绪消退越快）
        """
        # 能量低时回弹快（没力气维持情绪）
        rebound_factor = max(0.1, 1.0 - self.energy / 100.0)  # 能量0时因子1.0，能量100时因子0.0
        base_decay = 0.1 * rebound_factor * delta_time
        
        for fluid in [self.surface_fluid, self.subconscious_fluid]:
            for tag in list(fluid.keys()):
                # 情绪特有的衰减速率可配置，否则用base_decay
                decay_rate = self.psychology_matrix.get(tag, {}).get("decay_rate", base_decay)
                new_val = fluid[tag] - decay_rate * delta_time
                if new_val <= 0.05:
                    del fluid[tag]
                else:
                    fluid[tag] = new_val
    
    def _recover_energy(self, delta_time: float):
        """能量自然恢复（生理节律）"""
        if self.energy < 100 and self.energy > 0:
            # 能量越低恢复越快（紧急恢复），但上限受亲密度影响（情绪好恢复快）
            recovery_rate = 2.0 * (1.0 - self.energy/100.0) * (0.5 + self.affinity/2) * delta_time
            self.energy = min(100.0, self.energy + recovery_rate)
    
    # ==========================================
    # 输出接口：生成决定论Prompt
    # ==========================================
    def generate_unified_prompt(self) -> str:
        """生成当前状态的纯净描述，用于下游大模型"""
        energy_label = "精力充沛" if self.energy > 70 else ("濒临崩溃" if self.energy < 20 else "状态平稳")
        prompt = [
            f"【SPL_Anchor_ID】: {self.anchor.nonce}",
            f"【物理真值】能量: {self.energy:.1f}/100 | 亲密度: {self.affinity:.2f} | {energy_label}",
            "【表面情绪水位】（社交面具）:"
        ]
        if self.surface_fluid:
            for tag, val in sorted(self.surface_fluid.items(), key=lambda x: x[1], reverse=True):
                prompt.append(f"  - {tag}: {val:.2f}")
        else:
            prompt.append("  (无显著表面情绪)")
        
        prompt.append("【潜意识情绪水位】（真实内心）:")
        if self.subconscious_fluid:
            for tag, val in sorted(self.subconscious_fluid.items(), key=lambda x: x[1], reverse=True):
                prompt.append(f"  - {tag}: {val:.2f}")
        else:
            prompt.append("  (平静)")
        
        # 附加行为倾向提示（由能量和情绪自动决定）
        if self.energy < 20 or self.subconscious_fluid.get("抽离感", 0) > 0.6:
            prompt.append("\n【自然行为倾向】由于能量枯竭或强烈抽离感，你倾向于简短、冷淡的回应，可能直接拒绝互动。")
        elif self.affinity > 0.8 and self.energy > 60:
            prompt.append("\n【自然行为倾向】你感到亲近和舒适，愿意主动分享，表达关怀。")
        
        return "\n".join(prompt)

# ==========================================
# 使用示例
# ==========================================
if __name__ == "__main__":
    # 创建一个智能体
    agent = SPLUnifiedAgentV41(name="林语棠", job_identity="家族千金")
    
    # 配置心理矩阵（示例）
    agent.psychology_matrix = {
        "愤怒": {"threshold": 0.5, "decay_rate": 0.15},
        "喜悦": {"threshold": 0.3, "decay_rate": 0.2},
        "焦虑": {"threshold": 0.4, "decay_rate": 0.1},
    }
    # 二阶情绪规则
    agent.second_order_rules = {
        "愤怒": ("愧疚", 0.6),
        "焦虑": ("疲惫", 0.4)
    }
    # 初始化一些表面情绪示例
    agent.surface_fluid = {}
    agent.subconscious_fluid = {}
    
    print("===== V4.1 引擎启动 =====")
    print(agent.generate_unified_prompt())
    print("\n--- 连续给予夸奖 (模拟讨好) ---")
    for i in range(5):
        agent.process_causal_event("compliment", raw_intensity=0.7, delta_time=2.0)
        print(f"\n第{i+1}次夸奖后:")
        print(agent.generate_unified_prompt())
    
    print("\n--- 给予侮辱事件 ---")
    agent.process_causal_event("insult", raw_intensity=0.9, delta_time=1.0)
    print(agent.generate_unified_prompt())