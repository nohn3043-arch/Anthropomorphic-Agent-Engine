/**
 * SPL Pure Core V8.0 — Causal Logic Psychological Fluid Engine
 * Translated from the second-person causal logic reasoning engine specification.
 */

export interface PsychologicalVector {
  threat?: number;
  belonging?: number;
  autonomy?: number;
  fatigue?: number;
  shame_trigger?: number;
  [key: string]: number | undefined;
}

export interface ExpectedEvent {
  valence: number;
  confidence: number;
  time: number;
  age: number;
}

export interface MemoryTrace {
  vector: Record<string, number>;
  strength: number;
  valence: number;
  timestamp: number;
  age: number;
  count: number;
}

export class NarrativeMapper {
  static mapEvent(event: string, intensity: number): PsychologicalVector {
    switch (event) {
      case "compliment": // 夸奖
        return { belonging: 0.3 * intensity, autonomy: 0.1 * intensity };
      case "insult": // 侮辱
        return { belonging: -0.4 * intensity, threat: 0.3 * intensity };
      case "betrayal": // 背叛
        return { belonging: -0.6 * intensity, threat: 0.5 * intensity };
      case "alone": // 独处/冷暴力
        return { belonging: -0.3 * intensity };
      case "rest": // 休息
        return { fatigue: -0.5 * intensity };
      default:
        return { belonging: 0.0, threat: 0.0 };
    }
  }
}

export class SPLEngine {
  // ---------- 基础生理/心理参数 ----------
  psychological_resilience = 0.5; // 心理韧性 [0,1]
  energy = 100.0;                 // 生理能量 [0,100]
  affinity = 0.5;                 // 对外亲和基线
  last_time = Date.now() / 1000;  // 记录秒级时间戳
  _clock_override: number | null = null; // 虚拟时钟覆盖

  // ---------- 8 维情绪流体（连续状态） ----------
  fluid: Record<string, number> = {
    "喜悦": 0.0, "愤怒": 0.0, "恐惧": 0.0,
    "信任": 0.5, "疏离": 0.2, "张力": 0.2,
    "愧疚": 0.0, "羞耻": 0.0
  };
  fluid_target: Record<string, number> = {
    "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
    "信任": 0.5, "疏离": 0.2, "张力": 0.2,
    "愧疚": 0.0, "羞耻": 0.0
  };
  fluid_baseline: Record<string, number> = {
    "喜悦": 0.2, "愤怒": 0.0, "恐惧": 0.1,
    "信任": 0.5, "疏离": 0.2, "张力": 0.2,
    "愧疚": 0.0, "羞耻": 0.0
  };

  // ---------- V8.0 心境层（慢变量背景情绪） ----------
  mood: Record<string, number> = {
    "愉悦": 0.5,  // pleasantness
    "紧张": 0.3,  // tension
    "精力": 0.7,  // vigor
  };
  MOOD_INERTIA = 0.0003; // 心境变化极慢

  // ---------- V8.0 睡眠系统 ----------
  sleep_debt = 0.0; // 睡眠债 [0,1]
  SLEEP_NEED_RATE = 1.0 / 57600; // 每秒累积
  SLEEP_RECOVER_RATE = 0.25;    // 每小时恢复速率
  DREAM_EMOTION_DECAY = 0.15;
  DREAM_FEAR_EXTINCTION = 0.08;
  DREAM_TRAUMA_HEAL_BOOST = 3.0;
  last_sleep_time = 0.0;

  // ---------- V8.0 自尊系统 ----------
  self_esteem = 0.5; // 自尊 [0,1]
  SELF_ESTEEM_INERTIA = 0.002;
  SELF_ESTEEM_UPDATE_RATE = 0.03;

  // ---------- V8.0 预期系统 ----------
  expected_events: Record<string, ExpectedEvent> = {};
  EXPECTATION_DECAY = 0.0001;
  SURPRISE_POSITIVE_BOOST = 0.4;
  SURPRISE_NEGATIVE_BOOST = 0.5;

  // ---------- V8.0 认知失调 ----------
  cognitive_dissonance = 0.0; // 认知失调水平 [0,1]
  DISSONANCE_THRESHOLD = 0.4;
  DISSONANCE_DECAY = 0.005;

  // ---------- V8.0 扩展防御机制 ----------
  denial_load = 0.0;
  DENIAL_THRESHOLD = 1.2;
  DENIAL_DRAIN = 0.015;
  DENIAL_BURST_COOLDOWN = 40.0;
  denial_burst_cd = 0.0;
  rationalization_load = 0.0;
  RATIONALIZE_DRAIN = 0.03;

  // ---------- 创伤节点（离散 SPL 节点） ----------
  trauma_state: Record<string, number> = {};
  TRAUMA_HEAL_RATE = 0.003;
  TRAUMA_BIAS = 0.35;

  // ---------- 记忆痕迹 + 艾宾浩斯遗忘曲线 ----------
  memory_traces: MemoryTrace[] = [];
  MAX_MEMORY_TRACES = 64;
  forgetting_rate = 0.01;
  trace_importance_threshold = 0.05;
  RECONSOL_RADIUS = 0.4;
  SAFETY_THRESHOLD = 0.3;

  // ---------- 压抑-反弹 ----------
  suppression_load = 0.0;
  SUPPRESSION_THRESHOLD = 1.5;
  SUPPRESSION_DRAIN = 0.02;
  SUPPRESSION_BURST_COOLDOWN = 30.0;
  suppression_burst_cd = 0.0;
  _suppressing_negativity = false;

  // ---------- 隐压雪崩 ----------
  latent_pressure = 0.0;
  LATENT_THRESHOLD = 2.0;
  LATENT_DRAIN = 0.01;
  LATENT_COOLDOWN = 60.0;
  avalanche_cd = 0.0;

  // ---------- 信任容量腐蚀 ----------
  max_trust = 1.0;
  TRUST_ERODE = 0.92;
  TRUST_RECOVER = 0.0005;

  // ---------- 粘滞度 / 心理时间 ----------
  dynamic_viscosity = 0.1;
  VISC_BASE = 0.1;
  VISC_TENSION_K = 0.3;
  VISC_FATIGUE_K = 0.2;
  psy_dilation = 1.0;
  time_compress_base = 0.0;

