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

    # --- 核心人格配置（保留原版）---
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    exclusive_groups: List[List[str]] = field(default_factory=list) # 互斥组
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [], "fallback": []
    })

    # --- ✅ 你新增的生命系统模块 ---
    affinity: float = 0.0               # 亲密度
    energy: float = 100.0               # 认知资源/精力值 0~100
    last_interaction_time: float = field(default_factory=time.time)
    trauma_tags: List[str] = field(default_factory=list) # 创伤/人格变异标签

    # ==========================================
    # ✅ 新增：状态更新主逻辑（每回合调用）
    # ==========================================
    def update_state(self, is_intense_action: bool = False):
        """
        每轮对话结束后必须调用一次，处理：时间衰减 + 疲劳恢复 + 创伤修正
        """
        current_time = time.time()
        
        # 1. 时间衰减：遗忘曲线，关系随时间淡化
        days_passed = (current_time - self.last_interaction_time) / 86400
        decay_factor = math.exp(-0.1 * days_passed) # 每日衰减约10%，可调整系数
        # 所有性格权重基线随时间回归初始值
        for tag in self.psychology_matrix:
            if 'base_start' not in self.psychology_matrix[tag]:
                self.psychology_matrix[tag]['base_start'] = self.psychology_matrix[tag]['start_weight']
            # 向初始值靠近
            original_start = self.psychology_matrix[tag]['base_start']
            current_start = self.psychology_matrix[tag]['start_weight']
            self.psychology_matrix[tag]['start_weight'] = original_start + (current_start - original_start) * decay_factor

        # 2. 能量系统：疲劳与恢复
        if is_intense_action:
            # 深度交流、情绪爆发、冲突 → 耗精力
            self.energy = max(0.0, self.energy - 25.0)
        else:
            # 普通闲聊、平静相处 → 恢复精力
            self.energy = min(100.0, self.energy + 12.0)

        # 3. 创伤覆写逻辑：永久改变底层规则
        if "betrayal_trauma" in self.trauma_tags:
            # 被背叛过：提高所有信任类特质的触发门槛，增强防御
            for tag in self.psychology_matrix:
                if "信任" in tag or "纵容" in tag or "脆弱" in tag:
                    self.psychology_matrix[tag]['threshold'] = max(0.8, self.psychology_matrix[tag].get('threshold', 0.0))
                if "高冷" in tag or "戒备" in tag or "理性" in tag:
                    self.psychology_matrix[tag]['end_weight'] = max(4.0, self.psychology_matrix[tag].get('end_weight', 1.0))

        # 4. 特殊状态：极度疲劳导致情绪崩溃/摆烂
        if self.energy < 10:
            # 精力耗尽，卸下所有伪装，只表现最本能的一面
            for tag in self.psychology_matrix:
                if "克制" in tag or "礼貌" in tag or "伪装" in tag:
                    self.psychology_matrix[tag]['end_weight'] = 0.0

        self.last_interaction_time = current_time

    # ==========================================
    # ✅ 新增：创伤事件触发接口
    # ==========================================
    def trigger_trauma(self, event_name: str):
        """触发重大事件，导致人格变异"""
        if event_name == "betrayal":
            if "betrayal_trauma" not in self.trauma_tags:
                self.trauma_tags.append("betrayal_trauma")
                self.affinity = max(0.05, self.affinity - 0.4) # 亲密度暴跌
                print(f"⚠️【人格变异】{self.name} 经历了背叛。信任系统已关闭，戒备心永久提升。")
        
        elif event_name == "loss":
            self.trauma_tags.append("loss_trauma")
            # 失去重要的东西 → 变得极度偏执/占有欲强
            for tag in self.psychology_matrix:
                if "占有欲" in tag or "控制欲" in tag:
                    self.psychology_matrix[tag]['end_weight'] = 5.0

    def set_affinity(self, value: float):
        """边界保护"""
        self.affinity = max(0.0, min(1.0, value))

    # ==========================================
    # ✅ 核心权重计算（融合S曲线+互斥+疲劳惩罚）
    # ==========================================
    def _get_dynamic_weights(self) -> Dict[str, float]:
        weights = {}
        active_traits = {}

        # 疲劳惩罚：能量越低，越没精力维持复杂情绪，高权重特质被压制
        fatigue_multiplier = 0.4 if self.energy < 15 else (0.7 if self.energy < 40 else 1.0)

        for tag, info in self.psychology_matrix.items():
            start = info.get('start_weight', 1.0)
            end = info.get('end_weight', 1.0)
            threshold = info.get('threshold', 0.0)
            curve_type = info.get('curve', 'linear')
            sensitivity = info.get('sensitivity', 1.0)

            # 门槛过滤
            if self.affinity < threshold:
                weights[tag] = 0.0
                continue

            # 归一化进度
            progress = (self.affinity - threshold) / (1.0 - threshold) if (1.0 - threshold) != 0 else 1.0
            progress = max(0.0, min(1.0, progress))
            delta = end - start
            w = start

            # 1. 曲线计算逻辑
            if curve_type == "linear":
                w = start + delta * progress * sensitivity
            elif curve_type == "sigmoid":
                k = sensitivity * 6
                sig_val = 1 / (1 + math.exp(-k * (progress - 0.5)))
                w = start + delta * sig_val
            elif curve_type == "step":
                w = start if progress < 0.5 else end

            # 2. ✅ 应用疲劳惩罚：累了就“懒得装了”
            w *= fatigue_multiplier
            w = round(max(0.0, w), 3)

            weights[tag] = w
            if w > 0.05:
                active_traits[tag] = w

        # 3. 互斥组抑制逻辑
        for group in self.exclusive_groups:
            active_in_group = [t for t in group if t in active_traits]
            if len(active_in_group) >= 2:
                sorted_t = sorted(active_in_group, key=lambda x: weights[x], reverse=True)
                leader = sorted_t[0]
                for follower in sorted_t[1:]:
                    weights[follower] *= 0.1 # 从属情绪大幅减弱

        return weights

    # ==========================================
    # 状态描述
    # ==========================================
    def _get_stage_label(self) -> str:
        base_stage = ""
        if self.affinity < 0.2: base_stage = "敌对排斥 / 完全理性"
        elif self.affinity < 0.45: base_stage = "商务社交 / 面具人格"
        elif self.affinity < 0.55: base_stage = "基准平衡 / 内心动摇"
        elif self.affinity < 0.8: base_stage = "情感主导 / 底线松动"
        else: base_stage = "本能支配 / 理智下线"

        # 叠加能量状态
        energy_state = "【精力充沛】" if self.energy > 70 else ("【身心疲惫】" if self.energy < 30 else "【状态平稳】")
        
        # 叠加创伤状态
        trauma_state = " ⚠️【曾受重创，戒备极强】" if self.trauma_tags else ""

        return f"{base_stage} | {energy_state}{trauma_state}"

    # ==========================================
    # 输出Prompt
    # ==========================================
    def to_ai_prompt(self) -> str:
        weights = self._get_dynamic_weights()
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"【当前状态】：{self._get_stage_label()} (亲密度: {self.affinity:.2f} | 能量: {self.energy:.0f}/100)",
            "【核心规则】：你的性格、语气、情绪完全由以下权重驱动。数值越高，该特质表现越强。矛盾特质自动抑制，以主导特质为准。重大经历已改写你的底层人格，不可违背。",
            "\n【动态心理权重】"
        ]

        for tag, info in self.psychology_matrix.items():
            w = weights.get(tag, 0.0)
            if w <= 0.01: continue
            desc = info.get('description', '')
            prompt.append(f"- {tag}: {w:.2f} | {desc}")

        if self.behavior_rules['fallback']:
            prompt.append("\n【行为准则】\n- " + "\n- ".join(self.behavior_rules['fallback']))
        if self.behavior_rules['forbidden']:
            prompt.append("\n【绝对禁止】\n- " + "\n- ".join(self.behavior_rules['forbidden']))

        return "\n".join(prompt)

