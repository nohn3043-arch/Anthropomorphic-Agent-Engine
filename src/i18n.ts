export type LanguageCode = "zh-CN" | "en" | "ja" | "ko" | "zh-TW";

export const LANGUAGE_OPTIONS: Array<{
  code: LanguageCode;
  label: string;
  nativeLabel: string;
  shortLabel: string;
}> = [
  { code: "zh-CN", label: "Simplified Chinese", nativeLabel: "简体中文", shortLabel: "简" },
  { code: "en", label: "English", nativeLabel: "English", shortLabel: "EN" },
  { code: "ja", label: "Japanese", nativeLabel: "日本語", shortLabel: "日" },
  { code: "ko", label: "Korean", nativeLabel: "한국어", shortLabel: "한" },
  { code: "zh-TW", label: "Traditional Chinese", nativeLabel: "繁體中文", shortLabel: "繁" }
];

const LOCALE_TEXT: Partial<Record<LanguageCode, Record<string, string>>> = {
  "zh-TW": {
    "Language": "語言",
    "Language settings": "語言設定",
    "Display language": "顯示語言",
    "Choose the language used by the app interface.": "選擇應用介面使用的語言。",
    "Dashboard": "儀表板",
    "Agent Chat": "智能體對話",
    "Extension Packer": "擴充套件打包",
    "Mind Presets & Custom Personalities": "心智預設與自訂人格",
    "Custom JSON Sandbox": "自訂 JSON 沙盒",
    "Close sandbox": "收起沙盒",
    "Custom Agent JSON Schema": "自訂人格 JSON 規格",
    "Cancel": "取消",
    "Import & Activate Preset": "匯入並啟用預設",
    "8-Dimensional Emotional Fluids": "八維連續情緒流體",
    "Click card to toggle details": "點擊卡片切換詳情",
    "Current value": "目前值",
    "Adaptive target": "自適應目標",
    "Psychological baseline": "心理基線",
    "Adaptive Target": "自適應目標",
    "ACTIVE": "已啟用",
    "BUILTIN": "內建",
    "Edit": "編輯",
    "Delete": "刪除",
    "Delete custom personality": "刪除自訂人格",
    "Export JSON": "匯出 JSON",
    "Edit Personality JSON": "編輯人格 JSON",
    "Close": "關閉",
    "Initialize Engine": "初始化引擎",
    "VIRTUAL TIME": "虛擬時間",
    "RATE": "速率"
  },
  ja: {
    "Language": "言語",
    "Language settings": "言語設定",
    "Display language": "表示言語",
    "Choose the language used by the app interface.": "アプリ画面で使う言語を選択します。",
    "Dashboard": "ダッシュボード",
    "Agent Chat": "エージェント会話",
    "Extension Packer": "拡張機能パッカー",
    "Mind Presets & Custom Personalities": "心理プリセットとカスタム人格",
    "Custom JSON Sandbox": "カスタム JSON サンドボックス",
    "Close sandbox": "サンドボックスを閉じる",
    "Custom Agent JSON Schema": "カスタム人格 JSON スキーマ",
    "Cancel": "キャンセル",
    "Import & Activate Preset": "プリセットを読み込んで有効化",
    "8-Dimensional Emotional Fluids": "8次元の感情流体",
    "Click card to toggle details": "カードを押して詳細を切り替え",
    "Current value": "現在値",
    "Adaptive target": "適応目標",
    "Psychological baseline": "心理ベースライン",
    "Adaptive Target": "適応目標",
    "ACTIVE": "有効",
    "BUILTIN": "内蔵",
    "Edit": "編集",
    "Delete": "削除",
    "Delete custom personality": "カスタム人格を削除",
    "Export JSON": "JSONを書き出し",
    "Edit Personality JSON": "人格 JSON を編集",
    "Close": "閉じる",
    "Initialize Engine": "エンジンを初期化",
    "VIRTUAL TIME": "仮想時間",
    "RATE": "倍率"
  },
  ko: {
    "Language": "언어",
    "Language settings": "언어 설정",
    "Display language": "표시 언어",
    "Choose the language used by the app interface.": "앱 화면에 사용할 언어를 선택합니다.",
    "Dashboard": "대시보드",
    "Agent Chat": "에이전트 채팅",
    "Extension Packer": "확장 프로그램 패커",
    "Mind Presets & Custom Personalities": "마음 프리셋 및 사용자 성격",
    "Custom JSON Sandbox": "사용자 JSON 샌드박스",
    "Close sandbox": "샌드박스 닫기",
    "Custom Agent JSON Schema": "사용자 성격 JSON 스키마",
    "Cancel": "취소",
    "Import & Activate Preset": "프리셋 가져오기 및 활성화",
    "8-Dimensional Emotional Fluids": "8차원 감정 유체",
    "Click card to toggle details": "카드를 눌러 세부 정보 전환",
    "Current value": "현재값",
    "Adaptive target": "적응 목표",
    "Psychological baseline": "심리 기준선",
    "Adaptive Target": "적응 목표",
    "ACTIVE": "활성",
    "BUILTIN": "내장",
    "Edit": "편집",
    "Delete": "삭제",
    "Delete custom personality": "사용자 성격 삭제",
    "Export JSON": "JSON 내보내기",
    "Edit Personality JSON": "성격 JSON 편집",
    "Close": "닫기",
    "Initialize Engine": "엔진 초기화",
    "VIRTUAL TIME": "가상 시간",
    "RATE": "비율"
  }
};