  // ---------- 兴奋/唤醒（元参数） ----------
  excitation = 0.3;
  EXCITATION_BASELINE = 0.3;
  EXCITATION_NOVELTY_GAIN = 0.12;
  EXCITATION_SALIENCE_BOOST = 0.35;
  EXCITATION_DECAY = 0.025;
  EXCITATION_BOREDOM_THRESHOLD = 0.1;
  EXCITATION_MAX = 1.0;

  // ---------- 能量 / 疲劳 ----------
  ENERGY_RECOVER = 1.5;
  ENERGY_EVENT_COST = 1.5;
  ENERGY_MIN = 0.0;
  ENERGY_MAX = 100.0;
  fatigue = 0.0;
  FATIGUE_RECOVER = 0.05;

  last_perceived: Record<string, number> = {};

  // ---------- 最近爆发历史，用于UI反馈 ----------
  burst_events: Array<{ type: string; timestamp: number; detail: string }> = [];

  constructor() {
    this.last_time = this._now();
  }

  // ==================================================================
  // 时钟：支持虚拟时间注入
  // ==================================================================
  _now(): number {
    if (this._clock_override !== null) {
      return this._clock_override;
    }
    return Date.now() / 1000;
  }

  setClock(t: number | null) {
    this._clock_override = t;
  }

  advanceClock(dt: number) {
    if (this._clock_override === null) {
      this._clock_override = Date.now() / 1000;
    }
    this._clock_override += dt;
  }

  // ==================================================================
  // 公共入口 1：事件驱动
  // ==================================================================
  processVector(vector: PsychologicalVector, raw_intensity = 1.0, event_id = "") {
    this._advanceTime();

    // V8.0: 预期匹配——在认知增益之前计算 surprise
    let surprise = 0.0;
    if (event_id && this.expected_events[event_id]) {
      surprise = this._computeSurprise(event_id, vector, raw_intensity);
    }

    // 兴奋先于认知增益更新
    this._excitationOnEvent(vector, raw_intensity);

    const perceived = this._coreAppraisalGain(vector);

    // V8.0: surprise 调制 perceived vector
    let modifiedPerceived = { ...perceived };
    if (surprise !== 0.0) {
      modifiedPerceived = this._applySurprise(perceived, surprise);
    }

    this.last_perceived = { ...modifiedPerceived };

    const threat = modifiedPerceived.threat || 0.0;
    const belonging = modifiedPerceived.belonging || 0.0;

    if (Math.abs(threat) > 0.2 || Math.abs(belonging) > 0.3) {
      this._memoryReconsolidation(modifiedPerceived);
    }

    const threat_thr = 0.4 * (1.0 - this.psychological_resilience);
    if (threat > threat_thr) {
      this._applyTrauma("threat", threat - threat_thr);
    }
    if (belonging < -0.4 && threat > 0.3) {
      this._applyTrauma("betrayal", Math.abs(belonging) * threat);
    }

    if (belonging < -0.3) {
      this._erodeTrust(Math.abs(belonging));
    }

    this._latentAccumulate(modifiedPerceived);
    this._vectorToFluid(modifiedPerceived);

    // V8.0: 自尊更新
    this._updateSelfEsteem(modifiedPerceived);

    // V8.0: 认知失调处理
    this._dissonanceDynamics(modifiedPerceived);

    // V8.0: 扩展防御（先否认→再合理化→最后压抑）
    this._defenseHierarchy(modifiedPerceived);

    // 心境更新
    this._updateMood();

    this._updateDynamicViscosity();
    this._fluidDynamics(this._psychologicalDtFor(0.8));

    this._fluidToSystemFeedback();
    this._energyOnEvent(modifiedPerceived, raw_intensity);

    this.fatigue = Math.max(0.0, Math.min(1.0, this.fatigue + (modifiedPerceived.fatigue || 0.0) * 0.5));
    this.time_compress_base = Math.max(0.0, this.time_compress_base * 0.95);

    this.last_time = this._now();
  }

  // ==================================================================
  // 公共入口 2：空转 / 独处时间
  // ==================================================================
  idle(seconds: number) {
    if (seconds <= 0) return;
    if (this._clock_override !== null) {
      this._clock_override += seconds;
    } else {
      this.last_time -= seconds;
    }
    this._advanceTime();
  }

  processEvent(event: string, intensity = 1.0) {
    this.processVector(NarrativeMapper.mapEvent(event, intensity), intensity, event);
  }

  // ==================================================================
  // V8.0 公共入口 3：睡眠
  // ==================================================================
  sleep(hours: number) {
    if (hours <= 0) return;
    const seconds = hours * 3600.0;

    if (this._clock_override !== null) {
      this._clock_override += seconds;
    } else {
      this.last_time -= seconds;
    }

    // 先结算睡眠前的连续过程
    this._advanceTime();

    // 梦境情绪加工
    const dream_cycles = Math.max(1, Math.floor(hours * 1.5));
    for (let i = 0; i < dream_cycles; i++) {
      this._dreamProcess();
    }

    // 睡眠债清除
    this.sleep_debt = Math.max(0.0, this.sleep_debt - this.SLEEP_RECOVER_RATE * hours);
    this.last_sleep_time = this._now();

    // 心境重置
    this.mood["愉悦"] = Math.min(0.9, this.mood["愉悦"] + 0.15 * hours);
    this.mood["紧张"] = Math.max(0.05, this.mood["紧张"] - 0.12 * hours);
    this.mood["精力"] = Math.min(1.0, this.mood["精力"] + 0.2 * hours);

    // 能量完全恢复
    this.energy = this.ENERGY_MAX;
    this.fatigue = Math.max(0.0, this.fatigue - 0.5 * hours);

    // 创伤加速愈合
    this._healTraumas(seconds * this.DREAM_TRAUMA_HEAL_BOOST);

    this._updateMood();
    this._updateDynamicViscosity();
  }

  // ==================================================================
  // V8.0 公共入口 4：设定预期
  // ==================================================================
  expect(event_id: string, valence: number, confidence = 0.5) {
    this.expected_events[event_id] = {
      valence: Math.max(-1.0, Math.min(1.0, valence)),
      confidence: Math.max(0.0, Math.min(1.0, confidence)),
      time: this._now(),
      age: 0.0,
    };
  }

  // ==================================================================
  // V8.0 公共入口 5：触发认知失调
  // ==================================================================
  induceDissonance(magnitude: number) {
    this.cognitive_dissonance = Math.min(1.0, this.cognitive_dissonance + magnitude);
    this.fluid["张力"] = Math.min(1.0, this.fluid["张力"] + magnitude * 0.4);
    this.fluid["愧疚"] = Math.min(1.0, this.fluid["愧疚"] + magnitude * 0.3);
    this.energy = Math.max(this.ENERGY_MIN, this.energy - magnitude * 5.0);
  }

