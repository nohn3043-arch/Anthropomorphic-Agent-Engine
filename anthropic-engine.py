from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math

@dataclass
class AICharacterProfile:
    name: str
    age: int
    relationship: str
    job_identity: str

    # 核心心理矩阵：现在支持更多参数，不填则沿用你原来的逻辑
    # 新增: curve(曲线类型), threshold(触发阈值), priority(优先级)
    psychology_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 新增：心理互斥组 —— 定义哪些情绪不能同时高强度存在
    # 例如: [["高冷克制", "病态纵容"], ["理性", "感性"]]
    exclusive_groups: List[List[str]] = field(default_factory=list)

    behavior_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        "forbidden": [],
        "fallback": []
    })

    affinity: float = 0.0

    # ========== 【核心升级】动态权重计算 —— 从线性进化到真实心理模型 ==========
    def _get_dynamic_weights(self) -> Dict[str, float]:
        dynamic_weights = {}
        active_traits = {} # 记录激活的特质及其权重

        for tag, info in self.psychology_matrix.items():
            start = info.get("start_weight", 1.0)
            end = info.get("end_weight", start)
            threshold = info.get("threshold", 0.0)       # 门槛：低于这个值，特质为0
            curve_type = info.get("curve", "linear")     # linear / sigmoid / step
            sensitivity = info.get("sensitivity", 1.0)  # 敏感度，越大变化越极端

            # 1. 门槛过滤：关系没到，这个性格根本不会出现
            if self.affinity < threshold:
                dynamic_weights[tag] = 0.0
                continue

            # 2. 归一化计算：只计算超过门槛后的变化进度
            # 公式: Progress = (当前值 - 门槛) / (最大值 - 门槛) → 缩放到 0~1
            progress = (self.affinity - threshold) / (1.0 - threshold) if (1.0 - threshold) != 0 else 1.0
            progress = max(0.0, min(1.0, progress))

            # 3. 根据不同心理曲线计算权重
            delta = end - start
            w = start # 默认值

            if curve_type == "linear":
                # 🔹 你原来的算法：平滑直线过渡，最稳
                w = start + delta * progress * sensitivity

            elif curve_type == "sigmoid":
                # 🔹 S型曲线：【重点推荐】前期慢热，中期爆发，后期饱和 → 最像真人！
                # 比如：高冷前期死撑，0.4~0.6区间突然崩塌，后期彻底消失
                k = sensitivity * 6 # 陡峭度系数
                sigmoid_value = 1 / (1 + math.exp(-k * (progress - 0.5))) 
                w = start + delta * sigmoid_value

            elif curve_type == "step":
                # 🔹 阶跃函数：不到点不变，过了点瞬间切换 → 适合原则性、人设面具
                w = start if progress < 0.5 else end

            # 边界保护
            w = max(min(start, end), min(max(start, end), w)) 
            dynamic_weights[tag] = round(w, 3)
            
            if w > 0.05: # 只记录有效激活的特质
                active_traits[tag] = w

        # ========== 【新增】心理互斥抑制逻辑 ==========
        # 确保同一组情绪里，只有最强的那个在主导，其他被压制
        for group in self.exclusive_groups:
            # 找出当前这一组里，哪些特质是激活的
            group_active = {t: active_traits[t] for t in group if t in active_traits}
            if len(group_active) < 2:
                continue # 只有一个或没有，不用处理

            # 排序：权重最高的是当前主导情绪
            sorted_traits = sorted(group_active.items(), key=lambda x: x[1], reverse=True)
            leader_tag, leader_val = sorted_traits[0]

            # 抑制逻辑：其他情绪权重大幅衰减 (乘以0.1~0.3)，变成“内心挣扎”而不是“同时表现”
            for follower_tag, follower_val in sorted_traits[1:]:
                original_val = dynamic_weights.get(follower_tag, 0)
                # 保留一点点值，体现内心纠结，但不会主导行为
                dynamic_weights[follower_tag] = round(original_val * 0.15, 3) 

        return dynamic_weights

    def set_affinity(self, value: float):
        """强制边界约束，防止输入溢出"""
        self.affinity = max(0.0, min(1.0, value))

    def _get_stage_label(self) -> str:
        """引入0.5作为正常社交基准的认知标签"""
        if self.affinity < 0.2: 
            return "敌对排斥 / 完全理性"
        if self.affinity < 0.45: 
            return "商务/理性社交 / 面具人格"
        if 0.45 <= self.affinity <= 0.55: 
            return "标准社交基准 (内心开始动摇)"
        if self.affinity < 0.8: 
            return "情感逾矩 / 认知倾斜"
        return "本能坍塌 / 绝对占有 / 理智下线"

    def to_ai_prompt(self) -> str:
        """生成大模型Prompt，保持上下文约束与基准校验"""
        weights = self._get_dynamic_weights()
        prompt = [
            f"【角色设定】{self.name} | 身份：{self.job_identity} | 关系：{self.relationship}",
            f"\n【当前心流阶段】：{self._get_stage_label()} (实时亲密度: {self.affinity:.2f})",
            "\n【动态心理权重说明】：数值越高，该心理特质对行为的支配力越强。矛盾情绪已自动压制，以高权重特质为主导。",
            "\n【动态心理权重列表】"
        ]

        for tag, info in self.psychology_matrix.items():
            weight = weights.get(tag, 0.0)
            if weight <= 0.01:
                continue # 完全没激活的特质不显示，减少干扰

            desc = info.get("description", "无特定描述")
            line = f"- {tag}: {weight:.2f} | {desc}"
            
            # 标注变化模式，给AI更清晰的指令
            curve = info.get("curve", "linear")
            line += f" | 变化模式: {curve}"

            if info.get("effective_target"):
                line += f" | 作用对象: {','.join(info['effective_target'])}"
            if info.get("effective_scene"):
                line += f" | 生效场景: {','.join(info['effective_scene'])}"

            prompt.append(line)

        fallback_rules = self.behavior_rules.get("fallback", [])
        if fallback_rules:
            prompt.append("\n【兜底强制规则】\n- " + "\n- ".join(fallback_rules))

        forbidden_rules = self.behavior_rules.get("forbidden", [])
        if forbidden_rules:
            prompt.append("\n【绝对禁止行为】\n- " + "\n- ".join(forbidden_rules))

        return "\n".join(prompt)

