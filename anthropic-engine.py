from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class AICharacterProfile:
    name: str
    age: int
    relationship: str
    job_identity: str
    
    # 核心心理矩阵：定义 start (0.0) 和 end (1.0) 的权重
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [],
        "fallback": []
    })
    
    affinity: float = 0.0

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """线性插值计算，维持逻辑平滑演进"""
        dynamic_weights = {}
        for tag, info in self.psychology_matrix.items():
            start = info.get("start_weight", 1.0)
            end = info.get("end_weight", start)
            
            # W = start + (end - start) * affinity
            weight = start + (end - start) * self.affinity
            dynamic_weights[tag] = round(weight, 3)
            
        return dynamic_weights

    def set_affinity(self, value: float):
        """强制边界约束，防止输入溢出"""
        self.affinity = max(0.0, min(1.0, value))

    def _get_stage_label(self) -> str:
        """引入0.5作为正常社交基准的认知标签"""
        if self.affinity < 0.2: 
            return "敌对排斥"
        if self.affinity < 0.45: 
            return "商务/理性社交"
        if 0.45 <= self.affinity <= 0.55: 
            return "标准社交基准 (Normal)"
        if self.affinity < 0.8: 
            return "情感逾矩/认知倾斜"
        return "本能坍塌/绝对占有"

    def to_ai_prompt(self) -> str:
        """生成大模型Prompt，保持上下文约束与基准校验"""
        weights = self._get_dynamic_weights()
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"\n【当前心流阶段】：{self._get_stage_label()} (实时亲密度: {self.affinity:.2f})",
            "\n【动态心理权重（随亲密度实时演进，0.5为标准人类基准）】"
        ]
        
        for tag, info in self.psychology_matrix.items():
            weight = weights.get(tag, 1.0)
            desc = info.get("description", "无特定描述")
            
            line = f"- {tag}: {weight:.2f} (描述: {desc})"
            if info.get("effective_target"):
                line += f" | [约束目标]: {','.join(info['effective_target'])}"
            if info.get("effective_scene"):
                line += f" | [约束场景]: {','.join(info['effective_scene'])}"
            
            prompt.append(line)
        
        fallback_rules = self.behavior_rules.get("fallback", [])
        if fallback_rules:
            prompt.append("\n【兜底强制规则】\n- " + "\n- ".join(fallback_rules))
            
        forbidden_rules = self.behavior_rules.get("forbidden", [])
        if forbidden_rules:
            prompt.append("\n【绝对禁止行为】\n- " + "\n- ".join(forbidden_rules))

        return "\n".join(prompt)

# ==========================================
# 状态基准演进测试（以叶婉清为例）
# ==========================================
if __name__ == "__main__":
    ye_wanqing = AICharacterProfile(
        name="叶婉清", age=24, 
        relationship="陆景川的侄女 / 无法公开的背德恋人",
        job_identity="清日集团会长"
    )

    # 针对 0.5 正常人基准值调整了权重配置，使其在 0.5 时各项指标达到均衡
    ye_wanqing.psychology_matrix = {
        "高冷克制": {
            "start_weight": 2.5, "end_weight": 0.1, 
            "description": "公开场合的掌权者面具，以利益逻辑处事",
            "effective_scene": ["公开场合"]
        },
        "病态纵容": {
            "start_weight": 0.0, "end_weight": 3.0, 
            "description": "私密相处时放弃所有逻辑防线，无条件配合",
            "effective_target": ["陆景川"],
            "effective_scene": ["私密空间"]
        },
        "嫉妒心": {
            "start_weight": 0.2, "end_weight": 1.8, 
            "description": "由于占有欲导致的对第三方接近者的排斥"
        }
    }

    # 测试1：初始敌对/事务状态
    ye_wanqing.set_affinity(0.1)
    print(f"=== 测试点 1 ===")
    print(ye_wanqing.to_ai_prompt())
    print("\n" + "="*60 + "\n")

    # 测试2：切入正常人社交基准点
    ye_wanqing.set_affinity(0.5)
    print(f"=== 测试点 2 ===")
    print(ye_wanqing.to_ai_prompt())
