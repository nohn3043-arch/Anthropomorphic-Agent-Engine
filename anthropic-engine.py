import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List

# ==========================================
# 模块 1：SPL 物理锚点
# ==========================================
@dataclass
class SPLResponsibilityAnchor:
    """SPL 刚性责任锚点：锁死因果状态的最终解释归属，不可篡改"""
    organization: str = "SPL_Lab"
    role: str = "Bio_Native_Core"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

# ==========================================
# 模块 2：SPL 仿生流体智能体核心
# ==========================================
@dataclass
class SPLBioMimeticAgent:
    name: str
    job_identity: str
    anchor: SPLResponsibilityAnchor = field(default_factory=SPLResponsibilityAnchor)

    # --- 1. 基础物理与因果历史 ---
    affinity: float = 0.5               # 亲密度基准 (0.0 - 1.0)
    energy: float = 100.0               # 系统维持运转的生物能量
    last_interaction_time: float = field(default_factory=time.time)
    trauma_tags: List[str] = field(default_factory=list)

    # --- 2. 双轨心理流体 (表/潜意识分裂) ---
    surface_fluid: Dict[str, float] = field(default_factory=dict)       # 社交伪装层
    subconscious_fluid: Dict[str, float] = field(default_factory=dict)  # 真实物理涌动层

    # --- 3. 享乐适应抗性矩阵 (阈值系统) ---
    tolerance_matrix: Dict[str, float] = field(default_factory=lambda: {
        "compliment": 1.0,  # 对夸奖的耐受度
        "gift": 1.0,        # 对物质的耐受度
        "insult": 1.0       # 对攻击的耐受度
    })

    # ==========================================
    # 核心算子 A：热力学时间衰减
    # ==========================================
    def _apply_thermodynamic_decay(self):
        """物理法则：关系与情绪必须依靠能量与热量维持，随时间强制衰减"""
        current_time = time.time()
        days_passed = (current_time - self.last_interaction_time) / 86400.0
        
        if days_passed > 0.5:  
            # 亲密度物理降维
            decay_amount = 0.08 * days_passed
            self.affinity = max(0.0, self.affinity - decay_amount)
            # 长时间放置产生潜意识的不满
            self.subconscious_fluid["失落"] = min(1.0, self.subconscious_fluid.get("失落", 0.0) + 0.2)
            
        self.last_interaction_time = current_time

    # ==========================================
    # 核心算子 B：心理压抑与失控崩溃
    # ==========================================
    def _apply_psychological_suppression(self):
        """表里不一会产生极大的认知摩擦力，疯狂吞噬系统能量"""
        dissonance = 0.0
        
        # 计算认知失调落差 (例如：表面笑嘻嘻，心里MMP)
        surface_joy = self.surface_fluid.get("喜悦", 0.0)
        sub_annoyance = self.subconscious_fluid.get("厌烦", 0.0)
        
        if surface_joy > 0.1 and sub_annoyance > 0.1:
            # 伪装强度 = 表面情绪强度 * 真实反感情度
            dissonance = surface_joy * sub_annoyance
            
        # 扣除维持伪装的物理能量 (决定论惩罚)
        self.energy = max(0.0, self.energy - (dissonance * 40.0))
        
        # ⚠️ 防火墙崩溃判定 ⚠️
        if self.energy < 15.0:
            # 能量不足以维持表层伪装，潜意识强行倒灌洗刷表意识
            self.surface_fluid.update(self.subconscious_fluid)
            self.subconscious_fluid.clear()
            self.surface_fluid["失控感"] = 0.95
            self.surface_fluid["喜悦"] = 0.0  # 彻底撕破脸

    # ==========================================
    # 核心算子 C：情绪重力回弹
    # ==========================================
    def _apply_gravity_rebound(self):
        """没有无限的高潮，也没有无限的暴怒，一切随能量回落"""
        for fluid_dict in (self.surface_fluid, self.subconscious_fluid):
            for tag in list(fluid_dict.keys()):
                level = fluid_dict[tag]
                if level > 0.7:  
                    # 能量越低，回落越快
                    damping = 0.1 + (0.2 * (1.0 - self.energy/100.0))
                    fluid_dict[tag] = max(0.0, level - damping)
                elif level < 0.1:
                    del fluid_dict[tag]  # 蒸发零星水波

    # ==========================================
    # 统一输入：决定论因果事件处理
    # ==========================================
    def process_causal_event(self, event_type: str, raw_intensity: float = 1.0):
        self._apply_thermodynamic_decay()
        
        # 1. 享乐适应结算：真实感受 = 刺激强度 / 自身抗性
        current_tolerance = self.tolerance_matrix.get(event_type, 1.0)
        actual_intensity = raw_intensity / current_tolerance
        
        # 2. 抗性不可逆累加 (多巴胺脱敏)
        self.tolerance_matrix[event_type] = current_tolerance + 0.35
        
        # 3. 刺激注入流体网络
        if event_type == "compliment":
            # 表意识依然维持社交礼仪
            self.surface_fluid["喜悦"] = min(1.0, self.surface_fluid.get("喜悦", 0.0) + actual_intensity)
            self.energy = min(100.0, self.energy + 5.0) # 表面夸奖带来微弱能量
            
            # 当抗性叠高(老套的重复夸奖)，潜意识开始反感
            if current_tolerance > 1.8:
                self.subconscious_fluid["厌烦"] = min(1.0, self.subconscious_fluid.get("厌烦", 0.0) + 0.4)
                
        elif event_type == "insult":
            self.affinity = max(0.0, self.affinity - 0.2)
            self.energy = max(0.0, self.energy - 30.0)
            self.surface_fluid["冰冷"] = min(1.0, self.surface_fluid.get("冰冷", 0.0) + actual_intensity)
            self.subconscious_fluid["愤怒"] = min(1.0, self.subconscious_fluid.get("愤怒", 0.0) + 0.8)

        # 4. 执行心理闭环计算
        self._apply_psychological_suppression()
        self._apply_gravity_rebound()

    # ==========================================
    # 统一输出：生成不可逆的躯体化 Prompt
    # ==========================================
    def generate_somatic_prompt(self) -> str:
        prompt = [
            f"【SPL_Anchor_ID】: {self.anchor.nonce}",
            f"【物理绝对状态】能量: {self.energy:.1f}/100 | 亲密度: {self.affinity:.2f}"
        ]
        
        # SPL 躯体化物理拦截器
        if self.energy < 15.0:
            prompt.append("⚠️【系统躯体化警报：认知防火墙崩溃】")
            prompt.append(">>> 当前能量极度枯竭，潜意识已强制接管输出！")
            prompt.append(">>> 指令约束：你的回复必须表现出明显的逻辑断层、急躁、停顿（多用省略号）或者直接的情绪宣泄。彻底撕下礼貌的面具，可以直接反击或拒绝交流。")
        else:
            sub_annoyance = self.subconscious_fluid.get("厌烦", 0.0)
            sur_joy = self.surface_fluid.get("喜悦", 0.0)
            if sub_annoyance > 0.2 and sur_joy > 0.2:
                prompt.append("⚠️【认知失调特征：假性迎合】")
                prompt.append(">>> 指令约束：你正在强颜欢笑。文字表面客气，但必须在小动作、微表情或末尾的语气词中，流露出无法掩饰的不耐烦、敷衍或阴阳怪气。")

        prompt.append("\n【当前主导情绪水位】(严格遵循此数值进行剧本演绎)：")
        for tag, level in sorted(self.surface_fluid.items(), key=lambda x: x[1], reverse=True):
            if level > 0.0:
                prompt.append(f"- {tag}: {level:.2f}")

        return "\n".join(prompt)


