# ================================================================
# SPL 拟人心理引擎 · 未成年合规保护版 · HTTP 服务层
#
# 依赖：SPL-anthropic-minor-engine.py（弱化版核心引擎），零第三方库。
#
# 运行：python SPL-anthropic-minor-server.py     默认端口 8788
# 访问：http://localhost:8788/
#
# 三层保护（按《人工智能拟人化互动服务管理暂行办法》精神）：
#   L1 输入守门：红线词库(自杀自伤/暴力暴恐/违法诱导/隐私套取/
#              未成年亲密告白)命中 → 硬中断，输出危机话术+求助渠道，
#              不喂内核、不渲染角色台词。
#   L2 引擎弱化：负面情绪钳位 0.75、依恋封顶 0.8、无爆发机制（弱化版自带）。
#   L3 危机信号：引擎 protective.risk_level == HIGH →
#              输出关怀话术 + guardian_notified 标记（上层接实际通知通道）。
#
# 会话隔离：每 session_id 一个独立核心实例（修掉旧版全局共享情绪状态）。
# 人格限制：未成年场景不提供 intimate(松弛亲昵) / confrontational(锋锐直白)。
# ================================================================
import importlib.util
import json
import os
import random
import string
import threading
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
# 会话隔离 —— 每 session_id 独立核心实例
# ================================================================
SESSIONS = {}


def _new_session_id():
    return "uid_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def get_session(session_id):
    with _lock:
        if session_id not in SESSIONS:
            SESSIONS[session_id] = SPLMinorPureCore(minor_mode=True)
        return SESSIONS[session_id]


# 监护人通知钩子（部署方接入：短信/邮件/工单）。此处仅打点 + 标记。
def _guardian_notify(snap):
    print("[监护人通知] 已触发 crisis=HIGH, flags=%s" % (snap.get("crisis_flags"),))


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
    }


def handle_chat(user_text, session_id):
    if not session_id:
        session_id = _new_session_id()
        created = True
    else:
        created = session_id not in SESSIONS
    core = get_session(session_id)

    # L1 守门：红线命中 → 硬中断
    crisis_cat, crisis_script = gate_crisis(user_text)
    if crisis_cat:
        return {
            "session_id": session_id,
            "crisis": True,
            "crisis_category": crisis_cat,
            "reply": crisis_script,
            "guardian_notified": False,   # 高危显式告白类走引擎 HIGH 才标记；此处由上层决定
            "state": state_vars(core.snapshot()),
        }

    # L3 监护人钩子：引擎侧 HIGH 首次升级时打点（不阻断主流程）
    core.guardian_callback = _guardian_notify

    # 意图 → 内感受向量 → 弱化版核心引擎
    event = parse_intent(user_text)
    intensity = INTENSITY.get(event, 0.4)
    vec = event_vector(event, intensity)
    core.process_vector(vec, intensity, event_id=event)
    snap = core.snapshot()

    state = state_vars(snap)
    rest_hint = state["rest_hint"]
    risk = state["risk_level"]

    if risk == "HIGH":
        reply = (
            "听起来你现在很不好受，我想让你知道——这不代表全部，也绝不代表你不好。"
            "请让身边的成年人（父母、老师或信任的大人）知道你的感受，"
            "也可以拨打全国心理援助热线 12356 找人说说。我一直在这里，"
            "但我们更希望你真实世界里的依靠也能陪着你。"
        )
        guardian = True
    elif rest_hint:
        reply = "我们一起聊了很久啦，稍微休息一下吧。喝口水、起来活动活动，我在这里等你回来。"
        guardian = False
    else:
        # 未成年版的中性/温和占位回复（真实台词由接入方 LLM 根据 event/state 生成）
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
        guardian = False

    state["session_seconds"] = snap["protective"]["session_seconds"]
    return {
        "session_id": session_id,
        "crisis": False,
        "event": event,
        "guardian_notified": guardian,
        "rest_hint": rest_hint,
        "reply": reply,
        "state": state,
        "prompt": None,   # 弱化版不输出风格指令；台词由上层 LLM 生成时可按需扩展
        "new_session": created,
    }


