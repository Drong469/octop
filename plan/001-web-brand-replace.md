# 001 · 第一阶段技术方案：Web 层品牌换脸（元控智能 / MetaControl AI）

> 状态：待用户确认开工
> 日期：2026-10-13
> 前置：阶段 0（原版基线跑通）已完成；grill-with-docs 审问已完成，术语见仓库根 `CONTEXT.md`

---

## 1. 背景与目标

Octop（腾讯开源，v1.0.2b7，MIT）是元控智能的技术基座。本阶段把**用户可见 Web 层**的品牌从 Octop 替换为元控智能 / MetaControl AI，主题默认色统一为深蓝。

目标：**外行用户感知不到 Octop 来源**。代码层痕迹（包名、`OCTOP_` 环境变量、依赖名、LICENSE）不在本阶段范围——MIT 许可依法要求保留原版权声明，体验层与代码层脱钩是刻意设计。

## 2. 决策记录（grill-with-docs 审问共识）

| # | 决策点 | 结论 |
|---|---|---|
| D1 | 品牌名 | 中文「元控智能」，英文「MetaControl AI」（占位，公司定稿后只换资产） |
| D2 | 品牌资产 | **复用 openclaw 项目（元控智能上一版）的现成 VI**；母版 `D:\openclaw\openclaw\img\LOGO.png`（1080×1080，蓝底白字「元控」） |
| D3 | 默认主题色 | 预置调色板 `tech`（#3A5FE0 深蓝），改 `DEFAULT_PALETTE` 常量，可回退 |
| D4 | 改名范围 | 方案 A：用户可见 Web 层（B 层开发者可见项酌情后续） |
| D5 | 吉祥物 | 章鱼全部静态占位替换（动画位降级为静图） |
| D6 | 桌面端 | 不纳入本阶段（Web 换脸自动穿透桌面窗口；外壳品牌 + 「连接服务器」产品化留到内网部署阶段） |
| D7 | Slogan | `元控智能 - 让 AI 融入你的工作`（方案 A） |

## 3. 范围

### 做（In scope）
- `dashboard/src/styles/`：默认主题色 + 守护测试
- `dashboard/index.html`：标题、PWA meta
- `dashboard/public/manifest.json`：PWA 名称
- `dashboard/src/locales/{zh,en}.json`：品牌展示文案
- `dashboard/public/`：全套品牌资产同名替换（LOGO 加工）

### 不做（Out of scope，留档）
| 项 | 层级 | 原因 |
|---|---|---|
| `src/octop/i18n/{zh,en}.json`（后端 IM/CLI/错误文案） | B | 开发者/IM 可见，第二阶段酌情 |
| CLI 输出、FastAPI title、`X-Octop-Access-Token` | B | 同上 |
| 包名、`OCTOP_` 环境变量、`~/.octop` 数据目录 | C | 破坏上游同步，明确不做 |
| `desktop/`（Go+Wails 壳） | — | D6 |
| LICENSE / 版权声明 | — | MIT 依法保留 |

## 4. 资产映射（openclaw → dashboard/public/，同名覆盖）

