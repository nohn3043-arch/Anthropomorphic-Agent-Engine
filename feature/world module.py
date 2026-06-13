# ==========================================
# 世界模型系统（World Model Core）
# ==========================================

world_model: Dict[str, float] = field(default_factory=lambda: {
    "trust_people": 0.6,              # 对他人可信度预期
    "relationship_stability": 0.6,    # 关系稳定性预期
    "effort_pays_off": 0.7,           # 努力是否有回报
    "authority_reliability": 0.5,     # 权威可信度
    "conflict_danger": 0.6            # 冲突风险感知
})

world_learning_rate: float = 0.08   # 学习率（人格塑性）
world_decay: float = 0.01           # 稳定性（抗改变）

# 历史预测误差缓存（用于“经验学习”）
prediction_errors: List[Dict[str, float]] = field(default_factory=list)