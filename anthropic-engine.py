from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
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
    exclusive_groups: List[List[str]] = field(default_factory=list)  # 互斥情绪组
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [], "fallback": []
    })

    # --- 生命系统变量 ---
    affinity: float = 0.0               # 亲密度 0.0 ~ 1.0
    energy: float = 100.0               # 认知能量 0 ~ 100
    last_interaction_time: float = field(default_factory=time.time)
    trauma_tags: List[str] = field(default_factory=list)  # 创伤标签
    trauma_recovery: Dict[str, float] = field(default_factory=dict)  # 新增：创伤修复进度 0~1

    # --- 新增：当前上下文（场景+对象）---
    current_context: Dict[str, str] = field(default_factory=lambda: {
        "scene": "default",    # 当前场景
        "target": "default"    # 对话对象
    })

    # ==========================================
    # 生命状态更新逻辑（时间衰减 + 疲劳 + 创伤 + 修复）
    # ==========================================
    def update_state(self, is_intense_action: bool = False):
        current_time = time.time()
        
        # 1. 时间衰减：艾宾浩斯遗忘曲线，关系随时间淡化
        days_passed = (current_time - self.last_interaction_time) / 86400
        decay_factor = math.exp(-0.1 * days_passed)  # 每日衰减系数

        # 所有特质的基线权重向初始值回归
        for tag in self.psychology_matrix:
            info = self.psychology_matrix[tag]
            if 'base_start' not in info:
                info['base_start'] = info.get('start_weight', 1.0)
            # 动态衰减
            original = info['base_start']
            current = info.get('start_weight', original)
            info['start_weight'] = original + (current - original) * decay_factor

        # 2. 能量管理：消耗与恢复
        if is_intense_action:
            self.energy = max(0.0, self.energy - 25.0)
            # 深度互动可加速创伤修复
            for trauma in self.trauma_recovery:
                self.trauma_recovery[trauma] = min(1.0, self.trauma_recovery[trauma] + 0.08)
        else:
            self.energy = min(100.0, self.energy + 12.0)

        # 3. 创伤覆写逻辑 + 修复机制
        if "betrayal_trauma" in self.trauma_tags:
            recovery = self.trauma_recovery.get("betrayal_trauma", 0.0)
            # 修复进度越高，负面影响越弱
            impact_factor = 1.0 - recovery * 0.8  # 最多恢复80%，留永久痕迹

            for tag in self.psychology_matrix:
                if any(k in tag for k in ["信任", "纵容", "脆弱"]):
                    original_threshold = self.psychology_matrix[tag].get('base_threshold', 0.3)
                    self.psychology_matrix[tag]['threshold'] = original_threshold + (0.8 - original_threshold) * impact_factor
                if any(k in tag for k in ["高冷", "戒备", "理性", "风险控制"]):
                    original_end = self.psychology_matrix[tag].get('base_end', 1.5)
                    self.psychology_matrix[tag]['end_weight'] = original_end + (4.0 - original_end) * impact_factor

            # 完全修复则移除创伤标记（但参数已永久改变）
            if recovery >= 1.0:
                self.trauma_tags.remove("betrayal_trauma")
                print(f"✅【创伤修复完成】{self.name} 已重建信任，但防备心略高于从前。")

        # 4. 极度疲劳状态：卸下所有伪装
        if self.energy < 10:
            for tag in self.psychology_matrix:
                if any(k in tag for k in ["克制", "礼貌", "伪装"]):
                    self.psychology_matrix[tag]['end_weight'] = 0.0

        self.last_interaction_time = current_time

    # ==========================================
    # 重大事件触发：创伤 + 修复事件
    # ==========================================
    def trigger_trauma(self, event_name: str):
        """触发负面事件，造成创伤"""
        if event_name == "betrayal" and "betrayal_trauma" not in self.trauma_tags:
            self.trauma_tags.append("betrayal_trauma")
            self.trauma_recovery["betrayal_trauma"] = 0.0
            self.affinity = max(0.05, self.affinity - 0.4)
            print(f"⚠️【人格变异】{self.name} 经历信任危机！信任门槛大幅提高，戒备心增强。")
        
        elif event_name == "loss":
            self.trauma_tags.append("loss_trauma")
            for tag in self.psychology_matrix:
                if "占有欲" in tag or "控制欲" in tag:
                    self.psychology_matrix[tag]['end_weight'] = 5.0

    def trigger_recovery_event(self, event_name: str):
        """触发正向事件，修复创伤"""
        if event_name == "transparency_communication" and "betrayal_trauma" in self.trauma_tags:
            self.trauma_recovery["betrayal_trauma"] = min(1.0, self.trauma_recovery.get("betrayal_trauma", 0.0) + 0.15)
            print(f"🔧【修复进展】沟通坦诚，信任度小幅恢复 ({self.trauma_recovery['betrayal_trauma']*100:.0f}%)")

    def set_affinity(self, value: float):
        self.affinity = max(0.0, min(1.0, value))

    def set_context(self, scene: str = "default", target: str = "default"):
        """设置当前场景与对话对象，用于过滤"""
        self.current_context["scene"] = scene
        self.current_context["target"] = target

    # ==========================================
    # 核心算法：动态权重计算 + 场景过滤 + 互斥抑制 + 疲劳惩罚
    # ==========================================
    def _get_dynamic_weights(self) -> Dict[str, float]:
        weights = {}
        active_traits = {}
        current_scene = self.current_context["scene"]
        current_target = self.current_context["target"]

        # 疲劳惩罚：能量越低，情绪表达越单一、越本能
        fatigue_multiplier = 0.4 if self.energy < 15 else (0.7 if self.energy < 40 else 1.0)

        for tag, info in self.psychology_matrix.items():
            # ========== ✅ 场景+对象过滤逻辑 ==========
            # 检查是否有生效场景/对象配置
            effective_scenes = info.get("effective_scene", ["default"])
            forbidden_scenes = info.get("forbidden_scene", [])
            effective_targets = info.get("effective_target", ["default"])

            # 禁用场景 → 直接跳过
            if current_scene in forbidden_scenes:
                continue
            # 非生效场景 且 非默认 → 跳过
            if current_scene not in effective_scenes and "default" not in effective_scenes:
                continue
            # 非生效对象 且 非默认 → 跳过
            if current_target not in effective_targets and "default" not in effective_targets:
                continue

            # ========== 权重计算逻辑 ==========
            start = info.get('start_weight', 1.0)
            end = info.get('end_weight', 1.0)
            threshold = info.get('threshold', 0.0)
            curve_type = info.get('curve', 'linear')
            sensitivity = info.get('sensitivity', 1.0)

            # 门槛过滤：关系不到，特质不激活
            if self.affinity < threshold:
                weights[tag] = 0.0
                continue

            # 进度归一化
            progress = (self.affinity - threshold) / (1.0 - threshold) if (1.0 - threshold) != 0 else 1.0
            progress = max(0.0, min(1.0, progress))
            delta = end - start
            w = start

            # 曲线计算
            if curve_type == "linear":
                w = start + delta * progress * sensitivity
            elif curve_type == "sigmoid":
                k = sensitivity * 6
                sig_val = 1 / (1 + math.exp(-k * (progress - 0.5)))
                w = start + delta * sig_val
            elif curve_type == "step":
                w = start if progress < 0.5 else end

            # 应用疲劳惩罚
            w *= fatigue_multiplier
            w = round(max(0.0, w), 3)

            weights[tag] = w
            if w > 0.05:
                active_traits[tag] = w

        # 互斥逻辑：矛盾情绪抑制，只保留主导情绪
        for group in self.exclusive_groups:
            active_in_group = [t for t in group if t in active_traits]
            if len(active_in_group) >= 2:
                sorted_t = sorted(active_in_group, key=lambda x: weights[x], reverse=True)
                leader = sorted_t[0]
                for follower in sorted_t[1:]:
                    weights[follower] *= 0.1  # 从属情绪弱化

        return weights

    # ==========================================
    # 状态描述
    # ==========================================
    def _get_stage_label(self) -> str:
        if self.affinity < 0.2: base = "敌对排斥 / 完全理性"
        elif self.affinity < 0.45: base = "商务社交 / 面具人格"
        elif self.affinity < 0.55: base = "基准平衡 / 内心动摇"
        elif self.affinity < 0.8: base = "情感主导 / 底线松动"
        else: base = "本能支配 / 理智下线"

        energy_state = "【精力充沛】" if self.energy > 70 else ("【身心疲惫】" if self.energy < 30 else "【状态平稳】")
        trauma_state = f" ⚠️【戒备状态:{self.trauma_recovery.get('betrayal_trauma',0.0)*100:.0f}%修复】" if self.trauma_tags else ""
        context_info = f" | 场景:{self.current_context['scene']} | 对象:{self.current_context['target']}"
        return f"{base} | {energy_state}{trauma_state}{context_info}"

    # ==========================================
    # 输出Prompt
    # ==========================================
    def to_ai_prompt(self) -> str:
        weights = self._get_dynamic_weights()
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"【当前状态】：{self._get_stage_label()} (亲密度: {self.affinity:.2f} | 能量: {self.energy:.0f}/100)",
            "【核心规则】：性格、语气、专业度由权重驱动。数值越高影响越强。矛盾特质自动抑制，仅主导特质生效。重大经历已改写底层逻辑，必须遵循。",
            "\n【动态心理权重（已按场景/对象过滤）】"
        ]

        for tag, info in self.psychology_matrix.items():
            w = weights.get(tag, 0.0)
            if w <= 0.01: continue
            desc = info.get('description', '')
            line = f"- {tag}: {w:.2f} | {desc}"
            # 标注生效范围，给AI更明确指令
            scenes = ",".join(info.get('effective_scene', ['all']))
            targets = ",".join(info.get('effective_target', ['all']))
            line += f" | 生效范围：场景[{scenes}] | 对象[{targets}]"
            prompt.append(line)

        if self.behavior_rules['fallback']:
            prompt.append("\n【行为准则】\n- " + "\n- ".join(self.behavior_rules['fallback']))
        if self.behavior_rules['forbidden']:
            prompt.append("\n【绝对禁止】\n- " + "\n- ".join(self.behavior_rules['forbidden']))

        return "\n".join(prompt)
