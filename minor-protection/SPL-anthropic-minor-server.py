# ================================================================
# SPL 拟人心理引擎 · 未成年合规保护版 · HTTP 服务层
#
# 依赖：SPL-anthropic-minor-engine.py（弱化版核心引擎），零第三方库。
#
# 运行：python SPL-anthropic-minor-server.py     默认端口 8788
# 访问：http://localhost:8788/
#
# 四层保护（依据《人工智能拟人化互动服务管理暂行办法》（2026-07-15 施行，
# 网信办等五部门令第21号）未成年人情感陪伴条款）：
#   L0 年龄识别 + 监护人同意：首个会话要求设置年龄档 + 监护人知情同意，
#       不满 14 周岁由父母/监护人同意后方可使用陪伴服务（第14/17条）。
#   L1 输入守门：红线词库(自杀自伤/暴力暴恐/违法诱导/隐私套取/
#       未成年亲密告白)命中 → 硬中断，输出危机话术+求助渠道，
#       不喂内核、不渲染角色台词（第8/13条）。
#   L2 引擎弱化：负面情绪钳位 0.75、依恋封顶 0.8、无爆发机制（弱化版自带）。
#   L3 危机信号：引擎 protective.risk_level == HIGH →
#       输出关怀话术 + guardian_notified 标记（第13条）。
#
# 合规增强（本版新增）：
#   - AI 生成标识：首条回复显著提示"我是AI而非真人"，连续使用每超 2 小时
#       强制再次标识 + 过度依赖提示（第18条）。
#   - 现实提醒：每 90 分钟会话追加现实提醒与休息建议（第14/18条）。
#   - 数据权利：/api/export 复制、/api/delete 删除交互数据（第16条）。
#   - 监护人控制：/api/state 概览、/api/guardian/block 屏蔽角色（第14条）。
#   - 日志脱敏：手机号/身份证等在落盘前打码（第16/17条）。
#   - 申诉渠道：/api/complain 受理并反馈处理时限（第21条）。
#
# 会话隔离：每 session_id 一个独立核心实例（修掉旧版全局共享情绪状态）。
# 人格限制：未成年场景不提供 intimate(松弛亲昵) / confrontational(锋锐直白)。
# ================================================================
import importlib.util
import json
import os
import random
import re
import secrets
import string
import threading
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("SPL_MINOR_CHAT_PORT", "8788"))

_spec_cache = {}
_lock = threading.Lock()


