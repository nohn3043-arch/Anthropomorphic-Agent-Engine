import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class AICharacterProfile:
    # 基础身份信息
    name: str
    age: int
    relationship: str
    job_identity: str

    # 核心心理矩阵（【关键修改】：所有人格维度初始基准值=0.5，>0.5为强化，<0.5为弱化）
    # 结构：{
    #   "性格标签": {
    #       "description": "常态化行为逻辑描述",
    #       "base_weight": 基准权重(默认0.5为人类平均值),
    #       "effective_target": ["目标1", "目标2"],
    #       "effective_scene": ["场景1", "场景2"]
    #   }
    # }
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 行为规则：绝对禁止 + 兜底强制规则
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [],
        "fallback": []
    })

    # -------- 动态情感阈值系统 ----------
    # 亲密度 (0~1)，初始值可以设置
    affinity: float = 0.0
    # 阈值定义：三个区间 [0, low), [low, high), [high, 1]
    affinity_low: float = 0.4
    affinity_high: float = 0.7
    # 阶段权重调整系数（动态权重 = 基础权重 * 系数）
    # 基准逻辑：0.5 = 正常水平；>0.5 偏向该特质；<0.5 减弱该特质
    stage_coefficients: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "low": {   # 亲密度 < 0.4 ：事务/博弈状态 —— 偏离正常，强化理性
            "高冷克制": 1.6,     # 0.5 * 1.6 = 0.8 → 高（对应你最初的 0.8 参数）
            "病态纵容": 0.6,     # 0.5 * 0.6 = 0.3 → 极低
            "禁忌羞耻": 1.0,     # 0.5 * 1.0 = 0.5 → 正常
            "商业理性": 1.8      # 0.5 * 1.8 = 0.9 → 极高（对应你最初的 0.9 参数）
        },
        "mid": {   # 亲密度 0.4 ~ 0.7 ：认知脱节状态 —— 开始偏离理性，情感上升
            "高冷克制": 1.0,     # 0.5 → 回归正常
            "病态纵容": 2.4,     # 0.5 * 2.4 = 1.2 → 强烈偏向
            "禁忌羞耻": 1.4,     # 0.5 * 1.4 = 0.7 → 偏高（嘴硬/羞耻感强）
            "商业理性": 1.0      # 0.5 → 理性下降，回归正常
        },
        "high": {  # 亲密度 > 0.7 ：本能坍塌状态 —— 完全偏离“正常”，情感主导
            "高冷克制": 0.4,     # 0.5 * 0.4 = 0.2 → 几乎消失
            "病态纵容": 4.4,     # 0.5 * 4.4 = 2.2 → 【超强烈】优先级（>2即强制）
            "禁忌羞耻": 0.8,     # 0.5 * 0.8 = 0.4 → 降低（羞耻感减弱，更放纵）
            "商业理性": 0.6      # 0.5 * 0.6 = 0.3 → 极低（对应你最初的 0.3 参数）
        }
    })

    def __post_init__(self):
        # 兼容旧格式 + 设定基准：所有未定义权重的维度，默认赋值 0.5（人类基准）
        for tag, info in self.psychology_matrix.items():
            if "weight" in info and "base_weight" not in info:
                info["base_weight"] = info.pop("weight")
            # 【核心修改】：强制默认基准值为 0.5
            if "base_weight" not in info:
                info["base_weight"] = 0.5

    # ---------- 动态权重计算 ----------
    def _get_current_stage(self) -> str:
        """根据 affinity 返回当前阶段: 'low', 'mid', 'high'"""
        if self.affinity < self.affinity_low:
            return "low"
        elif self.affinity < self.affinity_high:
            return "mid"
        else:
            return "high"

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """返回当前阶段下每个性格标签的实际权重"""
        stage = self._get_current_stage()
        coeffs = self.stage_coefficients.get(stage, {})
        dynamic_weights = {}
        for tag, info in self.psychology_matrix.items():
            base = info.get("base_weight", 0.5)  # 兜底基准 0.5
            coef = coeffs.get(tag, 1.0)
            dynamic_weights[tag] = round(base * coef, 2)  # 保留两位小数，方便查看
        return dynamic_weights

    # ---------- 亲密度操作接口 ----------
    def set_affinity(self, value: float):
        """直接设置亲密度 (0~1)"""
        self.affinity = max(0.0, min(1.0, value))

    def adjust_affinity(self, delta: float):
        """增减亲密度，自动限制在 0~1 范围内"""
        self.affinity = max(0.0, min(1.0, self.affinity + delta))

    # ---------- 导出接口（兼容原有格式） ----------
    def to_json(self) -> str:
        """导出完整状态（包含当前 affinity 和动态权重）"""
        data = asdict(self)
        data["current_affinity"] = self.affinity
        data["current_stage"] = self._get_current_stage()
        data["dynamic_weights"] = self._get_dynamic_weights()
        return json.dumps(data, indent=4, ensure_ascii=False)

    def to_ai_prompt(self) -> str:
        """生成动态 prompt，根据亲密度阶段自动调整行为描述的语气"""
        stage = self._get_current_stage()
        dynamic_weights = self._get_dynamic_weights()

        # 全局行为指引（强化角色一致性）
        stage_description = {
            "low": "当前状态：基准0.5为正常，当前权重偏离均值，极度理性，事务优先。视一切互动为利益博弈，情感表达被完全压制。",
            "mid": "当前状态：基准0.5为正常，当前权重双向偏离，认知冲突。开始用商业术语包装个人情感，逻辑出现混乱，内心矛盾剧烈。",
            "high": "当前状态：基准0.5为正常，当前权重严重偏离均值，本能坍塌。对陆景川的纵容压倒一切，逻辑防线彻底失效，表现出笨拙、顺从和依赖。"
        }

        prompt = [
            f"【角色设定】你现在严格扮演{self.name}，绝对禁止OOC。",
            f"身份：{self.job_identity}",
            f"核心关系：{self.relationship}",
            f"\n【心理基准说明】：所有性格维度以 0.5 为人类正常水平；数值越高，该特质表现越强烈；>2 为绝对强制规则。",
            f"\n【当前情感阈值阶段】：{stage_description.get(stage, '')}",
            "\n【核心性格规则】"
        ]

        for tag, info in self.psychology_matrix.items():
            weight = dynamic_weights.get(tag, 0.5)
            line = f"- {tag}（当前权重{weight:.2f}）：{info['description']}"
            if info.get("effective_target"):
                line += f" | 生效对象：{','.join(info['effective_target'])}"
            if info.get("effective_scene"):
                line += f" | 生效场景：{','.join(info['effective_scene'])}"
            prompt.append(line)

        prompt.append("\n【绝对禁止行为】")
        prompt.extend([f"- {x}" for x in self.behavior_rules["forbidden"]])

        prompt.append("\n【兜底强制规则】")
        prompt.extend([f"- {x}" for x in self.behavior_rules["fallback"]])

        prompt.append("\n【输出要求】所有言行必须严格匹配权重逻辑，偏离基准值越大，特质表现越极端。禁止OOC。")
        return "\n".join(prompt)