type LocalizedPreset = {
  name: string;
  description: string;
};

const PRESET_TEXT: Record<string, Partial<Record<LanguageCode, LocalizedPreset>>> = {
  preset_default: {
    "zh-TW": {
      name: "預設平衡心智",
      description: "健康且平衡的心理底色，具備中等韌性與穩定自尊恢復，能合理消化日常心理觸發。"
    },
    ja: {
      name: "標準の安定した心",
      description: "健全でバランスの取れた心理基盤。日常的な刺激を落ち着いて処理できます。"
    },
    ko: {
      name: "기본 균형 마음",
      description: "건강하고 균형 잡힌 심리 기반으로, 일상 자극을 안정적으로 소화합니다."
    }
  },
  preset_sensitive: {
    "zh-TW": {
      name: "高敏感自卑者",
      description: "自尊基礎脆弱、心理韌性偏低，對批評與威脅高度敏感，恐懼、愧疚與羞恥基線較高。"
    },
    ja: {
      name: "高感受性の魂",
      description: "自尊心が脆く、批判や脅威に強く反応します。恐れ、罪悪感、恥の基準値が高めです。"
    },
    ko: {
      name: "고감도 마음",
      description: "자존감 기반이 약하고 비판과 위협에 민감하며, 두려움과 죄책감, 수치심의 기준선이 높습니다."
    }
  },
  preset_narcissist: {
    "zh-TW": {
      name: "自戀防衛者",
      description: "膨脹自尊搭配強力自我合理化，會快速阻斷批評，或將其外射為憤怒。"
    },
    ja: {
      name: "自己愛的な防衛者",
      description: "高い自尊心と強い合理化で批判を遮断し、外向きの怒りへ変換します。"
    },
    ko: {
      name: "자기애 방어자",
      description: "부풀려진 자존감과 강한 합리화로 비판을 차단하거나 외부 분노로 전환합니다."
    }
  },
  preset_distant: {
    "zh-TW": {
      name: "冷淡避世者",
      description: "高度疏離與低信任基線，傾向以情感退縮阻斷威脅，長期維持距離。"
    },
    ja: {
      name: "冷たく距離を置く心",
      description: "疎外感が強く信頼の基準値が低め。感情的に退いて脅威を遮断します。"
    },
    ko: {
      name: "차갑고 거리 둔 마음",
      description: "소외감이 높고 신뢰 기준선이 낮아, 감정적으로 물러서며 위협을 차단합니다."
    }
  }
};

