# 003 · 客户端阶段：演示版安装包（D1–D4）

> 状态：待用户确认后开工。审问方式：grill-with-docs（2026-10-14）。
> 前置文档：`plan/001-web-brand-replace.md`（第一阶段，已完成并提交）、`docs/adr/0001-desktop-product-identity-placeholder.md`、`CONTEXT.md`（演示版/瘦壳术语）。

## 1. 审问共识（决策记录）

| # | 决策点 | 结论 |
|---|---|---|
| D1 | 演示版完成定义 | **空数据起步**；验收 = 全新机器五步全通：安装（无脑下一步）→ 打开（自动起服务）→ 首启向导建账号 → 配模型 Key → 发消息并收到产出 |
| D2 | 壳品牌 | 图标从 openclaw 母版（`D:\openclaw\openclaw\img\LOGO.png`）加工；productName=`元控智能`；companyName=`MetaControl AI`；productIdentifier=`com.metacontrol.ai`（ADR-0001：有存量装机后冻结） |
| D3 | 安装域 | `WAILS_INSTALL_SCOPE=user`（%LOCALAPPDATA%，免管理员，无 UAC 弹窗） |
| D4 | 版本号 | 安装包独立版本线 `0.1.0`（打包参数传入）；pyproject.toml 版本**不动**（避免影响 pip/上游更新逻辑），两套版本号并存 |
| D5 | 功能裁剪 | **不裁剪**。云端协同(BETA)已查证：实例互联功能，不配置即静默空状态，零外部依赖零风险 |
| D6 | 交付配套 | **不带任何说明书**，Key 领导自配；产品必须自解释（对齐 WorkBuddy 哲学）。卸载保留 `~\.octop` 数据属正常设计，不特别说明 |
| D7 | 形态路线 | 演示版=胖壳产线（现在）；瘦壳=部署产线（服务器到货后启动，预估 1~3 天，见 CONTEXT.md 术语）；同一代码两条产线互不阻塞 |

## 2. 执行阶段

### D1 · 工具链 + 壳跑通（预计半天）
1. 安装 Go 1.25.x（winget/官网安装包；配 `GOPROXY=https://goproxy.cn,direct`）
2. `go install github.com/wailsapp/wails/v3/cmd/wails3@v3.0.0-beta.13`
3. 安装 NSIS 3.11（官网下载，装完确认 `makensis.exe` 在 PATH）
4. 开发模式验证：`cd desktop/src && OCTOP_DESKTOP_URL=http://127.0.0.1:8088 wails3 dev`（连已运行的本地 Octop 服务，出现客户端窗口即通）

> 每一步安装都会先列出清单征求确认（动系统环境的操作需用户批准）。

### D2 · 绿包构建 + 完整打包（预计半天）✅ 2026-10-14 完成
逐步执行 CI 配方（`.github/workflows/octop-desktop.yml` 的 windows-amd64 路径），在 Git Bash 中：
1. 前端构建（Node 24 前置 PATH，`npm run build` → `src/octop/dashboard`）
2. `bash desktop/portable/bootstrap-runtime.sh windows-amd64`（下载便携 CPython 3.12.12，需代理；PBS_BASE_URL 可配）
3. `bash desktop/portable/package.sh windows-amd64`（`uv export --frozen` 装依赖 → 绿包 zip → verify_imports.py 冒烟）
4. `cd desktop/src && wails3 task package ARCH=amd64 VERSION=0.1.0 PORTABLE_ZIP=../portable/release/Octop-portable-windows-amd64-<版本>.zip`
5. 产物：`desktop/src/bin/Octop-desktop-windows-amd64-0.1.0.exe`（NSIS 安装器）

**执行记录（可复现要点）**：
- 便携 CPython 默认走 **npmmirror 淘宝镜像**（`_common.sh:17`），无需代理，实测 2 秒下完；
- `package.sh` 打 zip 时 Git Bash 无 `zip` 命令、回退 `python` 会命中 Windows 商店假别名报错 → staging 此时已完整，用系统 Python `shutil.make_archive` 直接补齐 zip 即可；
- 冒烟校验用绿包自带 Python 跑 `verify_imports.py` → OK；
- winget 安装的 NSIS **不自动进 PATH** → 命令前置 `${env:ProgramFiles(x86)}\NSIS`；
- 绿包 zip 的文件名版本取自 pyproject（`…-1.0.2b7.zip`），安装器版本取 `VERSION=` 参数（0.1.0）——两者独立，符合 D4 版本号决策；
- 产物：`bin/Octop-desktop-windows-amd64-0.1.0.exe`（203MB，内嵌 206MB 绿包）。