  // ==================================================================
  // 连续时间物理模拟
  // ==================================================================
  _advanceTime() {
    const now = this._now();
    let dt = now - this.last_time;
    if (dt <= 0) {
      this.last_time = now;
      return;
    }
    dt = Math.min(dt, 86400.0); // 最大24小时一步

    // 积累睡眠债
    this.sleep_debt = Math.min(1.0, this.sleep_debt + this.SLEEP_NEED_RATE * dt);

    // 预期衰减
    this._decayExpectations(dt);

    this._rebuildFluidTarget();
    this._updateDynamicViscosity();
    this._fluidDynamics(this._psychologicalDtFor(dt));
    this._forgetOver(dt);
    this._energyIdle(dt);
    this._excitationDecay(dt);
    this._checkBoredom(dt);

    this.suppression_load = Math.max(0.0, this.suppression_load - this.SUPPRESSION_DRAIN * dt);
    this.latent_pressure = Math.max(0.0, this.latent_pressure - this.LATENT_DRAIN * dt);
    this.denial_load = Math.max(0.0, this.denial_load - this.DENIAL_DRAIN * dt);
    this.rationalization_load = Math.max(0.0, this.rationalization_load - this.RATIONALIZE_DRAIN * dt);
    this.cognitive_dissonance = Math.max(0.0, this.cognitive_dissonance - this.DISSONANCE_DECAY * dt);

    this._healTraumas(dt);
    this._recoverTrust(dt);

    this.suppression_burst_cd = Math.max(0.0, this.suppression_burst_cd - dt);
    this.avalanche_cd = Math.max(0.0, this.avalanche_cd - dt);
    this.denial_burst_cd = Math.max(0.0, this.denial_burst_cd - dt);

    this.time_compress_base *= Math.pow(0.95, Math.max(0.0, Math.min(dt, 10.0)));
    if (this.time_compress_base < 1e-4) {
      this.time_compress_base = 0.0;
    }

    this._fluidToSystemFeedback();
    this.fatigue = Math.max(0.0, this.fatigue - this.FATIGUE_RECOVER * dt);
    this._updateMood();

    this.last_time = now;
  }

  // ==================================================================
  // 1. 认知增益与调制
  // ==================================================================
  _coreAppraisalGain(v: PsychologicalVector): Record<string, number> {
    const out: Record<string, number> = {};
    const energy_factor = this.energy / 100.0;
    const tension = this.fluid["张力"] || 0;
    const fear = this.fluid["恐惧"] || 0;
    const trust = Math.min(this.fluid["信任"] || 0, this.max_trust);

    const arousal_mult = 1.0 + this.excitation * 0.6;
    const mood_pleasantness = this.mood["愉悦"] || 0.5;
    const mood_mod = 1.0 + (mood_pleasantness - 0.5) * 0.5;

    const esteem_threat_mod = 1.0 + (0.5 - this.self_esteem) * 0.8;
    const esteem_belonging_pos_mod = 0.6 + this.self_esteem * 0.8;

    const sleep_mod_neg = 1.0 + this.sleep_debt * 0.5;
    const sleep_mod_pos = 1.0 - this.sleep_debt * 0.3;

    for (const k of Object.keys(v)) {
      const val = v[k];
      if (typeof val === "number") {
        const base_mod = (0.4 + 0.6 * energy_factor) * arousal_mult * mood_mod;
        out[k] = val * base_mod;
      }
    }

    if (out.threat && out.threat > 0) {
      out.threat *= (1.0 + 1.5 * tension * fear) * esteem_threat_mod * sleep_mod_neg;
    }
    if (this.trauma_state["threat"] && out.threat && out.threat > 0) {
      out.threat *= 1.0 + this.trauma_state["threat"];
    }
    if (this.trauma_state["betrayal"] && out.belonging && out.belonging < 0) {
      out.belonging *= 1.0 + this.trauma_state["betrayal"];
    }
    if (out.belonging && out.belonging < 0) {
      out.belonging *= (1.0 - 0.4 * trust) * sleep_mod_neg;
    }
    if (out.belonging && out.belonging > 0) {
      out.belonging *= (1.0 - 0.3 * this.fatigue) * esteem_belonging_pos_mod * sleep_mod_pos;
    }

    return out;
  }

  // ==================================================================
  // 2. 记忆重巩固
  // ==================================================================
  _vecSim(a: Record<string, number>, b: Record<string, number>): number {
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
    if (keys.size === 0) return 0.0;
    let dot = 0.0;
    let na = 0.0;
    let nb = 0.0;
    for (const k of keys) {
      const va = a[k] || 0.0;
      const vb = b[k] || 0.0;
      dot += va * vb;
      na += va * va;
      nb += vb * vb;
    }
    if (na === 0 || nb === 0) return 0.0;
    return dot / (Math.sqrt(na) * Math.sqrt(nb));
  }

  _memoryReconsolidation(v: Record<string, number>) {
    const valence = (v.belonging || 0.0) - (v.threat || 0.0);
    const intensity = Math.sqrt(Object.values(v).reduce((acc, val) => acc + val * val, 0));
    const trust = Math.min(this.fluid["信任"] || 0, this.max_trust);
    const fear = this.fluid["恐惧"] || 0;
    const safety = trust * (1.0 - fear);

    let best_idx = -1;
    let best_sim = 0.0;
    for (let i = 0; i < this.memory_traces.length; i++) {
      const sim = this._vecSim(v, this.memory_traces[i].vector);
      if (sim > best_sim) {
        best_sim = sim;
        best_idx = i;
      }
    }

    const now = this._now();
    if (best_idx >= 0 && best_sim > (1.0 - this.RECONSOL_RADIUS)) {
      const tr = this.memory_traces[best_idx];
      if (safety > this.SAFETY_THRESHOLD) {
        tr.strength *= 0.85;
      } else {
        tr.strength = Math.min(1.0, tr.strength + intensity * 0.2);
      }
      tr.timestamp = now;
      tr.age = 0.0;
      tr.count += 1;
    } else {
      const trace: MemoryTrace = {
        vector: { ...v },
        strength: Math.min(1.0, intensity),
        valence,
        timestamp: now,
        age: 0.0,
        count: 1,
      };
      this.memory_traces.push(trace);
      if (this.memory_traces.length > this.MAX_MEMORY_TRACES) {
        this.memory_traces.sort((a, b) => {
          const scoreA = a.strength * (1.0 + Math.log1p(a.count));
          const scoreB = b.strength * (1.0 + Math.log1p(b.count));
          return scoreA - scoreB;
        });
        this.memory_traces.shift();
      }
    }
  }

