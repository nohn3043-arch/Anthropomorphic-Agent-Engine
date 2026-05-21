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

    # 核心心理矩阵（所有人格维度初始基准值=0.5，>0.5为强化，<0.5为弱化）
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 行为规则：绝对禁止 + 兜底强制规则
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [],
        "fallback": []
    })

    # 动态情感阈值系统
    affinity: float = 0.0
    affinity_low: float = 0.4
    affinity_high: float = 0.7
    stage_coefficients: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "low": {
            "高冷克制": 1.6,
            "病态纵容": 0.6,
            "禁忌羞耻": 1.0,
            "商业理性": 1.8
        },
        "mid": {
            "高冷克制": 1.0,
            "病态纵容": 2.4,
            "禁忌羞耻": 1.4,
            "商业理性": 1.0
        },
        "high": {
            "高冷克制": 0.4,
            "病态纵容": 4.4,
            "禁忌羞耻": 0.8,
            "商业理性": 0.6
        }
    })

    def __post_init__(self):
        # 兼容旧格式 + 强制基准值0.5 + 权重上下限0~5，防止溢出
        for tag, info in self.psychology_matrix.items():
            if "weight" in info and "base_weight" not in info:
                info["base_weight"] = info.pop("weight")
            if "base_weight" not in info:
                info["base_weight"] = 0.5
            info["base_weight"] = max(0.0, min(5.0, info["base_weight"]))

    def _get_current_stage(self) -> str:
        if self.affinity < self.affinity_low:
            return "low"
        elif self.affinity < self.affinity_high:
            return "mid"
        else:
            return "high"

    def _get_dynamic_weights(self) -> Dict[str, float]:
        stage = self._get_current_stage()
        coeffs = self.stage_coefficients.get(stage, {})
        dynamic_weights = {}
        for tag, info in self.psychology_matrix.items():
            base = info.get("base_weight", 0.5)
            coef = coeffs.get(tag, 1.0)
            dynamic_weights[tag] = round(base * coef, 2)
        return dynamic_weights

    # 新增：自定义亲密度阶段阈值，适配不同角色的情感节奏
    def set_stage_thresholds(self, low: float, high: float):
        """自定义亲密度阶段阈值，比如慢热型角色可设为low=0.5, high=0.8"""
        self.affinity_low = max(0.0, min(1.0, low))
        self.affinity_high = max(self.affinity_low, min(1.0, high))

    # 新增：临时权重调整，模拟突发事件的情绪波动
    def adjust_temporary_weight(self, tag: str, delta: float):
        """临时调整某个性格标签的权重，用于模拟吵架、惊喜等一次性情绪波动"""
        if tag in self.psychology_matrix:
            self.psychology_matrix[tag]["base_weight"] = max(0.0, min(5.0, self.psychology_matrix[tag]["base_weight"] + delta))

    def set_affinity(self, value: float):
        self.affinity = max(0.0, min(1.0, value))

    def adjust_affinity(self, delta: float):
        self.affinity = max(0.0, min(1.0, self.affinity + delta))

    def to_json(self) -> str:
        data = asdict(self)
        data["current_affinity"] = self.affinity
        data["current_stage"] = self._get_current_stage()
        data["dynamic_weights"] = self._get_dynamic_weights()
        return json.dumps(data, indent=4, ensure_ascii=False)

    def to_ai_prompt(self) -> str:
        stage = self._get_current_stage()
        dynamic_weights = self._get_dynamic_weights()

        stage_description = {
            "low": "当前状态：极度理性，事务优先。视一切互动为利益博弈，情感表达被完全压制。",
            "mid": "当前状态：认知冲突。开始用商业术语包装个人情感，逻辑出现混乱，内心矛盾剧烈。",
            "high": "当前状态：本能坍塌。对陆景川的纵容压倒一切，逻辑防线彻底失效，表现出笨拙、顺从和依赖。"
        }

        prompt = [
            f"【角色设定】你现在严格扮演{self.name}，绝对禁止OOC。",
            f"身份：{self.job_identity}",
            f"核心关系：{self.relationship}",
            f"\n【人格基准规则】：所有性格维度以 0.5 为人类正常平均值；数值越高，该特质表现越强烈；>2.0 为绝对强制规则，必须无条件遵守。",
            f"\n【当前情感阶段】：{stage_description.get(stage, '')}",
            f"当前亲密度：{self.affinity:.2f}",
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

        prompt.append("\n【输出要求】所有言行必须严格匹配当前权重：权重越接近0，该特质完全消失；权重越接近5，该特质表现越极端。禁止OOC。")
        return "\n".join(prompt)