| Octop 目标文件（文件名不变） | 引用位置 | 来源与加工 |
|---|---|---|
| `logo_horizontal_dark.png` / `logo_horizontal_white.png` | `layouts/Sidebar.tsx:432`、`layouts/Header.tsx:25`、`pages/Setup/index.tsx:262`（明/暗主题各取其一）。~~`pages/Login/index.tsx:274`~~ **执行变更**：登录页改为引用独立图标 `logo_icon.png`（用户决策：登录页用图标、侧边栏保留艺术字），并顺手修复 `alt="Octop"` 残留 | `LOGO.png` 按原文件画布尺寸缩放；LOGO 为蓝底白字，明暗通用，两份同图 |
| `favico.svg` | 浏览器标签 | 直接复用 `D:\openclaw\openclaw\ui\public\favicon.svg` 内容（矢量，同为元控图标） |
| `apple-touch-icon.png` | iOS/PWA 主屏 | LOGO 缩放 180×180 |
| `pwa-512.png` / `pwa-192.png` | PWA 安装图标 | LOGO 缩放 512 / 192 |
| `logo_vertical_dark.svg` / `logo_vertical_white.svg` | 离线页（`offline.html`） | **SVG 壳内嵌 base64 PNG**（`<svg><image href="data:image/png;base64,…"/></svg>`）——保持 `.svg` 文件名与引用兼容，内容用 LOGO 加工图 |
| `octop-mascot-empty.png` | 空状态插画（`components/EmptyState/OctopEmptyMascot.tsx`，20+ 页面） | LOGO 圆角 + 缩放（PIL） |
| `octop-mascot-tasks.png` | 任务页 | 同上 |
| `octop-mascot-peek.webp` / `octop-mascot-type.webp` | **三处代码引用**：欢迎屏随机池（`pages/Chat/components/WelcomeScreen.tsx:8-9`）、连接指示器（`components/StreamConnectingIndicator/index.tsx:4`）、AI 思考气泡（`pages/Chat/components/ThinkingBubble.tsx:15`） | 同一张 LOGO 加工静图；同名覆盖，三处自动生效，**无需改任何引用代码** |
| `octop-mascot-peek.webm` / `octop-mascot-type.webm` | **死资产，零代码引用**（已全目录核实：唯一 `.webm` 引用是 `api/modules/voice.ts:48` 的录音产物名，无关） | 不处理——未引用即不进 UI，外行不可见；按外科手术原则不顺手删除 |

> 观感预期：空状态从「粉色章鱼插画」变为「蓝色方块应用图标」，稳重风格与企业工作台定位一致；将来正式 VI/吉祥物出来后仅替换文件。

## 5. 改动清单（文件级）

### 5.1 主题默认色（约 2 个文件）
- `dashboard/src/styles/themePalettes.ts:28`：`DEFAULT_PALETTE: ThemePalette = "rose"` → `"tech"`
- `dashboard/src/styles/themePalettes.test.ts:39-45`：默认色守护测试（"keeps the historic Elegant Rose default"）期望值改为 tech（`#3A5FE0` / `#2E4FD4` / `#233FB8`）
- `appearanceStorage.test.ts` 引用的是 `DEFAULT_PALETTE` 常量本身，自动跟随，无需改动

### 5.2 标题与 PWA 文本
- `dashboard/index.html`：`<title>` → `元控智能 - 让 AI 融入你的工作`；`apple-mobile-web-app-title` → `元控智能`；检查 `meta description` / `theme-color`
- `dashboard/public/manifest.json`：`name` / `short_name` → `元控智能`
- **明确不动**：`App.tsx` 的 `prefixCls="octop"`、localStorage key `octop:*`（功能性，B/C 层）

### 5.3 locale 品牌文案
- `dashboard/src/locales/zh.json` / `en.json`（各约 132 行含 Octop 字样）
- 流程：① 全量列出含 `Octop/octop` 的行 → ② 人工分类【品牌展示：改 / 技术引用：不改】 → ③ zh 替换为「元控智能」，en 替换为 `MetaControl AI`；`app.pageTitle` 按 D7 slogan
- 禁止盲目全局替换（存在 `X-Octop-Access-Token` 等技术引用文案）；替换后全量 diff 审查

### 5.4 资产加工与替换
- 加工脚本：Python + PIL（`pillow` 已在 `.venv`），从母版 `LOGO.png` 生成全部目标尺寸；圆角处理用于吉祥物位
- 产出到 `dashboard/public/` 同名覆盖；完成后跑一次构建 + 截图确认无资源 404

## 6. 实施步骤

| 批次 | 内容 | 依赖 | 预估 |
|---|---|---|---|
| B1 | 主题色 + 守护测试同步 | 无 | 15 分钟 |
| B2 | index.html / manifest / locale 品牌文案（含分类清单） | 无 | 1 小时 |
| B3 | 资产加工与替换（PIL 脚本，纯文件同名覆盖） | openclaw 资产已就位 ✅ | 1 小时 |
| B4 | `npx tsc -b` + vitest 相关测试 + `npm run build` | B1–B3 | 10 分钟 |
| B5 | 服务重启（用户窗口）→ 系统 Edge 截图对比基线 + 功能点检 | B4 | 15 分钟 |
| B6 | 汇报 diff + 截图 → 用户确认 → 提交推送 | B5 | 10 分钟 |