  // ==================================================================
  // 3. 创伤
  // ==================================================================
  _applyTrauma(key: string, magnitude: number) {
    const cur = this.trauma_state[key] || 0.0;
    const gain = magnitude * (1.0 - this.psychological_resilience) * 0.7;
    this.trauma_state[key] = Math.min(1.0, cur + gain);
  }

  _healTraumas(dt: number) {
    const rate = this.TRAUMA_HEAL_RATE * (0.3 + this.psychological_resilience) * dt;
    const healed: string[] = [];
    for (const k of Object.keys(this.trauma_state)) {
      const nv = this.trauma_state[k] - rate;
      if (nv <= 0.01) {
        healed.push(k);
      } else {
        this.trauma_state[k] = nv;
      }
    }
    for (const k of healed) {
      delete this.trauma_state[k];
    }
  }

  // ==================================================================
  // 4. 信任容量腐蚀 & 恢复
  // ==================================================================
  _erodeTrust(magnitude: number) {
    const factor = 1.0 - (1.0 - this.TRUST_ERODE) * Math.min(1.0, magnitude);
    this.max_trust = Math.max(0.1, this.max_trust * factor);
  }

  _recoverTrust(dt: number) {
    if (this.max_trust < 1.0) {
      const recover = this.TRUST_RECOVER * dt * (1.01 - this.max_trust);
      this.max_trust = Math.min(1.0, this.max_trust + recover);
    }
  }

  // ==================================================================
  // 5. 隐压累积 + 雪崩
  // ==================================================================
  _latentAccumulate(v: Record<string, number>) {
    const neg = Math.max(0.0, -(v.belonging || 0.0)) + Math.max(0.0, v.threat || 0.0);
    this.latent_pressure += neg * 0.4;
    if (this.latent_pressure >= this.LATENT_THRESHOLD && this.avalanche_cd <= 0) {
      this._triggerAvalanche();
    }
  }

