# ================================================================
# 台词模块接通演示（Language Style · 端到端）
# 把 SPL Pure Core V8.0 主引擎 与 feature/language style.py 台词模块接通：
#   事件(NarrativeMapper) → 核心引擎(SPLPureCoreV7_3.snapshot) → 台词风格(render_style)
#
# 运行：python "feature/language-style-demo.py"
# 依赖：SPL-anthropic-engine.py + feature/language style.py（均在仓库内，零第三方依赖）
# ================================================================
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 1) 主引擎（连字符文件名，需 importlib 加载）
core_mod = _load("spl_core", os.path.join(ROOT, "SPL-anthropic-engine.py"))
# 2) 台词模块（文件名带空格，同样需 importlib 加载）
lang_mod = _load("lang_style", os.path.join(HERE, "language style.py"))

SPLPureCoreV7_3 = core_mod.SPLPureCoreV7_3
NarrativeMapper = core_mod.NarrativeMapper
LanguageStyleEngine = lang_mod.LanguageStyleEngine
LanguagePersonaEngine = lang_mod.LanguagePersonaEngine
LanguagePersona = lang_mod.LanguagePersona
StyleProfile = lang_mod.StyleProfile


def chat_round(core, persona, style_profile, event, intensity=1.0):
    """单轮端到端：喂事件 → 引擎推演 → 台词风格指令。"""
    # 事件 → 内感受向量 → 核心引擎
    vec = NarrativeMapper.map_event(event, intensity)
    core.process_vector(vec, intensity, event_id=event)
    snapshot = core.snapshot()

    # 语言人格过滤 + 风格渲染
    persona_engine = LanguagePersonaEngine(persona, style_profile)
    expression = persona_engine.filter_expression(snapshot)
    rendered = LanguageStyleEngine(style_profile).render_style(snapshot, expression=expression)

    return snapshot, expression, rendered


def show(title, snapshot, expression, rendered, style_profile):
    print("=" * 70)
    print("■", title)
    print("-" * 70)
    fluid = snapshot.get("fluid", {})
    print(f"  内心状态  : 喜悦{f['喜悦']:.2f} 恐惧{f['恐惧']:.2f} 信任{f['信任']:.2f} 张力{f['张力']:.2f}"
          f" 羞耻{f['羞耻']:.2f} 愤怒{f['愤怒']:.2f}" if (f := fluid) else "  -")
    print(f"  能量/疲劳 : 能量{snapshot.get('energy',0):.0f} 疲劳{snapshot.get('fatigue',0):.2f}"
          f" 否认仓{snapshot.get('denial_load',0):.2f}")
    print(f"  表达模式  : {expression.expression_mode}  情绪隐藏:{expression.emotion_hidden}")
    print(f"  真实意图  : {expression.speech_intention}  沉默:{expression.should_silence}")
    if expression.should_silence and rendered.silence_hint:
        print(f"  【台词】  : {rendered.silence_hint}")
    else:
        print(f"  【合成台词】: {LanguageStyleEngine(style_profile).generate_line(snapshot, expression)}")
    print("  【LLM Prompt】")
    for line in rendered.prompt_injection.split("\n"):
        print("    ", line)


if __name__ == "__main__":
    print("SPL Pure Core V8.0 × Language Style 台词模块 · 端到端接通演示\n")

    # 场景：熬夜 + 高否认 + 高羞耻 → 人格过滤
    base_core = SPLPureCoreV7_3()
    # 先注入一个"背叛"事件制造创伤与不信任，再注入"羞辱"制造高羞耻/高否认
    base_core.process_vector(NarrativeMapper.map_event("betrayal", 1.0), 1.0, "betrayal")
    base_core.process_vector(NarrativeMapper.map_event("insult", 1.0), 1.0, "insult")

    # ── 角色 A：祁皇英（高压控制型，情绪深藏，触发沉默）──
    qhy = LanguagePersona(mode="restrained", silence_policy=True,
                          silence_hint="她没有回答。只是垂下眼帘，避开了目光。")
    qhy_style = StyleProfile(base_verbosity=0.4, formality=0.9, sarcasm_tendency=0.4)
    snap, expr, rnd = chat_round(base_core, qhy, qhy_style, "insult", 1.0)
    show("祁皇英（restrained · 沉默策略）", snap, expr, rnd, qhy_style)

    # ── 角色 B：素锦（坦率直接，情绪如常表露）──
    sujin = LanguagePersona(mode="direct", silence_policy=False)
    sujin_style = StyleProfile(base_verbosity=0.7, formality=0.4, sarcasm_tendency=0.2)
    snap2, expr2, rnd2 = chat_round(base_core, sujin, sujin_style, "compliment", 0.8)
    show("素锦（direct · 情绪外露）", snap2, expr2, rnd2, sujin_style)