## 7. 验证标准

1. `npx tsc -b` 零错误；dashboard vitest 相关套件全绿
2. 生产构建成功
3. Edge（全新浏览器上下文，避开本机 localStorage 里的 rose 偏好）：
   - 标签页标题 / favicon = 元控智能
   - 登录页：新 Logo、无章鱼
   - 主界面：侧边栏新 Logo、主色深蓝（tech）、空状态为新形象
   - 明 / 暗两种主题下 Logo 均正常
4. 功能点检：登录、全菜单导航、专家页、知识库页渲染正常
5. 截图与阶段 0 基线（`%TEMP%\octop-ui-check\01-06.png`）对比，留档到 `plan/assets/`

## 8. 提交策略（遵守「未确认不提交」红线）

- B5 验证通过 → 汇报 diff 摘要 + 换脸前后截图 → **用户确认**
- commit 风格：conventional commits（中文），如 `feat(brand): replace web identity with MetaControl AI (YuanKong)`
- push：`origin main`（GitHub 主仓库）+ `gitee main`（备份）；`upstream` 永不推
- 注意：本仓库**未启用** `.githooks`（`make install-hooks` 未跑，且 Windows 无 make）——提交不触发 pre-commit，质量由 B4 手动验证保证

## 9. 上游冲突预期

| 文件 | 冲突概率 | 应对 |
|---|---|---|
| `locales/{zh,en}.json` | **高**（上游高频改文案） | 替换规则机械，冲突时重放 |
| `themePalettes.ts` + 守护测试 | 低 | — |
| `index.html` / `manifest.json` | 低 | — |
| `public/` 资产 | 无（二进制同名覆盖） | 文件名不变是刻意设计，上游新增引用不坏 |

> 本阶段无任何 mascot 相关代码改动（webp 三处引用同名覆盖自动生效；webm 为死资产不处理）。

## 10. 风险与注意点

1. 本机 Edge localStorage 已存 rose 偏好（个人偏好优先于默认值）→ 验证一律用全新上下文
2. PWA Service Worker 缓存旧资产 → 强刷 `Ctrl+Shift+R` 或等 SW 更新（一次性）
3. locale 误伤技术引用 → 先分类后替换 + 全量 diff 审查
4. `offline.html` 对 `logo_vertical_*.svg` 的引用 → 用「SVG 壳内嵌 PNG」保持兼容
5. 空状态观感从插画变为图标式 → 已在 D5 确认接受；正式 VI 后仅换文件

## 11. 附录：关键代码事实

| 事实 | 位置 |
|---|---|
| `DEFAULT_PALETTE = "rose"` | `dashboard/src/styles/themePalettes.ts:28` |
| 默认色守护测试 | `dashboard/src/styles/themePalettes.test.ts:39-45` |
| Logo 固定 URL 引用 | `Sidebar.tsx:432`、`Header.tsx:25`、`Login/index.tsx:274`、`Setup/index.tsx:262` |
| 吉祥物组件与来源 | `components/EmptyState/OctopEmptyMascot.tsx` ← `assets/mascot.ts` |
| 吉祥物 webp 引用（3 处，均只读文件） | `WelcomeScreen.tsx:8-9`（欢迎屏随机池）、`StreamConnectingIndicator/index.tsx:4`（连接指示器）、`ThinkingBubble.tsx:15`（思考气泡） |
| `.webm` 死资产 | `public/octop-mascot-{peek,type}.webm` 零代码引用（全目录核实；唯一 `.webm` 引用为 `api/modules/voice.ts:48`，录音产物名，无关） |
| 调色板切换器挂载点 | `components/AvatarDropdown.tsx:648`（左下角头像菜单） |
| PWA manifest 来源 | `dashboard/vite.config.ts:182`（`manifest:false` → 用 `public/manifest.json`） |
| 资产母版 | `D:\openclaw\openclaw\img\LOGO.png`（1080×1080 蓝底白字「元控」；openclaw 的 `manifest.webmanifest` 品牌名即「元控智能」） |
| 阶段 0 基线截图 | `%TEMP%\octop-ui-check\01~06.png` |
