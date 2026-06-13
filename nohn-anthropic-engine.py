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
    role: str = "Unified_Core_V4.3"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

# ==========================================
# 模块 2：V4.3 统一智能体引擎 (含艾宾浩斯记忆 + 创伤修复)
# ==========================================
@dataclass
class SPLUnifiedAgentV43:
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
        "compliment": 1.0, "insult": 1.0, "request": 1.0, "neutral": 1.0,
        "betrayal": 1.0, "apology": 1.0
    })
    
    # --- 反讨好机制 ---
    consecutive_positive_count: int = 0
    POSITIVE_EXHAUSTION_THRESHOLD: int = 3
    POSITIVE_EXHAUSTION_BASE: float = 12.0
    
    # --- 普通记忆系统 (艾宾浩斯遗忘曲线) ---
    memories: List[Dict[str, Any]] = field(default_factory=list)
    DEFAULT_DECAY_RATE: float = 0.6
    MEMORY_PRUNE_THRESHOLD: float = 0.05

    # ========== 新增：创伤与修复系统 ==========
    # 创伤记忆池：独立于普通记忆，衰减极慢，需主动修复
    trauma_memories: List[Dict[str, Any]] = field(default_factory=list)
    TRAUMA_FORMATION_THRESHOLD: float = 0.7    # 负面事件强度超过此值形成创伤
    TRAUMA_BASE_DECAY: float = 0.05            # 创伤自然衰减速率/天（极慢）
    TRAUMA_REPAIR_THRESHOLD: float = 0.02      # 创伤强度低于此值视为完全修复
    # 创伤泛化映射：核心创伤事件会影响哪些相关事件的容忍度
    TRAUMA_GENERALIZATION_MAP: Dict[str, List[Tuple[str, float]]] = field(default_factory=lambda: {
        "betrayal": [("insult", 0.6), ("request", 0.5), ("compliment", 0.4)],
        "insult": [("request", 0.3), ("neutral", 0.2)]
    })
    # 修复事件映射：哪些事件能带来修复，以及修复系数
    REPAIR_EVENT_MAP: Dict[str, float] = field(default_factory=lambda: {
        "apology": 0.4,      # 道歉：高强度定向修复
        "friendly_chat": 0.08, # 温和陪伴：低强度持续修复
        "neutral": 0.03,     # 平静共处：微量修复
        "gift": 0.02         # 礼物：修复极弱，易触发反讨好
    })
    
    last_interaction_time: float = field(default_factory=time.time)

    # ==========================================
    # 核心因果处理入口
    # ==========================================
    def process_causal_event(self, event_type: str, raw_intensity: float = 1.0, delta_time: float = 1.0):
        # 1. 物理时间熵增衰减
        self._apply_thermodynamic_decay(delta_time)
        
        # 2. 更新普通记忆 + 创伤记忆（艾宾浩斯 + 创伤自然衰减）
        self._update_memories(delta_time)
        self._update_trauma_decay(delta_time)
        
        # 3. 记录本次事件到对应记忆池
        self._store_memory(event_type, raw_intensity)
        # 负面事件超过阈值，形成创伤
        if event_type in ["insult", "betrayal", "force_command"] and raw_intensity >= self.TRAUMA_FORMATION_THRESHOLD:
            self._form_trauma(event_type, raw_intensity)
        
        # 4. 应用当前创伤对系统的全局影响（容忍度、情绪基底、能量消耗）
        self._apply_trauma_effects(delta_time)
        
        # 5. 情绪响应处理（含记忆强化、容忍度修正）
        self._process_emotional_response(event_type, raw_intensity, delta_time)
        
        # 6. 创伤修复计算（根据本次事件类型累积修复进度）
        self._process_trauma_repair(event_type, raw_intensity, delta_time)
        
        # 7. 原有物理规则链路
        self._apply_psychological_suppression(delta_time)
        self._apply_gravity_rebound(delta_time)
        self._recover_energy(delta_time)
        
        # 8. 低能量创伤闪回
        if self.energy < 30.0:
            self._trauma_flashback()
        
        self.last_interaction_time = time.time()
    
    # ==========================================
    # 普通记忆系统（保留 V4.2 逻辑）
    # ==========================================
    def _store_memory(self, event_type: str, intensity: float):
        decay_rate = self.DEFAULT_DECAY_RATE
        if event_type in ["insult", "betrayal"]:
            decay_rate = 0.3
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
        now = time.time()
        new_memories = []
        for mem in self.memories:
            days = (now - mem["timestamp"]) / 86400.0
            mem["cur_strength"] = mem["orig_strength"] * math.exp(-mem["decay_rate"] * days)
            if mem["cur_strength"] > self.MEMORY_PRUNE_THRESHOLD:
                new_memories.append(mem)
        self.memories = new_memories
    
    # ==========================================
    # 创伤核心机制
    # ==========================================
    def _form_trauma(self, event_type: str, intensity: float):
        """形成创伤记忆：独立存储，附带泛化标签和修复进度"""
        self.trauma_memories.append({
            "event": event_type,
            "severity": intensity,          # 初始严重度
            "cur_severity": intensity,      # 当前严重度
            "repair_progress": 0.0,         # 修复进度 0~1
            "timestamp": time.time(),
            "generalization": self.TRAUMA_GENERALIZATION_MAP.get(event_type, [])
        })
        # 形成创伤瞬间，直接向潜意识注入对应负面情绪
        if event_type == "betrayal":
            self.subconscious_fluid["不信任"] = min(1.0, self.subconscious_fluid.get("不信任", 0.0) + intensity * 0.8)
        elif event_type == "insult":
            self.subconscious_fluid["屈辱感"] = min(1.0, self.subconscious_fluid.get("屈辱感", 0.0) + intensity * 0.6)

    def _update_trauma_decay(self, delta_time: float):
        """创伤自然衰减（极缓慢，仅兜底用）"""
        days = delta_time / 86400.0
        new_traumas = []
        for trauma in self.trauma_memories:
            trauma["cur_severity"] *= math.exp(-self.TRAUMA_BASE_DECAY * days)
            if trauma["cur_severity"] > self.TRAUMA_REPAIR_THRESHOLD:
                new_traumas.append(trauma)
        self.trauma_memories = new_traumas

    def _apply_trauma_effects(self, delta_time: float):
        """创伤对系统的全局影响：拉低容忍度 + 持续消耗能量"""
        total_trauma = sum(t["cur_severity"] for t in self.trauma_memories)
        if total_trauma <= 0:
            return
        
        # 1. 核心事件 + 泛化事件 容忍度下降
        for trauma in self.trauma_memories:
            event = trauma["event"]
            sev = trauma["cur_severity"]
            # 核心事件容忍度降低
            self.tolerance_matrix[event] = max(0.1, self.tolerance_matrix.get(event, 1.0) - sev * 0.05 * delta_time)
            # 泛化事件容忍度降低
            for gen_event, factor in trauma["generalization"]:
                self.tolerance_matrix[gen_event] = max(0.1, self.tolerance_matrix.get(gen_event, 1.0) - sev * factor * 0.03 * delta_time)
        
        # 2. 潜意识持续消耗能量（创伤内耗）
        energy_cost = total_trauma * 0.8 * delta_time
        self.energy = max(0.0, self.energy - energy_cost)

    def _process_trauma_repair(self, event_type: str, intensity: float, delta_time: float):
        """创伤修复：仅安全事件有效，讨好类事件修复效率极低"""
        if not self.trauma_memories:
            return
        
        repair_coeff = self.REPAIR_EVENT_MAP.get(event_type, 0.0)
        if repair_coeff <= 0:
            return
        
        # 反讨好机制对冲：连续正向事件超过阈值，修复效率打折
        if self.consecutive_positive_count >= self.POSITIVE_EXHAUSTION_THRESHOLD:
            repair_coeff *= 0.2
        
        # 修复量 = 事件强度 * 修复系数 * 时间
        repair_amount = intensity * repair_coeff * delta_time
        
        # 优先修复严重度最低的创伤（先易后难）
        for trauma in sorted(self.trauma_memories, key=lambda x: x["cur_severity"]):
            if repair_amount <= 0:
                break
            # 修复进度累积
            trauma["repair_progress"] = min(1.0, trauma["repair_progress"] + repair_amount * 0.5)
            # 进度转化为严重度下降
            severity_reduce = repair_amount * trauma["cur_severity"]
            trauma["cur_severity"] = max(self.TRAUMA_REPAIR_THRESHOLD, trauma["cur_severity"] - severity_reduce)
            repair_amount -= severity_reduce
        
        # 修复同步提升对应容忍度
        for trauma in self.trauma_memories:
            if trauma["repair_progress"] > 0.5:
                recover = trauma["repair_progress"] * 0.02 * delta_time
                self.tolerance_matrix[trauma["event"]] = min(1.0, self.tolerance_matrix[trauma["event"]] + recover)

    def _trauma_flashback(self):
        """低能量创伤闪回：临时强化潜意识负面情绪"""
        for trauma in self.trauma_memories:
            sev = trauma["cur_severity"] * 0.3
            if trauma["event"] == "betrayal":
                self.subconscious_fluid["不信任"] = min(1.0, self.subconscious_fluid.get("不信任", 0.0) + sev)
            elif trauma["event"] == "insult":
                self.subconscious_fluid["屈辱感"] = min(1.0, self.subconscious_fluid.get("屈辱感", 0.0) + sev)
        # 闪回额外消耗能量
        self.energy = max(0.0, self.energy - 5.0)

    # ==========================================
    # 情绪与物理处理（兼容创伤影响）
    # ==========================================
    def _process_emotional_response(self, event_type: str, raw_intensity: float, delta_time: float):
        # 记忆强度叠加
        memory_boost = 0.0
        for mem in self.memories:
            if mem["event"] == event_type and mem["cur_strength"] > 0.2:
                memory_boost += mem["cur_strength"] * 0.3
        actual_intensity = min(1.0, raw_intensity + memory_boost)
        
        # 容忍度修正
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
        is_positive = event_type in ["compliment", "friendly_chat", "gift", "apology"]
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
        elif event_type in ["insult", "force_command", "betrayal"]:
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
            # 独处能量恢复时附带微量创伤修复（脆弱性对冲）
            if self.trauma_memories:
                for trauma in self.trauma_memories:
                    trauma["cur_severity"] *= (1 - 0.001 * delta_time)
    
    # ==========================================
    # 输出接口：含创伤状态
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
        
        # 普通记忆
        if self.memories:
            top_mem = sorted(self.memories, key=lambda x: x["cur_strength"], reverse=True)[:3]
            prompt.append("\n【近期活跃记忆】:")
            for mem in top_mem:
                prompt.append(f"  - {mem['event']} 强度: {mem['cur_strength']:.2f}")
        
        # ========== 新增：创伤状态输出 ==========
        if self.trauma_memories:
            prompt.append("\n【创伤印记】:")
            for idx, trauma in enumerate(self.trauma_memories, 1):
                prompt.append(
                    f"  {idx}. {trauma['event']} 严重度: {trauma['cur_severity']:.2f} | "
                    f"修复进度: {trauma['repair_progress']:.1%}"
                )
            total_sev = sum(t["cur_severity"] for t in self.trauma_memories)
            if total_sev > 0.5:
                prompt.append("\n【自然行为倾向】存在未愈合的创伤印记，你对相关事件保持警惕，难以完全信任对方。")
            if self.energy < 30:
                prompt.append("【自然行为倾向】能量过低触发创伤闪回，情绪易失控，倾向于回避互动。")
        else:
            prompt.append("\n【创伤印记】: 无")
        
        # 通用行为倾向
        if self.energy < 20 or self.subconscious_fluid.get("抽离感", 0) > 0.6:
            prompt.append("\n【自然行为倾向】能量枯竭或强烈抽离感，倾向于简短、冷淡回应，直接拒绝互动。")
        elif self.affinity > 0.8 and self.energy > 60 and not self.trauma_memories:
            prompt.append("\n【自然行为倾向】感到亲近舒适，愿意主动分享、表达关怀。")
        
        return "\n".join(prompt)