  _triggerAvalanche() {
    this.avalanche_cd = this.LATENT_COOLDOWN;
    const overflow = this.latent_pressure - this.LATENT_THRESHOLD + 0.5;
    this.latent_pressure = 0.3;

    this.fluid["愤怒"] = Math.min(1.0, (this.fluid["愤怒"] || 0) + overflow * 0.5);
    this.fluid["恐惧"] = Math.min(1.0, (this.fluid["恐惧"] || 0) + overflow * 0.3);
    this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + overflow * 0.3);
    this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + overflow * 0.2);
    this.fluid["信任"] = Math.max(0.0, (this.fluid["信任"] || 0) - overflow * 0.3);
    this.fluid["喜悦"] = Math.max(0.0, (this.fluid["喜悦"] || 0) - overflow * 0.3);

    this.energy = Math.max(this.ENERGY_MIN, this.energy - overflow * 10);
    this.time_compress_base = Math.min(1.0, this.time_compress_base + 0.5);

    this.burst_events.push({
      type: "avalanche",
      timestamp: this._now(),
      detail: `隐压雪崩爆发！溢出压力 ${overflow.toFixed(2)}。压制崩溃，愤怒与张力飙升。`
    });
  }

  // ==================================================================
  // 6. 向量 → 流体瞬时映射
  // ==================================================================
  _vectorToFluid(v: Record<string, number>) {
    const b = v.belonging || 0.0;
    const t = v.threat || 0.0;
    const a = v.autonomy || 0.0;
    const f = v.fatigue || 0.0;
    const s = v.shame_trigger || 0.0;

    // ── V8.0 羞耻路径 ──
    if (s > 0) {
      this.fluid["羞耻"] = Math.min(1.0, (this.fluid["羞耻"] || 0) + s * 0.7);
      this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + s * 0.3);
      this.fluid["愤怒"] = Math.max(0.0, (this.fluid["愤怒"] || 0) - s * 0.3);
      this.fluid["恐惧"] = Math.min(1.0, (this.fluid["恐惧"] || 0) + s * 0.25);
    } else if (b < -0.3 && this.self_esteem < 0.35) {
      const shame_leak = (-b) * 0.3 * (0.5 - this.self_esteem);
      this.fluid["羞耻"] = Math.min(1.0, (this.fluid["羞耻"] || 0) + shame_leak);
      this.fluid["愤怒"] = Math.min(1.0, (this.fluid["愤怒"] || 0) + (-b) * 0.4);
      this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + (-b) * 0.5);
      this.fluid["愧疚"] = Math.min(1.0, (this.fluid["愧疚"] || 0) + (-b) * 0.2);
    } else if (b < 0) {
      this.fluid["愤怒"] = Math.min(1.0, (this.fluid["愤怒"] || 0) + (-b) * 0.7);
      this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + (-b) * 0.4);
      this.fluid["愧疚"] = Math.min(1.0, (this.fluid["愧疚"] || 0) + (-b) * 0.15);
      if (this.psychological_resilience > 0.6) {
        this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + (-b) * 0.3);
        this.fluid["愤怒"] *= 0.8;
      }
    }

    if (b > 0) {
      this.fluid["喜悦"] = Math.min(1.0, (this.fluid["喜悦"] || 0) + b * 0.6);
      this.fluid["信任"] = Math.min(this.max_trust, (this.fluid["信任"] || 0) + b * 0.25);
      this.fluid["愤怒"] = Math.max(0.0, (this.fluid["愤怒"] || 0) - b * 0.4);
      this.fluid["疏离"] = Math.max(0.0, (this.fluid["疏离"] || 0) - b * 0.3);
      this.fluid["羞耻"] = Math.max(0.0, (this.fluid["羞耻"] || 0) - b * 0.3);
    }

    if (t > 0) {
      this.fluid["恐惧"] = Math.min(1.0, (this.fluid["恐惧"] || 0) + t * 0.8);
      this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + t * 0.6);
      this.fluid["信任"] = Math.max(0.0, (this.fluid["信任"] || 0) - t * 0.2);
    }

    if (a > 0) {
      this.fluid["喜悦"] = Math.min(1.0, (this.fluid["喜悦"] || 0) + a * 0.3);
    }

    if (f > 0) {
      this.fluid["喜悦"] = Math.max(0.0, (this.fluid["喜悦"] || 0) - f * 0.3);
      this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + f * 0.2);
    }

    this.fluid["信任"] = Math.min(this.fluid["信任"] || 0, this.max_trust);

    for (const k of Object.keys(this.fluid)) {
      this.fluid[k] = Math.max(0.0, Math.min(1.0, this.fluid[k]));
    }

    // 兴奋调制
    if (this.excitation > 0.5) {
      const extra = (this.excitation - 0.5) * 0.4;
      this.fluid["喜悦"] = Math.min(1.0, (this.fluid["喜悦"] || 0) + extra * Math.max(0.0, b));
      this.fluid["愤怒"] = Math.min(1.0, (this.fluid["愤怒"] || 0) + extra * Math.max(0.0, -b));
      this.fluid["恐惧"] = Math.min(1.0, (this.fluid["恐惧"] || 0) + extra * Math.max(0.0, t));
      this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + extra * Math.max(0.0, t, -b) * 0.5);
    }
  }

  // ==================================================================
  // 7. 压抑动力学
  // ==================================================================
  _suppressionDynamics(v: Record<string, number>) {
    const neg = (this.fluid["愤怒"] || 0) + (this.fluid["恐惧"] || 0) + (this.fluid["疏离"] || 0);
    const will_to_suppress = (this.energy / 100.0) * (0.3 + this.psychological_resilience);
    const suppressed_here = neg * will_to_suppress * 0.5;

    if (suppressed_here > 0.05) {
      this._suppressing_negativity = true;
      this.suppression_load += suppressed_here;
      this.fluid["愤怒"] *= (1.0 - will_to_suppress * 0.6);
      this.fluid["恐惧"] *= (1.0 - will_to_suppress * 0.4);
      this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + suppressed_here * 0.3);
    } else {
      this._suppressing_negativity = false;
    }

    if (this.suppression_load >= this.SUPPRESSION_THRESHOLD && this.suppression_burst_cd <= 0) {
      this._triggerBurst();
    }
  }

  _triggerBurst() {
    this.suppression_burst_cd = this.SUPPRESSION_BURST_COOLDOWN;
    const load = this.suppression_load;
    this.suppression_load = 0.0;

    this.fluid["愤怒"] = Math.min(1.0, (this.fluid["愤怒"] || 0) + load * 0.6);
    this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + load * 0.4);
    this.fluid["喜悦"] = Math.max(0.0, (this.fluid["喜悦"] || 0) - load * 0.3);
    this.fluid["信任"] = Math.max(0.0, (this.fluid["信任"] || 0) - load * 0.2);

    this.energy = Math.max(this.ENERGY_MIN, this.energy - load * 8);
    this.time_compress_base = Math.min(1.0, this.time_compress_base + 0.7);
    this._applyTrauma("threat", load * 0.1);

    this.burst_events.push({
      type: "suppression",
      timestamp: this._now(),
      detail: `压抑反弹爆发！压抑负荷 ${load.toFixed(2)}。累积痛苦倾泻而出，极度愤怒。`
    });
  }

  // ==================================================================
  // 8. 动态粘滞度与心理时间
  // ==================================================================
  _updateDynamicViscosity() {
    const base = this.VISC_BASE;
    this.dynamic_viscosity = base
      + this.VISC_TENSION_K * (this.fluid["张力"] || 0)
      + this.VISC_FATIGUE_K * this.fatigue
      + (this.mood["紧张"] || 0) * 0.15
      + this.sleep_debt * 0.1;

    this.dynamic_viscosity -= this.excitation * 0.08;
    this.dynamic_viscosity = Math.max(0.02, Math.min(1.5, this.dynamic_viscosity));
    this.psy_dilation = 1.0 + this.time_compress_base * 2.0;
  }

  _psychologicalDtFor(real_dt: number): number {
    return real_dt * this.psy_dilation / (0.1 + this.dynamic_viscosity);
  }

  _fluidDynamics(dt: number) {
    const k = 1.0 / (0.2 + this.dynamic_viscosity * 3.0);
    let alpha = 1.0 - Math.exp(-k * Math.max(0.0, dt));
    alpha = Math.max(0.0, Math.min(1.0, alpha));

    for (const key of Object.keys(this.fluid)) {
      let tgt = this.fluid_target[key];
      if (tgt === undefined) {
        tgt = this.fluid[key];
      }
      if (key === "信任") {
        tgt = Math.min(tgt, this.max_trust);
      }
      this.fluid[key] += (tgt - this.fluid[key]) * alpha;
      this.fluid[key] = Math.max(0.0, Math.min(1.0, this.fluid[key]));
    }
  }

  // ==================================================================
  // target 重建
  // ==================================================================
  _rebuildFluidTarget() {
    for (const k of Object.keys(this.fluid_baseline)) {
      this.fluid_target[k] = this.fluid_baseline[k];
    }

    const mp = this.mood["愉悦"] || 0.5;
    this.fluid_target["喜悦"] = Math.min(1.0, this.fluid_target["喜悦"] + (mp - 0.5) * 0.3);
    this.fluid_target["愤怒"] = Math.max(0.0, this.fluid_target["愤怒"] - (mp - 0.5) * 0.15);
    this.fluid_target["疏离"] = Math.max(0.0, this.fluid_target["疏离"] - (mp - 0.5) * 0.15);

    this.fluid_target["羞耻"] = Math.max(0.0, this.fluid_target["羞耻"] + (0.5 - this.self_esteem) * 0.2);

    const sd = this.sleep_debt;
    this.fluid_target["张力"] = Math.min(1.0, this.fluid_target["张力"] + sd * 0.25);
    this.fluid_target["恐惧"] = Math.min(1.0, this.fluid_target["恐惧"] + sd * 0.15);
    this.fluid_target["喜悦"] = Math.max(0.0, this.fluid_target["喜悦"] - sd * 0.2);

    if (this.trauma_state["threat"]) {
      const w = this.trauma_state["threat"] * this.TRAUMA_BIAS;
      this.fluid_target["恐惧"] = Math.min(1.0, this.fluid_target["恐惧"] + w);
      this.fluid_target["张力"] = Math.min(1.0, this.fluid_target["张力"] + w * 0.8);
      this.fluid_target["信任"] = Math.max(0.0, this.fluid_target["信任"] - w * 0.5);
    }
    if (this.trauma_state["betrayal"]) {
      const w = this.trauma_state["betrayal"] * this.TRAUMA_BIAS;
      this.fluid_target["疏离"] = Math.min(1.0, this.fluid_target["疏离"] + w);
      this.fluid_target["信任"] = Math.max(0.0, this.fluid_target["信任"] - w * 0.7);
      this.fluid_target["愤怒"] = Math.min(1.0, this.fluid_target["愤怒"] + w * 0.3);
    }

    // 记忆共振
    const now = this._now();
    for (const tr of this.memory_traces) {
      const age = now - tr.timestamp;
      const weight = tr.strength * Math.exp(-this.forgetting_rate * age / 20.0);
      if (weight < 0.02) continue;

      const vec = tr.vector;
      if (vec.threat && vec.threat > 0) {
        this.fluid_target["恐惧"] = Math.min(1.0, this.fluid_target["恐惧"] + weight * 0.1 * vec.threat);
      }
      if (vec.belonging && vec.belonging < 0) {
        this.fluid_target["疏离"] = Math.min(1.0, this.fluid_target["疏离"] + weight * 0.1 * (-vec.belonging));
        this.fluid_target["信任"] = Math.max(0.0, this.fluid_target["信任"] - weight * 0.08 * (-vec.belonging));
      } else if (vec.belonging && vec.belonging > 0) {
        this.fluid_target["喜悦"] = Math.min(1.0, this.fluid_target["喜悦"] + weight * 0.1 * vec.belonging);
      }
    }

    for (const k of Object.keys(this.fluid_target)) {
      this.fluid_target[k] = Math.max(0.0, Math.min(1.0, this.fluid_target[k]));
    }
  }

  // ==================================================================
  // 系统反馈
  // ==================================================================
  _fluidToSystemFeedback() {
    const tension = this.fluid["张力"] || 0.0;
    this.psy_dilation = 1.0 + this.time_compress_base * 2.0 + tension * 0.5;

    const guilt = this.fluid["愧疚"] || 0.0;
    if (guilt > 0.3 && this.max_trust < 1.0) {
      this.max_trust = Math.min(1.0, this.max_trust + guilt * 0.0001);
    }

    const shame = this.fluid["羞耻"] || 0.0;
    if (shame > 0.4) {
      this.self_esteem = Math.max(0.1, this.self_esteem - shame * 0.0005);
    }
  }

  // ==================================================================
  // 能量和疲劳
  // ==================================================================
  _energyOnEvent(v: Record<string, number>, raw_intensity: number) {
    let cost = this.ENERGY_EVENT_COST * raw_intensity;
    const threat = v.threat || 0;
    const belonging = v.belonging || 0;
    if (threat > 0.2 || belonging < -0.2) {
      cost *= 1.8;
    }
    cost *= (1.0 + (this.fluid["张力"] || 0));
    cost *= (1.0 + this.cognitive_dissonance * 0.5);
    this.energy = Math.max(this.ENERGY_MIN, this.energy - cost);
  }

  _energyIdle(dt: number) {
    let recover = this.ENERGY_RECOVER * dt * (1.0 - 0.5 * this.fatigue);
    recover *= (1.0 - this.sleep_debt * 0.4);
    this.energy = Math.min(this.ENERGY_MAX, this.energy + recover);
  }

  // ==================================================================
  // 艾宾浩斯遗忘曲线
  // ==================================================================
  _forgetOver(dt: number) {
    const survivors: MemoryTrace[] = [];
    const now = this._now();
    for (const tr of this.memory_traces) {
      const age = now - tr.timestamp;
      const strength = tr.strength * Math.exp(-this.forgetting_rate * age / 10.0);
      if (strength > this.trace_importance_threshold) {
        tr.strength = strength;
        tr.age = age;
        survivors.push(tr);
      }
    }
    this.memory_traces = survivors;
  }

  // ==================================================================
  // 兴奋度
  // ==================================================================
  _excitationOnEvent(v: PsychologicalVector, raw_intensity: number) {
    let novelty = raw_intensity * this.EXCITATION_NOVELTY_GAIN;
    const threat = v.threat || 0.0;
    const belonging = v.belonging || 0.0;
    if (Math.abs(threat) > 0.5 || Math.abs(belonging) > 0.5) {
      novelty += raw_intensity * this.EXCITATION_SALIENCE_BOOST;
    }
    this.excitation = Math.min(this.EXCITATION_MAX, this.excitation + novelty);
  }

  _excitationDecay(dt: number) {
    if (this.excitation > this.EXCITATION_BASELINE) {
      this.excitation += (this.EXCITATION_BASELINE - this.excitation) * (1.0 - Math.exp(-this.EXCITATION_DECAY * dt));
      if (Math.abs(this.excitation - this.EXCITATION_BASELINE) < 0.005) {
        this.excitation = this.EXCITATION_BASELINE;
      }
    }
  }

  _checkBoredom(dt: number) {
    if (this.excitation < this.EXCITATION_BOREDOM_THRESHOLD) {
      this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + 0.003 * dt / 60);
      this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + 0.002 * dt / 60);
    }
  }

  // ==================================================================
  // 心境慢变量更新
  // ==================================================================
  _updateMood() {
    const joy = this.fluid["喜悦"] || 0.0;
    const anger = this.fluid["愤怒"] || 0.0;
    const fear = this.fluid["恐惧"] || 0.0;
    const alienation = this.fluid["疏离"] || 0.0;
    const shame = this.fluid["羞耻"] || 0.0;
    const tension = this.fluid["张力"] || 0.0;

    let target_pleasant = joy * 0.4 - anger * 0.3 - fear * 0.25 - alienation * 0.2 - shame * 0.3 + this.self_esteem * 0.4 + 0.3;
    target_pleasant = Math.max(0.0, Math.min(1.0, target_pleasant));

    let target_tension = tension * 0.5 + fear * 0.3 + this.cognitive_dissonance * 0.3 + this.sleep_debt * 0.3 + 0.1;
    target_tension = Math.max(0.0, Math.min(1.0, target_tension));

    let target_vigor = 1.0 - this.fatigue * 0.5 - this.sleep_debt * 0.6 - tension * 0.2 + this.self_esteem * 0.3;
    target_vigor = Math.max(0.0, Math.min(1.0, target_vigor));

    const alpha = this.MOOD_INERTIA;
    this.mood["愉悦"] += (target_pleasant - this.mood["愉悦"]) * alpha;
    this.mood["紧张"] += (target_tension - this.mood["紧张"]) * alpha;
    this.mood["精力"] += (target_vigor - this.mood["精力"]) * alpha;
  }

  // ==================================================================
  // 梦境情绪加工
  // ==================================================================
  _dreamProcess() {
    for (const tr of this.memory_traces) {
      const vec = tr.vector;
      for (const k of Object.keys(vec)) {
        if (Math.abs(vec[k]) > 0.05) {
          vec[k] *= (1.0 - this.DREAM_EMOTION_DECAY);
        }
      }
    }

    for (const tr of this.memory_traces) {
      if (tr.vector.threat && tr.vector.threat > 0.1) {
        const extinction = this.DREAM_FEAR_EXTINCTION * (0.4 + this.self_esteem * 1.2);
        tr.vector.threat *= (1.0 - extinction);
        tr.strength *= (1.0 - extinction * 0.5);
      }
    }

    this._healTraumas(90.0 * 60.0 * this.DREAM_TRAUMA_HEAL_BOOST * 0.1);
  }

  // ==================================================================
  // 预期计算
  // ==================================================================
  _computeSurprise(event_id: string, vector: PsychologicalVector, intensity: number): number {
    const exp = this.expected_events[event_id];
    delete this.expected_events[event_id];

    const expected_valence = exp.valence;
    const confidence = exp.confidence;

    let actual_valence = (vector.belonging || 0.0) - (vector.threat || 0.0) + (vector.autonomy || 0.0);
    actual_valence = Math.max(-1.0, Math.min(1.0, actual_valence));

    let surprise = (actual_valence - expected_valence) * confidence;
    const age = this._now() - exp.time;
    const age_discount = Math.exp(-0.00001 * age); // ~1天半衰期
    surprise *= age_discount

    return Math.max(-1.0, Math.min(1.0, surprise));
  }

  _applySurprise(perceived: Record<string, number>, surprise: number): Record<string, number> {
    const out = { ...perceived };
    if (surprise > 0.1) {
      out.belonging = (out.belonging || 0.0) + surprise * this.SURPRISE_POSITIVE_BOOST;
      out.threat = (out.threat || 0.0) - surprise * this.SURPRISE_POSITIVE_BOOST * 0.5;
    } else if (surprise < -0.1) {
      const mag = Math.abs(surprise);
      out.threat = (out.threat || 0.0) + mag * this.SURPRISE_NEGATIVE_BOOST;
      out.belonging = (out.belonging || 0.0) - mag * this.SURPRISE_NEGATIVE_BOOST * 0.7;
    }
    return out;
  }

  _decayExpectations(dt: number) {
    const now = this._now();
    const expired: string[] = [];
    for (const eid of Object.keys(this.expected_events)) {
      const exp = this.expected_events[eid];
      const decay = this.EXPECTATION_DECAY * dt;
      exp.confidence = Math.max(0.0, exp.confidence - decay);
      if (exp.confidence < 0.05) {
        expired.push(eid);
      }
    }
    for (const eid of expired) {
      delete this.expected_events[eid];
    }
  }

  // ==================================================================
  // 自尊更新
  // ==================================================================
  _updateSelfEsteem(v: Record<string, number>) {
    const b = v.belonging || 0.0;
    const t = v.threat || 0.0;
    const a = v.autonomy || 0.0;

    let impact = 0.0;
    if (b > 0) {
      impact += b * this.SELF_ESTEEM_UPDATE_RATE * (0.3 + this.self_esteem * 1.4);
    }
    if (b < 0) {
      impact -= Math.abs(b) * this.SELF_ESTEEM_UPDATE_RATE * (1.5 - this.self_esteem);
    }
    if (a > 0) {
      impact += a * this.SELF_ESTEEM_UPDATE_RATE * 0.5;
    }
    if (t > 0 && b < 0) {
      impact -= t * Math.abs(b) * this.SELF_ESTEEM_UPDATE_RATE * 0.8;
    }

    this.self_esteem += impact * this.SELF_ESTEEM_INERTIA;
    this.self_esteem = Math.max(0.05, Math.min(0.95, this.self_esteem));
  }

  // ==================================================================
  // 认知失调消解
  // ==================================================================
  _dissonanceDynamics(v: Record<string, number>) {
    if (this.cognitive_dissonance > this.DISSONANCE_THRESHOLD) {
      const rationalize_amount = this.cognitive_dissonance * 0.15;
      this.rationalization_load = Math.min(1.0, this.rationalization_load + rationalize_amount);
      this.cognitive_dissonance *= 0.85;

      this.energy = Math.max(this.ENERGY_MIN, this.energy - rationalize_amount * 2.0);
      this.fluid["张力"] = Math.max(0.0, (this.fluid["张力"] || 0) - rationalize_amount * 0.2);
    }
  }

  // ==================================================================
  // 防御层级
  // ==================================================================
  _defenseHierarchy(v: Record<string, number>) {
    const threat = v.threat || 0.0;
    const neg_belonging = Math.max(0.0, -(v.belonging || 0.0));
    const total_neg = threat + neg_belonging;

    if (total_neg < 0.1) {
      this._suppressionDynamics(v);
      return;
    }

    const denial_tendency = 0.3 * (1.0 - this.self_esteem);
    const denied = total_neg * denial_tendency;

    let v_modified = { ...v };
    if (denied > 0.02) {
      this.denial_load += denied;
      const remaining_denial = 1.0 - denial_tendency;
      if (v_modified.threat) {
        v_modified.threat *= remaining_denial;
      }
      if (v_modified.belonging && v_modified.belonging < 0) {
        v_modified.belonging *= remaining_denial;
      }
    }

    if (this.denial_load >= this.DENIAL_THRESHOLD && this.denial_burst_cd <= 0) {
      this._triggerDenialBurst();
    }

    const rationalize_tendency = 0.2;
    const remaining_neg = (v_modified.threat || 0.0) + Math.max(0.0, -(v_modified.belonging || 0.0));
    const rationalized = remaining_neg * rationalize_tendency;

    if (rationalized > 0.02) {
      this.rationalization_load = Math.min(1.0, this.rationalization_load + rationalized);
      if (v_modified.threat) {
        v_modified.threat *= (1.0 - rationalize_tendency);
      }
      if (v_modified.belonging && v_modified.belonging < 0) {
        v_modified.belonging *= (1.0 - rationalize_tendency * 0.5);
      }
    }

    this._suppressionDynamics(v_modified);
  }

  _triggerDenialBurst() {
    this.denial_burst_cd = this.DENIAL_BURST_COOLDOWN;
    const load = this.denial_load;
    this.denial_load = 0.0;

    this.fluid["恐惧"] = Math.min(1.0, (this.fluid["恐惧"] || 0) + load * 0.7);
    this.fluid["张力"] = Math.min(1.0, (this.fluid["张力"] || 0) + load * 0.5);
    this.fluid["疏离"] = Math.min(1.0, (this.fluid["疏离"] || 0) + load * 0.4);
    this.fluid["信任"] = Math.max(0.0, (this.fluid["信任"] || 0) - load * 0.3);

    this.energy = Math.max(this.ENERGY_MIN, this.energy - load * 6);
    this.time_compress_base = Math.min(1.0, this.time_compress_base + 0.5);

    this.burst_events.push({
      type: "denial",
      timestamp: this._now(),
      detail: `否认壁垒破裂！现实强烈侵入。否认负荷 ${load.toFixed(2)}。恐惧、张力和疏离感骤增！`
    });
  }

  // ==================================================================
  // 核心状态快照导出
  // ==================================================================
  snapshot() {
    return {
      fluid: { ...this.fluid },
      fluid_target: { ...this.fluid_target },
      fluid_baseline: { ...this.fluid_baseline },
      mood: { ...this.mood },
      self_esteem: this.self_esteem,
      energy: this.energy,
      fatigue: this.fatigue,
      excitation: this.excitation,
      max_trust: this.max_trust,
      suppression_load: this.suppression_load,
      denial_load: this.denial_load,
      rationalization_load: this.rationalization_load,
      latent_pressure: this.latent_pressure,
      cognitive_dissonance: this.cognitive_dissonance,
      sleep_debt: this.sleep_debt,
      trauma: { ...this.trauma_state },
      memory_traces: [...this.memory_traces],
      expected_events: { ...this.expected_events },
      last_perceived: { ...this.last_perceived },
      burst_events: [...this.burst_events],
      last_time: this.last_time,
      psy_dilation: this.psy_dilation,
    };
  }

  // ==================================================================
  // 序列化 / 反序列化以实现 LocalStorage 固化持久化
  // ==================================================================
  serialize(): string {
    return JSON.stringify({
      psychological_resilience: this.psychological_resilience,
      energy: this.energy,
      affinity: this.affinity,
      last_time: this.last_time,
      fluid: this.fluid,
      fluid_target: this.fluid_target,
      fluid_baseline: this.fluid_baseline,
      mood: this.mood,
      sleep_debt: this.sleep_debt,
      last_sleep_time: this.last_sleep_time,
      self_esteem: this.self_esteem,
      expected_events: this.expected_events,
      cognitive_dissonance: this.cognitive_dissonance,
      denial_load: this.denial_load,
      denial_burst_cd: this.denial_burst_cd,
      rationalization_load: this.rationalization_load,
      trauma_state: this.trauma_state,
      memory_traces: this.memory_traces,
      suppression_load: this.suppression_load,
      suppression_burst_cd: this.suppression_burst_cd,
      latent_pressure: this.latent_pressure,
      avalanche_cd: this.avalanche_cd,
      max_trust: this.max_trust,
      dynamic_viscosity: this.dynamic_viscosity,
      psy_dilation: this.psy_dilation,
      time_compress_base: this.time_compress_base,
      excitation: this.excitation,
      fatigue: this.fatigue,
      last_perceived: this.last_perceived,
      burst_events: this.burst_events
    });
  }

  deserialize(jsonStr: string) {
    try {
      const data = JSON.parse(jsonStr);
      if (data.psychological_resilience !== undefined) this.psychological_resilience = data.psychological_resilience;
      if (data.energy !== undefined) this.energy = data.energy;
      if (data.affinity !== undefined) this.affinity = data.affinity;
      if (data.last_time !== undefined) this.last_time = data.last_time;
      if (data.fluid !== undefined) this.fluid = { ...this.fluid, ...data.fluid };
      if (data.fluid_target !== undefined) this.fluid_target = { ...this.fluid_target, ...data.fluid_target };
      if (data.fluid_baseline !== undefined) this.fluid_baseline = { ...this.fluid_baseline, ...data.fluid_baseline };
      if (data.mood !== undefined) this.mood = { ...this.mood, ...data.mood };
      if (data.sleep_debt !== undefined) this.sleep_debt = data.sleep_debt;
      if (data.last_sleep_time !== undefined) this.last_sleep_time = data.last_sleep_time;
      if (data.self_esteem !== undefined) this.self_esteem = data.self_esteem;
      if (data.expected_events !== undefined) this.expected_events = data.expected_events;
      if (data.cognitive_dissonance !== undefined) this.cognitive_dissonance = data.cognitive_dissonance;
      if (data.denial_load !== undefined) this.denial_load = data.denial_load;
      if (data.denial_burst_cd !== undefined) this.denial_burst_cd = data.denial_burst_cd;
      if (data.rationalization_load !== undefined) this.rationalization_load = data.rationalization_load;
      if (data.trauma_state !== undefined) this.trauma_state = data.trauma_state;
      if (data.memory_traces !== undefined) this.memory_traces = data.memory_traces;
      if (data.suppression_load !== undefined) this.suppression_load = data.suppression_load;
      if (data.suppression_burst_cd !== undefined) this.suppression_burst_cd = data.suppression_burst_cd;
      if (data.latent_pressure !== undefined) this.latent_pressure = data.latent_pressure;
      if (data.avalanche_cd !== undefined) this.avalanche_cd = data.avalanche_cd;
      if (data.max_trust !== undefined) this.max_trust = data.max_trust;
      if (data.dynamic_viscosity !== undefined) this.dynamic_viscosity = data.dynamic_viscosity;
      if (data.psy_dilation !== undefined) this.psy_dilation = data.psy_dilation;
      if (data.time_compress_base !== undefined) this.time_compress_base = data.time_compress_base;
      if (data.excitation !== undefined) this.excitation = data.excitation;
      if (data.fatigue !== undefined) this.fatigue = data.fatigue;
      if (data.last_perceived !== undefined) this.last_perceived = data.last_perceived;
      if (data.burst_events !== undefined) this.burst_events = data.burst_events;
    } catch (e) {
      console.error("Failed to deserialize SPL state:", e);
    }
  }
}
