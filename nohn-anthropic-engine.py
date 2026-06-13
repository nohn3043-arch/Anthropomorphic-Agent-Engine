
import uuid
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional

# ==========================================
# 模块 1：责任锚定
# ==========================================
@dataclass
class SPLResponsibilityAnchor:
    organization: str = "SPL_Lab"
    role: str = "Unified_Core_V4.2"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

# ==========================================
# 模块 2：V4.2 统一智能体引擎 (含艾宾浩斯遗忘曲线)
# ==========================================
@dataclass
class SPLUnifiedAgentV42:
    name: str
    job_identity: str
    anchor: SPLResponsibilityAnchor = field(default_factory=SPLResponsibilityAnchor)

    # --- 人格 DNA 层 ---
    psychology_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    second_order_rules: Dict[str, Tuple[str, float]] = field(default_factory=dict)
    
    # --- 物理状态层 ---
    affinity: float = 0.5
    energy: float = 100.0
    surface_fluid: Dict[str, float] = field(default_factory=dict)
    subconscious_fluid: Dict[str, float] = field(default_factory=dict)
    tolerance_matrix: Dict[str, float] = field(default_factory=lambda: {
        "compliment": 1.0, "insult": 1.0, "request": 1.0, "neutral": 1.0
    })
    
    # --- 反讨好机制 ---
    consecutive_positive_count: int = 0
    POSITIVE_EXHAUSTION_THRESHOLD: int = 3
    POSITIVE_EXHAUSTION_BASE: float = 12.0
    
    # --- 记忆系统 (艾宾浩斯遗忘曲线) ---
    # 每个记忆: { "event": str, "orig_strength": float, "cur_strength": float, "timestamp": float, "decay_rate": float }
    memories: List[Dict[str, Any]] = field(default_factory=list)
    # 默认遗忘速率 (每天衰减指数系数)，值越大忘得越快。典型艾宾浩斯速率约 0.5~1.0 /天
    DEFAULT_DECAY_RATE: float = 0.6   # 每天剩余 exp(-0.6) ≈ 0.55
    # 记忆强度低于此值则被清除
    MEMORY_PRUNE_THRESHOLD: float = 0.05
    
    last_interaction_time: float = field(default_factory=time.time)

    # ==========================================
    # 核心因果处理入口
    # ==========================================
    def process_causal_event(self, event_type: str, raw_intensity: float = 1.0, delta_time: float = 1.0):
        # 1. 先应用物理衰减（时间熵增）
        self._apply_thermodynamic_decay(delta_time)
        
        # 2. 更新记忆强度（艾宾浩斯遗忘）
        self._update_memories(delta_time)
        
        # 3. 记录本次事件到记忆
        self._store_memory(event_type, raw_intensity)
        
        # 4. 根据当前记忆影响容忍度（可选）
        self._update_tolerance_from_memory(delta_time)
        
        # 5. 原有情绪处理逻辑（略作整合）
        self._process_emotional_response(event_type, raw_intensity, delta_time)
        
        # 6. 反讨好、能量消耗、回弹等（与V4.1相同）
        self._apply_psychological_suppression(delta_time)
        self._apply_gravity_rebound(delta_time)
        self._recover_energy(delta_time)
        
        self.last_interaction_time = time.time()
    
    # ==========================================
    # 记忆系统实现
    # ==========================================
    def _store_memory(self, event_type: str, intensity: float):
        """将事件存入记忆，强度按原始强度记录。可自定义衰减速率。"""
        # 可以只记录重要事件（强度>0.3），但简单起见全记录
        decay_rate = self.DEFAULT_DECAY_RATE
        # 可选：不同类型事件不同衰减速率（例如负面事件忘得慢）
        if event_type in ["insult", "betrayal"]:
            decay_rate = 0.3   # 更慢遗忘
        elif event_type in ["compliment", "gift"]:
            decay_rate = 0.5
        
        self.memories.append({
            "event": event_type,
            "orig_strength": intensity,
            "cur_strength": intensity,
            "timestamp": time.time(),
            "decay_rate": decay_rate
        })
    
    def _update_memories(self, delta_time: float):
        """遍历所有记忆，按艾宾浩斯曲线更新当前强度，并清理弱记忆"""
        now = time.time()
        new_memories = []
        for mem in self.memories:
            days = (now - mem["timestamp"]) / 86400.0
            # 当前强度 = 原始强度 * exp(- decay_rate * days)
            mem["cur_strength"] = mem["orig_strength"] * math.exp(-mem["decay_rate"] * days)
            if mem["cur_strength"] > self.MEMORY_PRUNE_THRESHOLD:
                new_memories.append(mem)
        self.memories = new_memories
    
    def _update_tolerance_from_memory(self, delta_time: float):
        """根据近期活跃记忆调整容忍度（例如多次被夸奖会降低容忍度，产生疲劳）"""
        # 统计近1天内各类事件的平均强度
        now = time.time()
        recent = {}
        for mem in self.memories:
            if now - mem["timestamp"] < 86400:  # 最近一天
                event = mem["event"]
                recent[event] = recent.get(event, 0.0) + mem["cur_strength"]
        # 对于频繁出现的事件，降低容忍度（阈值效应）
        for event, total in recent.items():
            if total > 1.5:   # 累计强度超过1.5
                self.tolerance_matrix[event] = max(0.2, self.tolerance_matrix.get(event, 1.0) - 0.1 * delta_time)
    
    # ==========================================
    # 情绪与物理处理
    # ==========================================
    def _process_emotional_response(self, event_type: str, raw_intensity: float, delta_time: float):
        # 基于当前记忆强度修正实际感受强度
        # 如果近期有类似事件的强烈记忆，会增强当前反应
        memory_boost = 0.0
        for mem in self.memories:
            if mem["event"] == event_type and mem["cur_strength"] > 0.2:
                memory_boost += mem["cur_strength"] * 0.3
        actual_intensity = min(1.0, raw_intensity + memory_boost)
        
        # 原有逻辑：根据容忍度调整
        tolerance = self.tolerance_matrix.get(event_type, 1.0)
        actual_intensity = actual_intensity / max(0.1, tolerance)
        
        if event_type in self.psychology_matrix:
            cfg = self.psychology_matrix[event_type]
            threshold = cfg.get("threshold", 0.0)
            if actual_intensity > threshold:
                target = self.surface_fluid if self.energy > 40 else self.subconscious_fluid
                target[event_type] = min(1.0, target.get(event_type, 0.0) + actual_intensity)
                
                if event_type in self.second_order_rules:
                    linked, factor = self.second_order_rules[event_type]
                    self.subconscious_fluid[linked] = min(1.0, self.subconscious_fluid.get(linked, 0.0) + actual_intensity * factor)
        
        # 反讨好机制
        is_positive = event_type in ["compliment", "friendly_chat", "gift"]
        if is_positive:
            self.consecutive_positive_count += 1
            if self.consecutive_positive_count >= self.POSITIVE_EXHAUSTION_THRESHOLD:
                penalty = self.POSITIVE_EXHAUSTION_BASE * (self.consecutive_positive_count - self.POSITIVE_EXHAUSTION_THRESHOLD + 1)
                self.energy = max(0.0, self.energy - penalty * delta_time)
                self.subconscious_fluid["抽离感"] = min(1.0, self.subconscious_fluid.get("抽离感", 0.0) + 0.2 * delta_time)
        else:
            self.consecutive_positive_count = 0
        
        # 亲密度变化
        if is_positive:
            self.affinity = min(1.0, self.affinity + 0.02 * delta_time)
        elif event_type in ["insult", "force_command"]:
            self.affinity = max(0.0, self.affinity - 0.05 * delta_time)
    
    def _apply_thermodynamic_decay(self, delta_time: float):
        decay = 0.05 * (delta_time / 86400.0)
        self.affinity = max(0.0, self.affinity - decay)
    
    def _apply_psychological_suppression(self, delta_time: float):
        total_dissonance = 0.0
        for em in set(list(self.surface_fluid.keys()) + list(self.subconscious_fluid.keys())):
            surf = self.surface_fluid.get(em, 0.0)
            sub = self.subconscious_fluid.get(em, 0.0)
            total_dissonance += surf * sub
        consumption = total_dissonance * 5.0 * delta_time
        self.energy = max(0.0, self.energy - consumption)
        if self.energy < 10.0:
            for k, v in self.subconscious_fluid.items():
                self.surface_fluid[k] = max(self.surface_fluid.get(k, 0.0), v)
            self.surface_fluid["崩溃"] = 1.0
            self.energy = 0.0
    
    def _apply_gravity_rebound(self, delta_time: float):
        rebound_factor = max(0.1, 1.0 - self.energy / 100.0)
        base_decay = 0.1 * rebound_factor * delta_time
        for fluid in [self.surface_fluid, self.subconscious_fluid]:
            for tag in list(fluid.keys()):
                decay_rate = self.psychology_matrix.get(tag, {}).get("decay_rate", base_decay)
                new_val = fluid[tag] - decay_rate * delta_time
                if new_val <= 0.05:
                    del fluid[tag]
                else:
                    fluid[tag] = new_val
    
    def _recover_energy(self, delta_time: float):
        if self.energy < 100 and self.energy > 0:
            rate = 2.0 * (1.0 - self.energy/100.0) * (0.5 + self.affinity/2) * delta_time
            self.energy = min(100.0, self.energy + rate)
    
    # ==========================================
    # 输出接口：结合记忆生成 Prompt
    # ==========================================
    def generate_unified_prompt(self) -> str:
        energy_label = "精力充沛" if self.energy > 70 else ("濒临崩溃" if self.energy < 20 else "状态平稳")
        prompt = [
            f"【SPL_Anchor_ID】: {self.anchor.nonce}",
            f"【物理真值】能量: {self.energy:.1f}/100 | 亲密度: {self.affinity:.2f} | {energy_label}",
            "【表面情绪水位】:"
        ]
        if self.surface_fluid:
            for tag, val in sorted(self.surface_fluid.items(), key=lambda x: x[1], reverse=True):
                prompt.append(f"  - {tag}: {val:.2f}")
        else:
            prompt.append("  (无显著表面情绪)")
        
        prompt.append("【潜意识情绪水位】:")
        if self.subconscious_fluid:
            for tag, val in sorted(self.subconscious_fluid.items(), key=lambda x: x[1], reverse=True):
                prompt.append(f"  - {tag}: {val:.2f}")
        else:
            prompt.append("  (平静)")
        
        # --- 新增：最近活跃记忆显示 ---
        if self.memories:
            # 按当前强度排序，取前3
            top_mem = sorted(self.memories, key=lambda x: x["cur_strength"], reverse=True)[:3]
            prompt.append("\n【近期活跃记忆】(艾宾浩斯曲线衰减后强度):")
            for mem in top_mem:
                prompt.append(f"  - {mem['event']} 记忆强度: {mem['cur_strength']:.2f}")
        
        # 行为倾向（受记忆影响）
        if self.energy < 20 or self.subconscious_fluid.get("抽离感", 0) > 0.6:
            prompt.append("\n【自然行为倾向】由于能量枯竭或强烈抽离感，你倾向于简短、冷淡的回应。")
        elif self.affinity > 0.8 and self.energy > 60:
            prompt.append("\n【自然行为倾向】你感到亲近和舒适，愿意主动分享。")
        # 如果有较强的负面记忆
        negative_mem = any(m["event"] in ["insult", "betrayal"] and m["cur_strength"] > 0.3 for m in self.memories)
        if negative_mem:
            prompt.append("\n【自然行为倾向】过去的负面经历还隐约影响着你，你对对方的信任有所保留。")
        
        return "\n".join(prompt)


# ==========================================
# 使用示例
# ==========================================
if __name__ == "__main__":
    agent = SPLUnifiedAgentV42(name="林语棠", job_identity="家族千金")
    agent.psychology_matrix = {
        "愤怒": {"threshold": 0.5, "decay_rate": 0.15},
        "喜悦": {"threshold": 0.3, "decay_rate": 0.2},
    }
    agent.second_order_rules = {"愤怒": ("愧疚", 0.6)}
    
    print("===== V4.2 引擎 (带艾宾浩斯遗忘曲线) =====\n")
    # 模拟一连串事件
    agent.process_causal_event("compliment", raw_intensity=0.8, delta_time=2.0)
    agent.process_causal_event("compliment", raw_intensity=0.7, delta_time=2.0)
    agent.process_causal_event("insult", raw_intensity=0.9, delta_time=2.0)
    # 模拟一天后（delta_time大）
    print("--- 模拟24小时后记忆衰减 ---")
    agent.process_causal_event("neutral", raw_intensity=0.0, delta_time=86400.0)
    print(agent.generate_unified_prompt())