# ==========================================
# 使用示例：背叛创伤 → 道歉修复 完整链路
# ==========================================
if __name__ == "__main__":
    agent = SPLUnifiedAgentV43(name="林语棠", job_identity="家族千金")
    agent.psychology_matrix = {
        "愤怒": {"threshold": 0.5, "decay_rate": 0.15},
        "喜悦": {"threshold": 0.3, "decay_rate": 0.2},
        "委屈": {"threshold": 0.4, "decay_rate": 0.1}
    }
    agent.second_order_rules = {"愤怒": ("愧疚", 0.6), "委屈": ("不信任", 0.7)}
    
    print("===== V4.3 引擎启动：创伤修复演示 =====\n")
    
    # 阶段1：背叛事件，形成创伤
    print("--- 阶段1：遭遇高强度背叛（形成创伤）---")
    agent.process_causal_event("betrayal", raw_intensity=0.9, delta_time=1.0)
    print(agent.generate_unified_prompt())
    
    # 阶段2：连续夸奖试图讨好（反讨好机制触发，修复无效）
    print("\n--- 阶段2：连续3次夸奖试图讨好（修复效率极低）---")
    for i in range(3):
        agent.process_causal_event("compliment", raw_intensity=0.8, delta_time=2.0)
    print(agent.generate_unified_prompt())
    
    # 阶段3：真诚道歉 + 温和陪伴（定向修复）
    print("\n--- 阶段3：真诚道歉 + 温和陪伴（有效修复）---")
    agent.process_causal_event("apology", raw_intensity=0.8, delta_time=3.0)
    agent.process_causal_event("friendly_chat", raw_intensity=0.6, delta_time=5.0)
    print(agent.generate_unified_prompt())
