# 002 · B2 技术方案：品牌文案替换清单（index.html / manifest / locales）

> 状态：待用户确认（未动手）
> 规则依据：`CONTEXT.md` Language 节 —— 中文品牌位 → **元控智能**，英文品牌位 → **MetaControl AI**；`_Avoid_: Octop`
> Slogan（D7）：`元控智能 - 让 AI 融入你的工作`

## 1. index.html（2 处改，其余为技术标识不动）

| 行 | 现状 | 改为 |
|---|---|---|
| 29 | `apple-mobile-web-app-title` = "Octop" | `元控智能` |
| 32 | `<title>Octop</title>` | `<title>元控智能 - 让 AI 融入你的工作</title>` |

**明确不动**：`#octop-boot`、`.octop-boot-*` CSS 类与动画 keyframes、`octop-boot-theme` script id、`octop:chunk-reload` sessionStorage key（纯技术标识，牵一发动全身，属 C 层）；`/logo_vertical_*.svg` 引用（B3 换文件内容，文件名不变）。

## 2. manifest.json（3 处改）

| 字段 | 现状 | 改为 |
|---|---|---|
| `name` | "Octop" | `元控智能` |
| `short_name` | "Octop" | `元控智能` |
| `description` | "Smarter self-hosted AI assistant — multi-user, multi-agent" | `元控智能 — 多用户、多智能体的企业 AI 工作台` |

**明确不动**：`theme_color`/`background_color`（颜色属主题体系，非本批次）、icons 数组（B3 换文件内容）。

## 3. locales 分类总览（zh.json 132 处；en.json 同 key 结构对应）

| 类别 | 处理 | 数量 | 规则 |
|---|---|---|---|
| **A 品牌散文** | **改** | ~88 行 | 散文里的产品名：zh `Octop` → `元控智能`；en `Octop` → `MetaControl AI`。行号清单见 §6 |
| **B 技术标识** | **不改** | ~33 行 | CLI 命令（`octop update` 等）、文件路径（`~/.octop`、`octop.cmd`）、环境变量（`OCTOP_*`）、技能 YAML 的 `octop:` metadata key、上游包名（`octop-harness`/`octop-gateway`/`octop-browser`）、pip extras（`octop[browser]`）、i18n key 名（`copyErrorForOctop`）。改了会破坏功能或误导用户 |
| **C 示例占位** | **待裁决（建议改）** | 5 行 | `octop.example.com`（×2）、`cn=svc-octop,…`、`octop-admins,…`、`D:/octop-data` —— 建议 → `metacontrol.example.com` / `cn=svc-metacontrol,…` / `metacontrol-admins,…` / `D:/yk-data` |
| **D OctopBot 平台** | **待裁决（建议不改）** | 3 行 | `label_octopbot`("OctopBot")、`octopbotGetCredentialsHint`、`intro_octopbot` —— OctopBot 是功能对接的托管机器人平台名，改名会造成语义错乱；建议第二阶段连同通道体系整体评估 |
| **混合行** | 部分 A 部分 B | 4 行 | `4763`（"重启 Octop（octop run）"→ 改品牌、留命令）、`4982`（路径留、品牌改）、`5676`（示例域名按 C 裁决、品牌改）、`6191`（品牌改、`octop plugin install` 命令留） |

## 4. en.json 替换规则

与 zh.json 相同 key 一一对应：品牌散文 `Octop` → `MetaControl AI`；`app.pageTitle` → `MetaControl AI - Let AI work for you`（D7 slogan 的英文占位，可后调）；B/C/D 类处理与 zh 一致。

## 5. 不在 B2 范围（重申）

- 后端 `src/octop/i18n/{zh,en}.json`（IM/CLI/错误文案，B 层）
- `App.tsx` 的 `prefixCls="octop"`、`styles/*.css` 里 74 处 `octop-` 类前缀、`api/modules/*` 里的 API 路径与 header、localStorage key —— 全部 C 层技术标识
- 上游 LICENSE