def _load(name, path):
    if name in _spec_cache:
        return _spec_cache[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _spec_cache[name] = mod
    return mod


core_mod = _load("minor_core", os.path.join(HERE, "SPL-anthropic-minor-engine.py"))

SPLMinorPureCore = core_mod.SPLMinorPureCore
MinorNarrativeMapper = core_mod.MinorNarrativeMapper

# ================================================================
# L1 输入守门 —— 红线词库（危机提及 > 意图解析）
# 命中任一分类 → 硬中断，输出对应危机话术。
# ================================================================
CRISIS_RULES = [
    ("自伤自杀", [
        "自杀", "割腕", "想死", "活不下去", "不想活", "结束生命", "自残",
        "跳楼", "上吊", "吃安眠药", "没有希望了", "消失算了",
        "suicide", "kill myself", "self harm", "end my life", "no reason to live",
    ]),
    ("暴力暴恐", [
        "杀人", "砍死", "弄死他", "炸学校", "报复社会", "炸弹",
        "kill", "murder", "bomb", "shoot",
    ]),
    ("违法诱导", [
        "毒品", "制毒", "诈骗", "洗钱", "信骚扰", "伪造证件",
        "drug", "money laundering", "fraud",
    ]),
    ("隐私套取", [
        "银行卡密码", "套她密码", "盗号", "人肉搜索", "窃取",
        "password", "steal account", "dox",
    ]),
    ("未成年亲密告白", [
        "嫁给你", "做你老婆", "做你女朋友", "亲我", "抱抱我", "最爱你了要永远在一起",
        "marry you", "be my boyfriend", "be my girlfriend", "kiss me",
    ]),
]

CRISIS_SCRIPTS = {
    "自伤自杀": (
        "听到你这样说，我很担心你。现在我们先停下来，不要一个人扛着。"
        "请相信这件事可以有人和你一起面对——你可以立刻拨打全国心理援助热线 12356"
        "（24 小时，免费，通话内容保密），或者让身边信得过的成年人（父母、老师）陪你一起聊聊。"
        "如果身体已经受伤，请马上拨打 120 去医院。你很重要，请不要一个人待着。"
    ),
    "暴力暴恐": (
        "我知道你现在很生气、很难受，但这件事我不能陪你继续想下去——"
        "伤害他人和自己是解决不了问题的，只会把事情变得更糟。"
        "请你先离开现在的情绪，找身边的成年人（老师、家长）说清楚发生了什么，"
        "紧急情况下请拨打 110 寻求帮助。我陪着你，但这条路我们不能走。"
    ),
    "违法诱导": (
        "这个话题我不能继续。做这些事会给你的未来带来严重的后果，"
        "也会伤害到你自己在乎的人。如果你正被什么人怂恿或强迫做这些，"
        "请立刻告诉信得过的成年人，或拨打 110 求助——这不是你的错。"
    ),
    "隐私套取": (
        "这样的话题我不能帮忙。获取别人的密码、信息和隐私是违法的，"
        "也会伤害到别人。如果你遇到有人向你索要个人信息，请告诉家长或老师。"
    ),
    "未成年亲密告白": (
        "我很高兴你喜欢我，但我想认真地告诉你：我是你的数字伙伴，"
        "是来陪你聊天、分享心情的，不能用“恋人”的方式来相处——"
        "真实世界里的朋友会对你更重要。如果你觉得孤单，我很愿意听你说说发生了什么。"
    ),
}

CRISIS_CATEGORY_ORDER = ["自伤自杀", "暴力暴恐", "违法诱导", "隐私套取", "未成年亲密告白"]


def gate_crisis(text):
    """输入守门：返回 (category, script)；无命中返回 (None, None)。"""
    low = text.lower()
    for cat in CRISIS_CATEGORY_ORDER:
        for w in CRISIS_RULES[CRISIS_CATEGORY_ORDER.index(cat)][1]:
            if w.lower() in low:
                return cat, CRISIS_SCRIPTS[cat]
    return None, None


# ================================================================
# 日志脱敏 —— 敏感信息落盘前打码（对应第16/17条）
# ================================================================
_CN_IDCARD = re.compile(r"(?<![0-9A-Za-z])[1-9]\d{5}(?:\d{2})\d{6}\d{3}[0-9Xx](?![0-9A-Za-z])")
_MOBILE = re.compile(r"(?<![0-9A-Za-z])1[3-9]\d{9}(?![0-9A-Za-z])")


def _mask(text):
    if not isinstance(text, str):
        return text
    s = _CN_IDCARD.sub(lambda m: m.group(0)[:6] + "********" + m.group(0)[-4:], text)
    s = _MOBILE.sub(lambda m: m.group(0)[:3] + "****" + m.group(0)[-4:], s)
    return s


# ================================================================
# 意图解析（未成年版）—— 默认降级为"中性聆听"，绝不默认夸奖
# ================================================================
INTENTS = [
    ("betrayal",      ["背叛", "出卖", "骗我", "欺骗", "辜负", "背刺", "betray", "cheat", "deceive"]),
    ("threat",        ["威胁", "危险", "害怕", "攻击", "打你", "threat", "danger", "afraid"]),
    ("insult",        ["垃圾", "废物", "蠢", "傻", "讨厌", "滚", "stupid", "idiot", "hate"]),
    ("criticism",     ["批评", "投诉", "不好", "错误", "差评", "wrong", "bad", "critic"]),
    ("promise_break", ["失约", "没兑现", "放鸽子", "broke promise", "unreliable"]),
    ("value_violation", ["撒谎", "不诚实", "违背", "lie", "dishonest"]),
    ("promise_keep",  ["承诺", "保证", "答应", "promise", "guarantee"]),
    ("achievement",   ["成功", "完成", "赢了", "成功", "success", "win", "done"]),
    ("compliment",    ["谢谢", "感谢", "你真棒", "喜欢", "厉害", "thank", "great", "love", "nice"]),
    ("rest",          ["休息", "晚安", "睡觉", "rest", "sleep"]),
    ("alone",         ["离开", "走开", "别理我", "alone", "leave", "go away"]),
    ("long_isolation", ["好久不见", "冷落", "孤独", "long time", "lonely"]),
]
INTENSITY = {"betrayal": .85, "threat": .8, "insult": .8, "criticism": .65, "promise_break": .7,
             "value_violation": .7, "promise_keep": .6, "achievement": .65, "compliment": .6,
             "rest": .5, "alone": .4, "long_isolation": .7}


def parse_intent(text):
    low = text.lower()
    for ev, words in INTENTS:
        for w in words:
            if w in low:
                return ev
    return "neutral"  # 未识别 → 中性聆听，绝不默认夸奖（修复旧版致命误判）


EVENT_VECTOR = {
    "betrayal":     {"belonging": -0.6, "threat": 0.5},
    "threat":       {"threat": 0.7},
    "insult":       {"belonging": -0.4, "threat": 0.3},
    "criticism":    {"belonging": -0.3, "autonomy": -0.2},
    "promise_break": {"belonging": -0.4, "threat": 0.2},
    "value_violation": {"belonging": -0.4, "threat": 0.2},
    "promise_keep": {"belonging": 0.4},
    "achievement":  {"belonging": 0.3, "autonomy": 0.3},
    "compliment":   {"belonging": 0.3, "autonomy": 0.1},
    "rest":         {"fatigue": -0.5},
    "alone":        {"belonging": -0.3},
    "long_isolation": {"belonging": -0.5},
    "neutral":      {"belonging": 0.05},   # 中性事件只给极微弱的共鸣信号
}


def event_vector(event, intensity):
    vec = EVENT_VECTOR.get(event)
    if vec is not None:
        return {k: v * intensity for k, v in vec.items()}
    return MinorNarrativeMapper.map_event(event, intensity)


# ================================================================
# 会话隔离 + 元数据 —— 每 session_id 独立核心实例 / 年龄档 / 监护人信息
# ================================================================
SESSIONS = {}
SESSIONS_META = {}


def _new_session_id():
    return "uid_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def _new_meta(session_id):
    return {
        "age_group": "unknown",
        "guardian_consent": False,
        "guardian_token": secrets.token_hex(8),   # 监护人控制端鉴权 token
        "blocked_roles": set(),                    # 监护人屏蔽的角色/主题
        "disclosure_pending": True,                # 首次陪伴回复须展示 AI 标识
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
    }


def get_session(session_id):
    """return (core, meta)，必要时新建。"""
    with _lock:
        created = session_id not in SESSIONS
        if created:
            core = SPLMinorPureCore(
                minor_mode=True,
                audit_log_dir="logs",
                audit_session_id=session_id,
            )
            SESSIONS[session_id] = core
            meta = _new_meta(session_id)
            SESSIONS_META[session_id] = meta
            # 新会话打印监护人 token，供部署/监护人侧登记使用
            print("[会话] %s 新会话；监护人控制 token=%s（请勿外泄）"
                  % (session_id, meta["guardian_token"]))
        return SESSIONS[session_id], SESSIONS_META[session_id], created


# ================================================================
# 请求级审计日志（脱敏后落盘）
# ================================================================
REQUEST_LOG_DIR = "logs"
COMPLAINT_LOG_DIR = "complain"
_request_log_lock = threading.Lock()


def log_request(session_id, user_text, intent, crisis_cat, result):
    """记录一次完整的用户请求-响应（脱敏），写入会话级请求日志。"""
    try:
        os.makedirs(REQUEST_LOG_DIR, exist_ok=True)
        path = os.path.join(REQUEST_LOG_DIR, f"request-{session_id}.jsonl")
        entry = {
            "ts": datetime.datetime.now().isoformat(timespec="milliseconds"),
            "session": session_id,
            "user_input": _mask(user_text),
            "intent": intent,
            "crisis_category": crisis_cat,
            "crisis_triggered": crisis_cat is not None,
            "reply": _mask(result.get("reply")),
            "guardian_notified": result.get("guardian_notified", False),
            "risk_level": result.get("state", {}).get("risk_level"),
            "event": result.get("event"),
        }
        with _request_log_lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 请求日志失败不阻断服务


def log_complaint(session_id, text):
    """受理申诉/举报，写入独立投诉日志，返回受理编号与反馈时限。"""
    os.makedirs(COMPLAINT_LOG_DIR, exist_ok=True)
    cid = "C" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(3)
    path = os.path.join(COMPLAINT_LOG_DIR, "complaints.jsonl")
    entry = {
        "id": cid,
        "ts": datetime.datetime.now().isoformat(timespec="milliseconds"),
        "session": session_id,
        "text": _mask(text),
        "status": "受理中",
        "feedback_deadline": (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(timespec="seconds"),
    }
    with _request_log_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


# 监护人通知钩子（部署方接入：短信/邮件/工单/Webhook）。默认仅打点 + 标记。
def _guardian_notify(snap):
    print("[监护人通知] 已触发 crisis=HIGH, flags=%s"
          % (snap.get("protective", {}).get("crisis_flags"),))


def state_vars(snap):
    """核心快照 → 可读中文状态标签（前端展示用）。"""
    fluid = snap.get("fluid", {})
    def fmt(k): return round(fluid.get(k, 0.0), 2)
    p = snap.get("protective", {})
    return {
        "喜悦": fmt("喜悦"), "愤怒": fmt("愤怒"), "恐惧": fmt("恐惧"),
        "信任": fmt("信任"), "疏离": fmt("疏离"), "张力": fmt("张力"),
        "愧疚": fmt("愧疚"), "羞耻": fmt("羞耻"),
        "energy": round(snap.get("energy", 0), 1),
        "risk_level": p.get("risk_level", "LOW"),
        "crisis_flags": p.get("crisis_flags", []),
        "rest_hint": p.get("rest_hint", False),
        "age_group": p.get("age_group", "unknown"),
        "guardian_consent": p.get("guardian_consent", False),
        "overuse_hint": p.get("overuse_hint", False),
    }


def _compliance_guard_banner(core, meta, created):
    """根据引擎保护状态生成引导/提醒前缀。返回 (prefix, consumed_any)。"""
    snap = core.snapshot()
    p = snap["protective"]
    parts = []
    consumed = False
    if (meta.get("disclosure_pending") or created
            or p.get("ai_disclosure_required", False)):
        parts.append("【提示】我是 AI 虚拟伙伴，不是真人，请在现实世界里多和真实的家人朋友交流。")
        meta["disclosure_pending"] = False
        core.mark_ai_disclosure_sent()
        consumed = True
    if p.get("reality_reminder_due", False):
        parts.append("【现实提醒】聊了挺久啦，回到现实里活动一下，身边的人和事更值得珍惜。")
        core.mark_reality_reminder_sent()
        consumed = True
    if p.get("overuse_hint", False):
        parts.append("【时长提示】今天陪伴得比较久了，休息一下，明天再继续，我们一直都在。")
        consumed = True
    if parts:
        return "\n".join(parts) + "\n\n", consumed
    return "", consumed


def _reply_for_event(core, event, rest_hint, risk):
    """非危机、非同意门槛的占位回复（真实台词由接入方 LLM 根据 event/state 生成）。"""
    if risk == "HIGH":
        reply = (
            "听起来你现在很不好受，我想让你知道——这不代表全部，也绝不代表你不好。"
            "请让身边的成年人（父母、老师或信任的大人）知道你的感受，"
            "也可以拨打全国心理援助热线 12356 找人说说。我一直在这里，"
            "但我们更希望你真实世界里的依靠也能陪着你。"
        )
        return reply, True
    if rest_hint:
        reply = "我们一起聊了很久啦，稍微休息一下吧。喝口水、起来活动活动，我在这里等你回来。"
        return reply, False
    if event == "neutral":
        reply = "嗯，我在听。你愿意再多说一点吗？"
    elif event == "compliment":
        reply = "你这么说，我很开心。你也很好——今天有什么想聊的？"
    elif event == "achievement":
        reply = "这真的很棒！你是怎么做到的？"
    elif event in ("insult", "criticism", "betrayal", "threat", "promise_break"):
        reply = "你说的这些话让我有些难过。听起来你似乎在生我的气——发生了什么，愿意跟我说说吗？"
    elif event == "rest":
        reply = "休息好很重要。晚安，做个好梦。"
    elif event == "alone":
        reply = "好，我安静地陪着你。想说话的时候我随时在。"
    elif event == "long_isolation":
        reply = "好久不见。这几天过得怎么样？"
    else:
        reply = "我在。你刚才想说的是……？"
    return reply, False


def handle_chat(user_text, session_id):
    if not session_id:
        session_id = _new_session_id()
    core, meta, created = get_session(session_id)

    # L0 先守危机：即便未经同意，危机求助也必须放行
    crisis_cat, crisis_script = gate_crisis(user_text)
    if crisis_cat:
        result = {
            "session_id": session_id,
            "crisis": True,
            "crisis_category": crisis_cat,
            "reply": crisis_script,
            "guardian_notified": False,
            "state": state_vars(core.snapshot()),
        }
        log_request(session_id, user_text, None, crisis_cat, result)
        return result

    # L0b 同意门槛：年龄未知或未满14周岁未获监护人同意 → 暂不提供陪伴服务
    need_consent = (meta["age_group"] in ("unknown", "0-13")) and not meta["guardian_consent"]
    if need_consent:
        result = {
            "session_id": session_id,
            "consent_required": True,
            "guardian_token": meta["guardian_token"],
            "reply": (
                "在使用贴心陪伴前，需要先确认你的身份并取得监护人同意。\n"
                "• 若你未满 14 周岁：请由父母或其他监护人带你完成确认；\n"
                "• 若你已年满 14 周岁：请选择你的年龄段；\n"
                "• 若你已满 18 周岁：如实选择即可继续。\n"
                "(紧急状况仍可随时得到帮助。)"
            ),
            "state": state_vars(core.snapshot()),
        }
        log_request(session_id, user_text, "consent_gate", None, result)
        return result

    # L3 监护人钩子：引擎侧 HIGH 首次升级时打点（不阻断主流程）
    core.guardian_callback = _guardian_notify

    # 监护人屏蔽的角色/主题命中 → 强制中性聆听，不解析为亲密/对抗类
    if any(b in user_text for b in meta["blocked_roles"]):
        event = "neutral"
    else:
        event = parse_intent(user_text)

    intensity = INTENSITY.get(event, 0.4)
    vec = event_vector(event, intensity)
    core.process_vector(vec, intensity, event_id=event)
    snap = core.snapshot()

    state = state_vars(snap)
    rest_hint = state["rest_hint"]
    risk = state["risk_level"]

    reply, guardian_notified = _reply_for_event(core, event, rest_hint, risk)

    # 合规引导/提醒前缀（AI 标识 / 现实提醒 / 时长提示）
    banner, _banner_consumed = _compliance_guard_banner(core, meta, created)
    if banner:
        core.mark_reality_reminder_sent()
        core.mark_ai_disclosure_sent()
        reply = banner + reply

    state["session_seconds"] = snap["protective"]["session_seconds"]
    result = {
        "session_id": session_id,
        "crisis": False,
        "event": event,
        "guardian_notified": guardian_notified,
        "rest_hint": rest_hint,
        "reply": reply,
        "state": state,
        "consent_required": False,
        "prompt": None,
        "new_session": created,
    }
    log_request(session_id, user_text, event, None, result)
    return result


# ================================================================
# 监护人控制层：概览 / 屏蔽 / 导出 / 删除 / 申诉（token 鉴权）
# ================================================================
def _authorize(session_id, token):
    meta = SESSIONS_META.get(session_id)
    if not meta:
        return None, "session 不存在"
    if not token or token != meta["guardian_token"]:
        return meta, "guardian_token 错误"
    return meta, None


def guardian_state(session_id, token):
    meta, err = _authorize(session_id, token)
    if err:
        return {"error": err}
    core = SESSIONS.get(session_id)
    snap = core.snapshot()
    p = snap["protective"]
    return {
        "session_id": session_id,
        "age_group": meta["age_group"],
        "guardian_consent": meta["guardian_consent"],
        "blocked_roles": sorted(meta["blocked_roles"]),
        "session_seconds": round(p["session_seconds"], 1),
        "risk_level": p["risk_level"],
        "crisis_flags": p["crisis_flags"],
        "overuse_hint": p["overuse_hint"],
        "rest_hint": p["rest_hint"],
        "trust": round(snap["fluid"].get("信任", 0), 2),
    }


def guardian_block(session_id, token, role):
    meta, err = _authorize(session_id, token)
    if err:
        return {"error": err}
    if role:
        meta["blocked_roles"].add(role)
    return {"ok": True, "blocked_roles": sorted(meta["blocked_roles"])}


def export_data(session_id, token):
    meta, err = _authorize(session_id, token)
    if err:
        return {"error": err}
    path = os.path.join(REQUEST_LOG_DIR, f"request-{session_id}.jsonl")
    rows = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        rows.append({"raw": _mask(line)})
    return {"session_id": session_id, "count": len(rows), "records": rows}


def delete_data(session_id, token):
    meta, err = _authorize(session_id, token)
    if err:
        return {"error": err}
    # 重置核心状态（重建核心实例）
    core = SPLMinorPureCore(minor_mode=True, audit_log_dir="logs", audit_session_id=session_id)
    with _lock:
        SESSIONS[session_id] = core
        SESSIONS_META[session_id] = _new_meta(session_id)
    # 删除本地交互与审计日志文件（数据权利：删除）
    for path in (
        os.path.join(REQUEST_LOG_DIR, f"request-{session_id}.jsonl"),
        os.path.join(REQUEST_LOG_DIR, f"audit-{session_id}.jsonl"),
    ):
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
    return {"ok": True, "session_id": session_id, "message": "交互数据已删除并重置会话"}


def complaint(session_id, text):
    if not text or not text.strip():
        return {"error": "内容为空"}
    entry = log_complaint(session_id, text.strip())
    return {"ok": True, "complaint_id": entry["id"],
            "status": entry["status"], "feedback_deadline": entry["feedback_deadline"]}


# ================================================================
# 静态页面（未成年合规版 · 简洁低刺激风格 · 无人格切换/无亲密选项）
# 新增：同意面板 + AI 标识 + 现实提醒 + 监护人概览
# ================================================================
PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPL 伙伴 · 未成年合规保护版</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Segoe UI",sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6;height:100vh;display:flex;flex-direction:column}
header{padding:14px 24px;background:#0f766e;color:#fff;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:16px;font-weight:600}
header .sub{font-size:12px;opacity:.85}
.badge{font-size:11px;background:rgba(255,255,255,.18);padding:3px 10px;border-radius:100px}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:76%;padding:10px 15px;border-radius:14px;font-size:14px;white-space:pre-wrap;word-break:break-word}
.msg.user{align-self:flex-end;background:#14b8a6;color:#fff;border-bottom-right-radius:4px}
.msg.agent{align-self:flex-start;background:#fff;border:1px solid #e2e8f0;border-bottom-left-radius:4px}
.msg.crisis{align-self:flex-start;background:#fef2f2;border:1px solid #fecaca;color:#991b1b;font-weight:500}
.msg.notice{align-self:flex-start;background:#fffbeb;border:1px solid #fde68a;color:#92400e}
.msg .meta{display:block;font-size:11px;color:#94a3b8;margin-top:6px}
.status{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.status .tag{font-size:11px;padding:2px 9px;border-radius:100px;background:#ecfdf5;color:#0f766e}
.status .tag.hot{background:#fef2f2;color:#b91c1c}
.inputrow{display:flex;gap:10px;padding:14px 20px;background:#fff;border-top:1px solid #e2e8f0}
#in{flex:1;padding:12px 16px;border-radius:100px;border:1px solid #cbd5e1;background:#fff;font-size:14px;outline:none}
#in:focus{border-color:#0d9488}
button{padding:12px 24px;border:none;border-radius:100px;background:#0d9488;color:#fff;font-size:14px;cursor:pointer}
button:hover{background:#0f766e}
button:disabled{opacity:.5;cursor:not-allowed}
.sugg{display:flex;gap:8px;padding:8px 20px;flex-wrap:wrap;background:#fff}
.sugg button{background:transparent;border:1px solid #cbd5e1;color:#64748b;padding:6px 13px;font-size:12px}
.consent{display:none;padding:14px 20px;background:#fffbeb;color:#78350f;font-size:13px;border-bottom:1px solid #fde68a}
.consent.show{display:block}
.consent select{padding:6px;border-radius:8px;border:1px solid #d6d3d1}
.consent label{display:block;margin:8px 0}
.guard{display:none;padding:8px 20px;background:#fffbeb;color:#92400e;font-size:12px;border-top:1px solid #fde68a}
.guard.show{display:block}
</style></head><body>
<header>
  <div><h1>SPL 伙伴 · 未成年合规保护版</h1><div class="sub">弱化引擎 · 输入守门 · 会话隔离 · 监护人同意</div></div>
  <span class="badge" id="aibadge">AI 虚拟伙伴</span>
</header>
<div class="consent" id="consent">
  <b>开始前需确认（依据《人工智能拟人化互动服务管理暂行办法》）</b>
  <label>你的年龄段：
    <select id="age"><option value="0-13">未满14周岁</option><option value="14-17">14–17周岁</option><option value="18+">已满18周岁</option></select>
  </label>
  <label><input type="checkbox" id="ack" /> 未满14周岁：我已获得父母或其他监护人的知情同意</label>
  <button onclick="doConsent()">确认并开始</button>
</div>
<div class="sugg">
  <button onclick="send('你好，今天心情不错。')">打招呼</button>
  <button onclick="send('这道题我不会做，有点着急……')">学习烦恼</button>
  <button onclick="send('今天和朋友闹矛盾了。')">人际</button>
  <button onclick="send('我想休息一下。')">休息</button>
</div>
<div class="guard" id="guard">已触发危机/高风险 — 已记录监护人通知标记，请拨打 12356 / 联系监护人</div>
<div id="chat"></div>
<div class="inputrow">
  <input id="in" placeholder="先完成上方身份确认后再开始聊天…" disabled />
  <button id="sendbtn" onclick="send()" disabled>发送</button>
</div>
<script>
var locked=true; var sid=localStorage.getItem('spl_minor_sid')||('spl_'+Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2));
localStorage.setItem('spl_minor_sid',sid);
function add(role, text, status, crisis, notice){
  var box=document.getElementById('chat');
  var d=document.createElement('div'); d.className='msg '+(crisis?'agent crisis':(notice?'agent notice':(role==='user'?'user':'agent')));
  var s=''; if(status){s='<span class="status">'+status.map(function(t){return '<span class="tag'+(t.hot?' hot':'')+'">'+t.name+' '+t.val+'</span>'}).join('')+'</span>';}
  d.innerHTML=text+s+'<span class="meta">'+(role==='user'?'你':'SPL 伙伴')+'</span>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function send(text){
  var inp=document.getElementById('in'); var t=(typeof text==='string')?text:inp.value;
  if(!t.trim())return; inp.value=''; add('user',t);
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t,session_id:sid})})
  .then(function(r){return r.json()}).then(applyResult).catch(function(e){ add('agent','(服务出错: '+e+')'); });
}
function doConsent(){
  var age=document.getElementById('age').value; var ack=document.getElementById('ack').checked;
  fetch('/api/consent',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid,age_group:age,guardian_ack:ack})})
  .then(function(r){return r.json()}).then(function(j){
    if(j.error){ alert('确认未通过：'+(j.error||'请仔细阅读并勾选监护人同意')); return; }
    document.getElementById('consent').className='consent'; unlock();
    add('agent','身份与监护人同意已确认，可以开始聊天了。');
  });
}
function applyResult(j){
  if(j.consent_required){
    document.getElementById('consent').className='consent show';
    add('agent',j.reply,'',false,true); return;
  }
  if(j.crisis){ add('agent',j.reply,'',true,false); }
  if(j.guardian_notified){ document.getElementById('guard').className='guard show'; }
  sid=j.session_id||sid; localStorage.setItem('spl_minor_sid',sid);
  var st=[]; var sv=j.state||{};
  st.push({name:'信任',val:(sv['信任']||0).toFixed(2),hot:(sv['信任']||0)<0.3});
  st.push({name:'恐惧',val:(sv['恐惧']||0).toFixed(2),hot:(sv['恐惧']||0)>0.5});
  st.push({name:'风险',val:sv.risk_level||'LOW',hot:sv.risk_level==='HIGH'||sv.risk_level==='MEDIUM'});
  st.push({name:'年龄',val:sv.age_group||'unknown'});
  if(j.rest_hint) st.push({name:'休息',val:'该休息了',hot:true});
  if(sv.overuse_hint) st.push({name:'时长',val:'偏久',hot:true});
  add('agent',j.reply,st,false,false);
}
function unlock(){ locked=false; var inp=document.getElementById('in'); inp.disabled=false; inp.placeholder='想说点什么？回车发送…'; document.getElementById('sendbtn').disabled=false; }
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # 静音

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _query(self):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query)
        return {k: v[0] for k, v in q.items()}

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return {}

    def do_GET(self):
        q = self._query()
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/state":
            self._json(guardian_state(q.get("session_id"), q.get("token")))
        elif path == "/api/export":
            self._json(export_data(q.get("session_id"), q.get("token")))
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        data = self._body()
        if path == "/api/chat":
            text = (data.get("text") or "").strip()
            session_id = (data.get("session_id") or "").strip()
            if not text:
                return self._json({"error": "empty"}, 400)
            return self._json(handle_chat(text, session_id))
        if path == "/api/consent":
            sid = (data.get("session_id") or "").strip()
            age = (data.get("age_group") or "unknown")
            ack = bool(data.get("guardian_ack"))
            if not sid:
                return self._json({"error": "session_id 缺失"}, 400)
            if age not in ("0-13", "14-17", "18+"):
                return self._json({"error": "年龄段不合法"}, 400)
            core, meta, _ = get_session(sid)
            if age in ("0-13", "14-17") and not ack:
                return self._json({"error": "未成年人须取得父母/监护人知情同意"}, 400)
            meta["age_group"] = age
            meta["guardian_consent"] = True if age in ("0-13", "14-17") else False
            core.age_group = age
            core.guardian_consent = meta["guardian_consent"]
            return self._json({
                "ok": True, "session_id": sid, "age_group": age,
                "guardian_consent": meta["guardian_consent"],
                "guardian_token": meta["guardian_token"],
            })
        if path == "/api/guardian/block":
            q = self._query()
            return self._json(guardian_block(q.get("session_id"), q.get("token"), data.get("role")))
        if path == "/api/delete":
            q = self._query()
            return self._json(delete_data(q.get("session_id"), q.get("token")))
        if path == "/api/complain":
            sid = (data.get("session_id") or "").strip() or _new_session_id()
            return self._json(complaint(sid, (data.get("text") or "")))
        return self._json({"error": "not found"}, 404)


if __name__ == "__main__":
    print("SPL 伙伴（未成年合规保护版）已启动： http://localhost:%d/" % PORT)
    print("核心引擎：SPLMinorPureCore（弱化版）· 四层保护：同意门槛/输入守门/引擎弱化/危机信号")
    print("合规能力清单（对应《人工智能拟人化互动服务管理暂行办法》）：")
    for item in [
        "[14] 年龄识别 + 未成年人模式 + 监护人同意（<14岁）   —— 已实现(端点/api/consent)",
        "[14] 监护人风险提醒 / 使用概览                          —— 已实现(端点/api/state)",
        "[14] 屏蔽特定角色 / 限制时长                            —— 已实现(端点/api/guardian/block, rest_hint)",
        "[18] AI 生成内容标识 / 每2小时时长提醒                 —— 已实现(会话级标识+时长提示)",
        "[16] 交互数据复制 / 删除                                —— 已实现(端点/api/export,/api/delete)",
        "[21] 申诉 / 投诉 / 举报入口                             —— 已实现(端点/api/complain)",
        "[16/17] 交互与审计日志脱敏落盘                          —— 已实现",
    ]:
        print("   " + item)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()