const FLUID_TEXT: Record<string, Partial<Record<LanguageCode, { name: string; desc: string }>>> = {
  Joy: {
    "zh-TW": { name: "喜悅", desc: "親和、放鬆與正向連結的流體指標。" },
    ja: { name: "喜び", desc: "親和、安心、前向きなつながりを示す流体指標。" },
    ko: { name: "기쁨", desc: "친밀감, 안정감, 긍정적 연결을 나타내는 유체 지표입니다." }
  },
  Anger: {
    "zh-TW": { name: "憤怒", desc: "邊界受侵犯或防衛被觸發時上升的流體指標。" },
    ja: { name: "怒り", desc: "境界が侵された時や防衛が起動した時に上がる指標。" },
    ko: { name: "분노", desc: "경계 침범이나 방어 반응이 일어날 때 상승하는 지표입니다." }
  },
  Fear: {
    "zh-TW": { name: "恐懼", desc: "風險感知、退縮與自我保護的流體指標。" },
    ja: { name: "恐れ", desc: "リスク認知、退避、自己防衛を示す指標。" },
    ko: { name: "두려움", desc: "위험 인식, 위축, 자기 보호를 나타내는 지표입니다." }
  },
  Trust: {
    "zh-TW": { name: "信任", desc: "安全感、依附與合作意願的流體指標。" },
    ja: { name: "信頼", desc: "安心、愛着、協力意欲を示す指標。" },
    ko: { name: "신뢰", desc: "안전감, 애착, 협력 의지를 나타내는 지표입니다." }
  },
  Alienation: {
    "zh-TW": { name: "疏離", desc: "心理距離、隔離感與斷開連結的流體指標。" },
    ja: { name: "疎外", desc: "心理的距離、孤立感、つながりの断絶を示す指標。" },
    ko: { name: "소외", desc: "심리적 거리, 고립감, 연결 단절을 나타내는 지표입니다." }
  },
  Tension: {
    "zh-TW": { name: "張力", desc: "內在壓力、警戒與不穩定程度的流體指標。" },
    ja: { name: "緊張", desc: "内的圧力、警戒、不安定さを示す指標。" },
    ko: { name: "긴장", desc: "내적 압력, 경계, 불안정성을 나타내는 지표입니다." }
  },
  Guilt: {
    "zh-TW": { name: "愧疚", desc: "責任感、自我譴責與修復衝動的流體指標。" },
    ja: { name: "罪悪感", desc: "責任感、自己非難、修復衝動を示す指標。" },
    ko: { name: "죄책감", desc: "책임감, 자기 비난, 회복 충동을 나타내는 지표입니다." }
  },
  Shame: {
    "zh-TW": { name: "羞恥", desc: "自我價值受損、暴露感與退縮傾向的流體指標。" },
    ja: { name: "恥", desc: "自己価値の傷つき、露出感、退縮傾向を示す指標。" },
    ko: { name: "수치심", desc: "자기 가치 손상, 노출감, 위축 경향을 나타내는 지표입니다." }
  }
};

export const normalizeLanguage = (saved?: string | null): LanguageCode => {
  if (saved === "zh") return "zh-CN";
  if (saved === "zh-CN" || saved === "en" || saved === "ja" || saved === "ko" || saved === "zh-TW") {
    return saved;
  }
  return "zh-CN";
};

export const translate = (lang: LanguageCode, zh: string, en: string): string => {
  if (lang === "zh-CN") return zh;
  if (lang === "en") return en;
  return LOCALE_TEXT[lang]?.[en] || en;
};

export const getLanguageText = (lang: LanguageCode, key: string): string => {
  if (lang === "en") return key;
  return LOCALE_TEXT[lang]?.[key] || key;
};

export const getPresetText = (
  lang: LanguageCode,
  preset: { id: string; name: string; nameEn: string; description: string; descriptionEn: string }
): LocalizedPreset => {
  if (lang === "zh-CN") {
    return { name: preset.name, description: preset.description };
  }
  if (lang === "en") {
    return { name: preset.nameEn, description: preset.descriptionEn };
  }
  return PRESET_TEXT[preset.id]?.[lang] || { name: preset.nameEn, description: preset.descriptionEn };
};

export const getFluidText = (
  lang: LanguageCode,
  meta: { nameEn: string; desc: string; descEn: string }
): { name: string; desc: string } => {
  if (lang === "zh-CN") return { name: "", desc: meta.desc };
  if (lang === "en") return { name: meta.nameEn, desc: meta.descEn };
  return FLUID_TEXT[meta.nameEn]?.[lang] || { name: meta.nameEn, desc: meta.descEn };
};