# ==========================================
# 【升级后的叶婉清配置】- 更真实的心理曲线
# ==========================================
if __name__ == "__main__":
    ye_wanqing = AICharacterProfile(
        name="叶婉清", age=24, 
        relationship="陆景川的侄女 / 无法公开的背德恋人",
        job_identity="清日集团会长"
    )

    # 定义：高冷和纵容是互斥的，不可能同时出现
    ye_wanqing.exclusive_groups = [
        ["高冷克制", "病态纵容"] 
    ]

    ye_wanqing.psychology_matrix = {
        # 【高冷克制】：S型曲线 —— 前期死撑，0.5之后断崖式下滑
        "高冷克制": {
            "start_weight": 2.5, "end_weight": 0.1, 
            "description": "公开场合的掌权者面具，以利益逻辑处事，保护自己不受伤害",
            "effective_scene": ["公开场合", "有第三人在场"],
            "curve": "sigmoid",      # ✅ 用S曲线，最真实
            "sensitivity": 2.0      # ✅ 敏感度高，说变就变
        },
        # 【病态纵容】：S型曲线 —— 不到0.4基本不触发，一过0.4疯狂上涨
        "病态纵容": {
            "start_weight": 0.0, "end_weight": 3.0, 
            "description": "私密相处时放弃所有逻辑防线，伦理道德全部崩塌，无条件服从取悦",
            "effective_target": ["陆景川"],
            "effective_scene": ["私密空间"],
            "threshold": 0.3,       # ✅ 门槛：关系不到0.3，根本不会纵容
            "curve": "sigmoid",
            "sensitivity": 1.5
        },
        # 【嫉妒心】：线性即可，越熟越容易吃醋
        "嫉妒心": {
            "start_weight": 0.2, "end_weight": 2.0, 
            "description": "由于占有欲导致的对任何接近目标者的排斥、敌意与不安",
            "curve": "linear"
        }
    }

    # 测试1：初始敌对/事务状态
    print(f"=== 测试点 1 | 亲密度: 0.1 ===")
    ye_wanqing.set_affinity(0.1)
    print(ye_wanqing.to_ai_prompt())
    print("\n" + "="*70 + "\n")

    # 测试2：切入正常人社交基准点 (核心平衡点)
    print(f"=== 测试点 2 | 亲密度: 0.5 ===")
    ye_wanqing.set_affinity(0.5)
    print(ye_wanqing.to_ai_prompt())
    print("\n" + "="*70 + "\n")

    # 测试3：深度亲密状态
    print(f"=== 测试点 3 | 亲密度: 0.85 ===")
    ye_wanqing.set_affinity(0.85)
    print(ye_wanqing.to_ai_prompt())
