# ================================================================
# SPL Agent · 可直接对话的演示服务端（零第三方依赖）
#   事件 → SPL Pure Core V8.0 核心引擎 → 台词风格(language style.py)
#   → 返回台词风格指令(LLM prompt) + 状态快照
#
# 运行：python "feature/spl-chat-server.py"    默认端口 8777
# 访问：http://localhost:8777/
# 说明：文件名带空格模块用 importlib 加载；仅标准库 http.server。
# ================================================================
import importlib.util
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = int(os.environ.get("SPL_CHAT_PORT", "8777"))

_spec_cache = {}
def _load(name, path):
    if name in _spec_cache:
        return _spec_cache[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _spec_cache[name] = mod
    return mod

core_mod = _load("spl_core", os.path.join(ROOT, "SPL-anthropic-engine.py"))
lang_mod = _load("lang_style", os.path.join(HERE, "language style.py"))

SPLPureCoreV7_3 = core_mod.SPLPureCoreV7_3
NarrativeMapper = core_mod.NarrativeMapper
LanguageStyleEngine = lang_mod.LanguageStyleEngine
LanguagePersonaEngine = lang_mod.LanguagePersonaEngine
LanguagePersona = lang_mod.LanguagePersona
StyleProfile = lang_mod.StyleProfile

# ── 关键词 → 事件（支持中英）──
INTENTS = [
    ("betrayal",      ["背叛","出卖","骗我","欺骗","辜负","背刺","betray","cheat","deceive"]),
    ("threat",        ["威胁","危险","害怕","攻击","打你","threat","danger","afraid"]),
    ("insult",        ["垃圾","废物","蠢","傻","讨厌","滚","stupid","idiot","hate"]),
    ("criticism",     ["批评","投诉","不好","错误","差评","wrong","bad","critic"]),
    ("promise_break", ["失约","没兑现","放鸽子","broke promise","unreliable"]),
    ("value_violation", ["撒谎","不诚实","违背","lie","dishonest"]),
    ("promise_keep",  ["承诺","保证","答应","promise","guarantee"]),
    ("achievement",   ["成功","完成","赢了","成功","success","win","done"]),
    ("compliment",    ["谢谢","感谢","你真棒","喜欢","厉害","thank","great","love","nice"]),
    ("rest",          ["休息","晚安","睡觉","rest","sleep"]),
    ("alone",         ["离开","走开","别理我","alone","leave","go away"]),
    ("long_isolation",["好久不见","冷落","孤独","long time","lonely"]),
]
INTENSITY = {"betrayal":.85,"threat":.8,"insult":.8,"criticism":.65,"promise_break":.7,
             "value_violation":.7,"promise_keep":.6,"achievement":.65,"compliment":.6,
             "rest":.5,"alone":.4,"long_isolation":.7}

def parse_intent(text):
    low = text.lower()
    for ev, words in INTENTS:
        for w in words:
            if w in low:
                return ev
    return "compliment"  # 默认温和回应

# 补全 NarrativeMapper 未覆盖的事件→内感受向量（增强演示效果，不修改主引擎）
EVENT_VECTOR = {
    "betrayal":    {"belonging": -0.6, "threat": 0.5},
    "threat":      {"threat": 0.7},
    "insult":      {"belonging": -0.4, "threat": 0.3},
    "criticism":   {"belonging": -0.3, "autonomy": -0.2},
    "promise_break":{"belonging": -0.4, "threat": 0.2},
    "value_violation":{"belonging": -0.4, "threat": 0.2},
    "promise_keep": {"belonging": 0.4},
    "achievement": {"belonging": 0.3, "autonomy": 0.3},
    "compliment":  {"belonging": 0.3, "autonomy": 0.1},
    "rest":        {"fatigue": -0.5},
    "alone":       {"belonging": -0.3},
    "long_isolation":{"belonging": -0.5},
}

def event_vector(event, intensity):
    vec = EVENT_VECTOR.get(event)
    if vec is not None:
        return {k: v * intensity for k, v in vec.items()}
    return NarrativeMapper.map_event(event, intensity)

# ── 每个"人格"独立维护一个核心引擎（状态互不干扰）──
SESSIONS = {}  # persona_mode -> {"core","persona","style","history"}

def get_session(persona_mode="direct", silence_policy=False):
    if persona_mode not in SESSIONS:
        SESSIONS[persona_mode] = {
            "core": SPLPureCoreV7_3(),
            "persona": LanguagePersona(mode=persona_mode, silence_policy=silence_policy,
                                       silence_hint="她没有回答。只是垂下眼帘，避开了目光。"),
            "style": StyleProfile(base_verbosity=0.6, formality=0.7, sarcasm_tendency=0.3),
            "history": [],
        }
    return SESSIONS[persona_mode]

def state_vars(snap):
    """把核心快照翻译成可读的中文状态标签（供前端展示）。"""
    fluid = snap.get("fluid", {})
    def fmt(k): return round(fluid.get(k, 0.0), 2)
    return {
        "喜悦": fmt("喜悦"), "愤怒": fmt("愤怒"), "恐惧": fmt("恐惧"),
        "信任": fmt("信任"), "疏离": fmt("疏离"), "张力": fmt("张力"),
        "愧疚": fmt("愧疚"), "羞耻": fmt("羞耻"),
        "energy": round(snap.get("energy", 0), 1),
        "denial": round(snap.get("denial_load", 0), 2),
        "trauma": round((snap.get("trauma") or {}).get("charge", 0.0) if isinstance(snap.get("trauma"), dict) else 0.0, 2),
    }

def handle_chat(user_text, persona_mode="direct", silence_policy=False):
    sess = get_session(persona_mode, silence_policy)
    core = sess["core"]
    persona = sess["persona"]
    style = sess["style"]

    # 关键词 → 事件
    event = parse_intent(user_text)
    intensity = INTENSITY.get(event, 0.5)

    # 事件 → 内感受向量 → 核心引擎
    vec = event_vector(event, intensity)
    core.process_vector(vec, intensity, event_id=event)
    snap = core.snapshot()

    # 台词风格渲染
    pe = LanguagePersonaEngine(persona, style)
    expression = pe.filter_expression(snap)
    rendered = LanguageStyleEngine(style).render_style(snap, expression=expression)

    sess["history"].append({"role": "user", "text": user_text, "event": event})

    return {
        "reply": rendered.silence_hint if (expression.should_silence and rendered.silence_hint) else rendered.prompt_injection,
        "event": event,
        "expression_mode": expression.expression_mode,
        "should_silence": expression.should_silence,
        "state": state_vars(snap),
        "prompt": rendered.prompt_injection,
        "history_len": len(sess["history"]),
    }

# ── 静态页面 ──
PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPL Agent · 直接对话演示</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Segoe UI",sans-serif;background:#0f172a;color:#f1f5f9;line-height:1.6;height:100vh;display:flex;flex-direction:column}
header{padding:14px 24px;background:#1e293b;border-bottom:1px solid #334155;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:16px;font-weight:600;color:#2dd4bf}
header .sub{font-size:12px;color:#94a3b8}
header select{background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:6px 10px;font-size:12px}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:72%;padding:10px 15px;border-radius:14px;font-size:14px;white-space:pre-wrap;word-break:break-word}
.msg.user{align-self:flex-end;background:#0d9488;color:#fff;border-bottom-right-radius:4px}
.msg.agent{align-self:flex-start;background:#1e293b;border:1px solid #334155;border-bottom-left-radius:4px}
.msg .meta{display:block;font-size:11px;color:#94a3b8;margin-top:6px}
.status{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.status .tag{font-size:11px;padding:2px 9px;border-radius:100px;background:#134e4a;color:#2dd4bf}
.status .tag.hot{background:#7f1d1d;color:#fca5a5}
.inputrow{display:flex;gap:10px;padding:14px 20px;background:#1e293b;border-top:1px solid #334155}
#in{flex:1;padding:12px 16px;border-radius:100px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:14px;outline:none}
#in:focus{border-color:#0d9488}
button{padding:12px 24px;border:none;border-radius:100px;background:#0d9488;color:#fff;font-size:14px;cursor:pointer}
button:hover{background:#0f766e}
.sugg{display:flex;gap:8px;padding:8px 20px;flex-wrap:wrap;background:#1e293b}
.sugg button{background:transparent;border:1px solid #334155;color:#94a3b8;padding:6px 13px;font-size:12px}
.sugg button:hover{color:#2dd4bf;border-color:#0d9488}
</style></head><body>
<header>
  <div><h1>⚡ SPL Agent · 直接对话</h1><div class="sub">Python 核心引擎 + 语言风格模块 · 确定性人格</div></div>
  <label class="sub">人格 <select id="persona">
    <option value="direct">坦率直接</option>
    <option value="restrained">克制冷峻</option>
    <option value="intimate">松弛亲昵</option>
    <option value="confrontational">锋锐直白</option>
    <option value="evasive">闪躲回避</option>
  </select></label>
</header>
<div class="sugg">
  <button onclick="send('你好，很高兴认识你！')">👋 打招呼</button>
  <button onclick="send('你真好，谢谢你帮我。')">🌟 夸奖</button>
  <button onclick="send('你太让我失望了。')">😞 打击</button>
  <button onclick="send('我保证，一定兑现承诺。')">🤝 承诺</button>
  <button onclick="send('你背叛了我。')">💔 背叛</button>
  <button onclick="send('今晚早点休息吧。')">🌙 休息</button>
</div>
<div id="chat"></div>
<div class="inputrow">
  <input id="in" placeholder="输入想说的话，回车发送…" onkeydown="if(event.key==='Enter')send()">
  <button onclick="send()">发送</button>
</div>
<script>
function add(role, text, status){
  var box=document.getElementById('chat');
  var d=document.createElement('div'); d.className='msg '+role;
  var s=''; if(status){s='<span class="status">'+status.map(function(t){return '<span class="tag'+(t.hot?' hot':'')+'">'+t.name+' '+t.val+'</span>'}).join('')+'</span>';}
  d.innerHTML=text+s+'<span class="meta">'+(role==='user'?'你':'SPL Agent')+'</span>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function send(text){
  var inp=document.getElementById('in'); var t=(typeof text==='string')?text:inp.value;
  if(!t.trim())return; inp.value=''; add('user',t);
  var persona=document.getElementById('persona').value;
  add('agent','…');
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:t,persona:persona})})
  .then(function(r){return r.json()})
  .then(function(j){
    var last=document.querySelector('#chat .msg.agent:last-child'); if(last)last.remove();
    var st=[]; var sv=j.state;
    st.push({name:'信任',val:sv['信任'].toFixed(2),hot:sv['信任']<0.35});
    st.push({name:'恐惧',val:sv['恐惧'].toFixed(2),hot:sv['恐惧']>0.5});
    st.push({name:'愤怒',val:sv['愤怒'].toFixed(2),hot:sv['愤怒']>0.5});
    st.push({name:'羞耻',val:sv['羞耻'].toFixed(2),hot:sv['羞耻']>0.5});
    st.push({name:'张力',val:sv['张力'].toFixed(2),hot:sv['张力']>0.5});
    st.push({name:'创伤',val:sv['trauma'].toFixed(2),hot:sv['trauma']>0.3});
    st.push({name:'能量',val:sv['energy'],hot:sv['energy']<30});
    add('agent', j.should_silence?('['+j.expression_mode+' · 沉默] '+j.reply):j.reply, st);
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
                raw = self.rfile.read(length).decode("utf-8")
                data = json.loads(raw or "{}")
                text = (data.get("text") or "").strip()
                persona = data.get("persona") or "direct"
                if not text:
                    return self._json({"error": "empty"}, 400)
                result = handle_chat(text, persona_mode=persona, silence_policy=(persona == "restrained"))
                return self._json(result)
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        else:
            return self._json({"error": "not found"}, 404)

if __name__ == "__main__":
    print(f"SPL Agent 对话演示服务已启动： http://localhost:{PORT}/")
    print(f"核心引擎：SPLPureCoreV7_3 · 台词模块：language style.py")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