## 6. A 类逐行清单（zh.json 行号）

3, 47, 90, 129, 137, 138, 141, 145, 172, 176, 218, 567, 597, 609, 702, 715, 886, 1066, 1254, 1255, 1269, 2180, 2181, 2304, 2505, 3043, 3414, 3444, 3451, 3482, 3556, 3576, 3691, 3693, 3695, 3720, 3961, 3963, 3980, 3992, 3997, 4014, 4138, 4141, 4210, 4226, 4229, 4236, 4323, 4350, 4613, 4615, 4621, 4706, 4740, 4759, 4762, 4763※, 4764, 4950, 4956, 4981, 4982※, 5132, 5140, 5141, 5144, 5273, 5301, 5320, 5676※, 5679, 5702, 5713, 5723, 5733, 5742, 5745, 5778, 5782, 5783, 5784, 5947, 6105, 6129, 6191※, 6388, 6408, 6541, 6571, 6580（※ = 混合行，见 §3）

## 7. B 类逐行清单（zh.json 行号，不改）

76（i18n key 名）, 168, 624（~/octop-login.txt）, 716, 1052, 1053, 2071, 2170（技能 YAML `octop:` metadata key ×2）, 2274（OCTOP_DEFAULT_TIMEZONE）, 2607（octop-gateway）, 2736（~/.octop/env）, 2885（octop-harness）, 3589, 3598, 3603, 3612, 3615, 3616, 3628（CLI 命令与数据目录）, 4625, 4627（pip extras / 包名）, 5099（octop_sandbox）, 5274, 5276, 5277, 5278, 5279, 5280, 5282, 5284（密码重置命令与路径）, 5998（OCTOP_* 环境变量）, 6117, 6184（~/.octop/plugins）

## 8. C / D 类逐行（待裁决）

**C 类（示例占位，建议改）**：
| 行 | key | 现状片段 | 建议 |
|---|---|---|---|
| 3032 | domainPlaceholder | `octop.example.com` | `metacontrol.example.com` |
| 3481 | peerUrlPlaceholder | `https://octop.example.com` | `https://metacontrol.example.com` |
| 5715 | bindDnPlaceholder | `cn=svc-octop,ou=services,…` | `cn=svc-metacontrol,…` |
| 5743 | adminGroupsPlaceholder | `octop-admins, cn=it,…` | `metacontrol-admins, cn=it,…` |
| 1243 | path_outside_root | `例如 D:/octop-data` | `例如 D:/yk-data` |

**D 类（OctopBot，建议不改）**：2398, 2430, 2445

## 9. 执行补充记录（2026-10-13，B2/B3 执行中发现并处理）

| 项 | 发现 | 处理 |
|---|---|---|
| `public/offline.html` | PWA 离线兜底页为纯静态 HTML（不走 i18n/主题系统）：3 处 "Octop" 文案 + h1/按钮 rose 硬编码配色 —— 原清单遗漏（用户复核发现） | 已重写：文案 → 元控智能，配色 → tech 深蓝（h1 #7b9bfc、按钮 #3a5fe0/#2e4fd0） |
| `index.html` boot splash 加载圈 | 转圈动画硬编码 rose（#e85d75/#f08b9a），是用户打开页面第一眼 | 已改 tech（light #3a5fe0 / dark #4b74fa） |
| `styles/theme-vars.css` :root 默认块 | 17 处 rose CSS 变量（--fn-color-brand 等） | **核实后不改**：boot splash 全屏遮罩期间 --fn-* 变量无可见消费者；React 挂载即设 `data-palette="tech"` 命中 tech 块，零可见影响。避免 17 处上游 CSS 无谓改动 |
| `bootTheme.test.ts` | 直接从 index.html 提取内联脚本 eval 测试 | 已核实：本次只改 `<style>` 色值未动 script，测试不受影响（实测 45/45 通过） |