### D4 · 壳品牌替换（预计半天，提前于实测）
| 文件 | 改动 |
|---|---|
| `desktop/src/build/config.yml` | productName=元控智能、companyName=MetaControl AI、productIdentifier=com.metacontrol.ai、description/copyright 同步 |
| `desktop/src/build/appicon.png` | LOGO 母版 → 512²（PIL 加工） |
| `desktop/src/assets/tray-icon.png` | 同母版适配（全出血） |
| `desktop/src/build/windows/icon.ico` | 由 512² 转多尺寸 ico |
| `desktop/src/desktop_copy.go` | 壳内文案 "Octop" → "元控智能"（连接中/启动中等状态文案） |
| 窗口标题 | 执行时查证 main.go 中窗口 title 定义并同步 |

改完重打包，产物为品牌化安装包。

### D3 · 实测（预计半天）
在本机（干净用户目录最佳）执行验收：
- [ ] 双击安装：无 UAC、一路下一步、完成页自动启动
- [ ] 首启：解压进度画面 → 服务就绪 → 首启向导（建账号）
- [ ] 配 MIMO Key → 对话 → 产出一份文件
- [ ] 托盘图标/菜单正常；窗口/任务栏图标为元控智能
- [ ] 开始菜单/桌面快捷方式存在；卸载列表显示"元控智能 0.1.0"
- [ ] 卸载：程序移除、`~\.octop` 保留
- [ ] 重装：数据仍在，直接进入登录页

## 3. 收口与上游策略
- 本阶段改动以 `desktop/` 为主（config.yml、desktop_copy.go、图标、NSIS scope 变量）；`dashboard/` 仅允许品牌防泄露类小改（见 3.1），不触碰 `src/` 与 `pyproject.toml`；
- 上游 `desktop/` 也在活跃迭代，品牌文件的冲突预期与 locales 同级（机械、可重放）；绿色打包脚本尽量不改，必须改时单独提交便于 cherry-pick；
- 提交节奏：D1 环境不产生代码提交；D2 若有脚本微调单独提交；D4 品牌一个提交；实测通过后推送 origin + gitee。

### 3.1 品牌防泄露（2026-10-14 完成，D1 期间发现并处理）
壳测试时发现版本号与更新页暴露上游痕迹，已注释式移除（用户要求：不删除，便于恢复）：
- `layouts/Sidebar.tsx` / `layouts/Header.tsx`：版本徽章（`AppVersionBadge`/`CurrentVersionBadge`）渲染与 import 注释掉；顺带把两处图片 `alt` 从 "Octop" 改为 "元控智能"；
- `Settings/AdvancedSettings/index.tsx`：「应用更新」tab 的注册/渲染/URL 解析/import 注释掉；`UpdateConfig.tsx` 文件保留不引用——内含腾讯 COS 安装脚本链接，摇树剔除后**不进构建产物**；
- `components/AvatarDropdown.tsx`（D4 后补）：头像菜单「项目地址」（腾讯仓库直链）、「帮助与反馈」（上游官网）、「检查更新」（指向已移除的更新页）三个入口注释掉，连带常量与 import；
- 验证：tsc 通过、Header 测试 3/3、前端已重建；
- 遗留备忘（部署阶段处理）：后端自动检查更新的逻辑仍在（当前最新=当前版本所以静默），上游发新版后可能推送"新版本可用"通知，届时查后端关闭自动检查的配置项。

## 4. 风险清单
| 风险 | 等级 | 应对 |
|---|---|---|
| Wails v3 为 beta | 低 | 上游钉死 beta.13 且 CI 持续构建；遇问题以 CI 日志为准对齐 |
| Windows 本地 bash 脚本杂音（路径/工具） | 中 | 逐步执行、以 CI 配方为权威；卡住改用 GitHub Actions 单平台兜底（windows-amd64） |
| 便携 CPython 下载走 GitHub | 低 | 系统代理 127.0.0.1:7897 已配（git 层）；浏览器层下载用系统代理 |
| 绿包体积（数百 MB） | 信息 | 演示场景正常；瘦壳时代归零 |
| 领导机器无法出公网 | 低 | 模型 Key 需联网；内网无外网场景等服务器+本地模型 |

## 5. 完成定义
本阶段完成 = D3 清单全绿 + 品牌化 `元控智能-desktop-windows-amd64-0.1.0.exe`（名以实际产物为准）可交付。