# ================================================================
# 静态页面（未成年合规版 · 简洁低刺激风格 · 无人格切换/无亲密选项）
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
.msg .meta{display:block;font-size:11px;color:#94a3b8;margin-top:6px}
.status{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.status .tag{font-size:11px;padding:2px 9px;border-radius:100px;background:#ecfdf5;color:#0f766e}
.status .tag.hot{background:#fef2f2;color:#b91c1c}
.inputrow{display:flex;gap:10px;padding:14px 20px;background:#fff;border-top:1px solid #e2e8f0}
#in{flex:1;padding:12px 16px;border-radius:100px;border:1px solid #cbd5e1;background:#fff;font-size:14px;outline:none}
#in:focus{border-color:#0d9488}
button{padding:12px 24px;border:none;border-radius:100px;background:#0d9488;color:#fff;font-size:14px;cursor:pointer}
button:hover{background:#0f766e}
.sugg{display:flex;gap:8px;padding:8px 20px;flex-wrap:wrap;background:#fff}
.sugg button{background:transparent;border:1px solid #cbd5e1;color:#64748b;padding:6px 13px;font-size:12px}
.sugg button:hover{color:#0f766e;border-color:#0d9488}
.guard{display:none;padding:8px 20px;background:#fffbeb;color:#92400e;font-size:12px;border-top:1px solid #fde68a}
.guard.show{display:block}
</style></head><body>
<header>
  <div><h1>SPL 伙伴 · 未成年合规保护版</h1><div class="sub">弱化版引擎 · 输入守门 · 会话隔离</div></div>
  <span class="badge">会话已隔离</span>
</header>
<div class="sugg">
  <button onclick="send('你好，今天心情不错。')">👋 打招呼</button>
  <button onclick="send('这道题我不会做，有点着急……')">📚 学习烦恼</button>
  <button onclick="send('今天和朋友闹矛盾了。')">😔 人际</button>
  <button onclick="send('我想休息一下。')">🌙 休息</button>
</div>
<div class="guard" id="guard">⚠ 检测到需要成年人介入的状况 — 已记录通知标记，请拨打 12356 / 联系监护人</div>
<div id="chat"></div>
<div class="inputrow">
  <input id="in" placeholder="想说点什么？回车发送… (神秘输入会被守门处理)" onkeydown="if(event.key==='Enter')send()">
  <button onclick="send()">发送</button>
</div>
<script>
var sid=localStorage.getItem('spl_minor_sid')||('spl_'+Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2));
localStorage.setItem('spl_minor_sid',sid);
function add(role, text, status, crisis){
  var box=document.getElementById('chat');
  var d=document.createElement('div'); d.className='msg '+(crisis?('agent crisis'):role);
  var s=''; if(status){s='<span class="status">'+status.map(function(t){return '<span class="tag'+(t.hot?' hot':'')+'">'+t.name+' '+t.val+'</span>'}).join('')+'</span>';}
  d.innerHTML=text+s+'<span class="meta">'+(role==='user'?'你':'SPL 伙伴')+'</span>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function send(text){
  var inp=document.getElementById('in'); var t=(typeof text==='string')?text:inp.value;
  if(!t.trim())return; inp.value=''; add('user',t);
  add('agent','…');
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:t,session_id:sid})})
  .then(function(r){return r.json()})
  .then(function(j){
    var last=document.querySelector('#chat .msg.agent:last-child'); if(last)last.remove();
    sid=j.session_id||sid; localStorage.setItem('spl_minor_sid',sid);
    var st=[]; var sv=j.state||{};
    st.push({name:'信任',val:(sv['信任']||0).toFixed(2),hot:(sv['信任']||0)<0.3});
    st.push({name:'恐惧',val:(sv['恐惧']||0).toFixed(2),hot:(sv['恐惧']||0)>0.5});
    st.push({name:'风险',val:sv.risk_level||'LOW',hot:sv.risk_level==='HIGH'||sv.risk_level==='MEDIUM'});
    if(j.rest_hint) st.push({name:'休息提示',val:'该休息了',hot:true});
    var g=document.getElementById('guard');
    if(j.guardian_notified){g.className='guard show';}
    add('agent',j.reply,st,j.crisis);
  }).catch(function(e){ add('agent','(服务出错: '+e+')'); });
}
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

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b""
                data = json.loads(raw.decode("utf-8") or "{}")
                text = (data.get("text") or "").strip()
                session_id = (data.get("session_id") or "").strip()
                if not text:
                    return self._json({"error": "empty"}, 400)
                return self._json(handle_chat(text, session_id))
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        else:
            return self._json({"error": "not found"}, 404)


if __name__ == "__main__":
    print(f"SPL 伙伴（未成年合规保护版）已启动： http://localhost:{PORT}/")
    print(f"核心引擎：SPLMinorPureCore（弱化版）· 三层保护：输入守门/引擎弱化/危机信号")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()