# ==========================================
# 【最终版：叶婉清 配置示例】
# ==========================================
if __name__ == "__main__":
    ye_wanqing = AICharacterProfile(
        name="叶婉清", age=24,
        relationship="陆景川的侄女 / 无法公开的背德恋人",
        job_identity="清日集团会长"
    )

    # 互斥组定义
    ye_wanqing.exclusive_groups = [["高冷克制", "病态纵容"], ["理性利益", "情感优先"]]

    # 心理矩阵配置（加入曲线、阈值）
    ye_wanqing.psychology_matrix = {
        "高冷克制": {
            "start_weight": 3.0, "end_weight": 0.2, 
            "description": "对外掌权者面具，利益至上，防备心强，不苟言笑",
            "effective_scene": ["公开场合"],
            "threshold": 0.0, "curve": "sigmoid", "sensitivity": 2.0
        },
        "病态纵容": {
            "start_weight": 0.0, "end_weight": 3.5, 
            "description": "仅对陆景川展现，放弃所有尊严与底线，无条件服从与取悦，道德感归零",
            "effective_target": ["陆景川"],
            "effective_scene": ["私密空间"],
            "threshold": 0.3, "curve": "sigmoid", "sensitivity": 1.5
        },
        "嫉妒心": {
            "start_weight": 0.2, "end_weight": 2.5, 
            "description": "强烈的占有欲，排斥任何靠近目标的异性，敏感多疑，易情绪失控",
            "threshold": 0.1, "curve": "linear"
        }
    }

    # ========== 模拟测试流程 ==========
    print("=== 初始状态 ===")
    ye_wanqing.set_affinity(0.1)
    print(ye_wanqing.to_ai_prompt())
    print("="*70)

    print("\n=== 经过一次深度交流 (消耗能量) ===")
    ye_wanqing.set_affinity(0.6)
    ye_wanqing.update_state(is_intense
