# Your Mirror · 拟人化智能体引擎（移动端）

> 基于 SPL 第二视角因果拓扑网络的拟人化智能体对话应用
> 版本 **v1.1** · 包名 `com.nohnlins.characterstudio`

「Your Mirror」把第二视角的因果推理能力装进口袋——与你的专属智能体对话、协作、推演，对话基于决定论因果链而非概率推测。

## ✨ 特性

- 🧠 **SPL 因果引擎**：内置第二视角因果拓扑网络
- 🤖 **多智能体**：内置多套预设 + 支持自定义智能体（角色/语气/行为参数）
- 🌐 **5 语言界面**：简中 / EN / 日本語 / 한국어 / 繁中，一键切换并持久化
- 🔒 **本地优先**：对话与设置全部存于 localStorage，不上传任何数据
- 🔌 **API 可配置**：默认 Gemini，支持自定义 Base URL / Key / 模型
- 📱 **多形态**：Android App（AAB）+ Web/PWA + Web 自包含包

## 📲 安装

- **Google Play**：[在 Google Play 下载](https://play.google.com/store/apps/details?id=com.nohnlins.characterstudio)
- **直接侧载**：从 `release/` 下载 AAB（Android 7.0+）：`release/1.1.aab`（5.09 MB）

> AAB 为 Play 标准发布格式；侧载安装需用 bundletool/aapt 转 APK 或使用 debug APK。

## 🛠️ 构建

**前置**：Node 18+ / JDK 17 / Android SDK（compileSdk 36）

```bash
npm install && npm run build
npx cap sync android
cd android && ./gradlew bundleRelease   # 产物: app/build/outputs/bundle/release/
```

或一条命令 `npm run build:aab`

## 📂 目录结构

```
android/      # Capacitor Android 原生壳（Gradle 工程）
src/          # React + Vite + TS 前端
  ├── lib/SPLEngine.ts   # SPL 因果引擎
  └── i18n.ts            # 5 语言字典
public/       # PWA 资源 + Web 自包含包
screenshots/  # 界面截图
scripts/      # 构建辅助脚本
```

## 🔗 相关

- 引擎本体：本仓库 `main` 分支
- 认知审计引擎在线版：https://nohnlins.com/audit/