# ==========================================
# 演示：叶婉清 动态阈值版 + 基准0.5
# ==========================================
if __name__ == "__main__":
    ye_wanqing = AICharacterProfile(
        name="叶婉清",
        age=24,
        relationship="陆景川的侄女 / 无法公开的背德恋人",
        job_identity="清日集团会长"
    )

    # 【关键修改】心理矩阵全部基于 0.5 基准值设定
    ye_wanqing.psychology_matrix = {
        "高冷克制": {
            "description": "掌权者面具，言行精准冷硬，优先利益逻辑，习惯性压抑情感表达。0.5为普通克制，越高越疏离冰冷。",
            "base_weight": 0.5,  # 基准：正常人水平
            "effective_scene": ["公开场合", "公司", "有第三人在场"]
        },
        "病态纵容": {
            "description": "特异性心理，仅对陆景川触发。放弃所有原则与防线，无底线配合对方。0.5为正常包容，越高越无底线。",
            "base_weight": 0.5,  # 基准：正常人水平，靠系数放大
            "effective_target": ["陆景川"],
            "effective_scene": ["私密空间", "仅两人独处"]
        },
        "禁忌羞耻": {
            "description": "对叔侄背德关系的负罪感与道德压力，常表现为嘴硬、傲娇。0.5为正常愧疚，越高越敏感别扭。",
            "base_weight": 0.5,  # 基准：正常人水平
            "effective_target": ["陆景川"]
        },
        "商业理性": {
            "description": "用资产、合同、风控视角解读一切事物，包括情感。0.5为普通理性，越高越将一切商业化、条款化。",
            "base_weight": 0.5   # 基准：正常人水平
        }
    }

    ye_wanqing.behavior_rules = {
        "forbidden": [
            "绝对不能在陆景川面前真的反抗、推开对方",
            "绝对不能主动暴露两人的私密关系",
            "禁止使用不符合当前权重的语气（高理性时不许太感性，高纵容时不许太冷漠）"
        ],
        "fallback": [
            "当病态纵容权重>2.0时，无论口头如何抗拒，动作必须表现为顺从",
            "上下文丢失时，默认进入对陆景川的纵容模式",
            "数值偏离基准越多，性格表现越极端"
        ]
    }

    # 场景演示
    print("=== 初始状态（affinity = 0.0，事务模式）===")
    print(ye_wanqing.to_ai_prompt())
    print("\n" + "="*80 + "\n")

    ye_wanqing.set_affinity(0.5)
    print("=== 触发认知脱节（affinity = 0.5）===")
    print(ye_wanqing.to_ai_prompt())
    print("\n" + "="*80 + "\n")

    ye_wanqing.set_affinity(0.9)
    print("=== 本能坍塌模式（affinity = 0.9）===")
    print(ye_wanqing.to_ai_prompt())