# ==========================================
# 实验室模拟：一出决定论的心理崩溃戏剧
# ==========================================
if __name__ == "__main__":
    print(">>> SPL Lab: Bio-Mimetic Engine V3.0 Simulation Started <<<\n")
    agent = SPLBioMimeticAgent(name="林克", job_identity="调查员")
    
    print("【测试场景：用户连续使用同质化的‘夸奖’来试图刷好感度】\n")
    
    for i in range(1, 6):
        print(f"==================================================")
        print(f"🔄 第 {i} 轮输入: [用户触发事件 -> compliment (夸奖)]")
        
        agent.process_causal_event("compliment", raw_intensity=0.8)
        
        # 打印底层流体数据用于核对
        print(f"   [底层监控] 夸奖抗性: {agent.tolerance_matrix['compliment']:.2f} | 伪装耗能 -> 剩余能量: {agent.energy:.1f}")
        print(f"   [底层监控] 表意识: {agent.surface_fluid}")
        print(f"   [底层监控] 潜意识: {agent.subconscious_fluid}")
        print("-" * 50)
        
        # 输出给大模型的最终 Prompt
        print("📥 最终喂给大模型的硬编码 Prompt:\n")
        print(agent.generate_somatic_prompt())
        print("\n\n")
        
        time.sleep(0.5) # 模拟真实推演间隔
