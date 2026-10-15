# 005 · VM 全新环境测试问题清单（D3 实测）

> 2026-10-14 VM 首测发现。全部待批量修复；修复后需重打包并回归。
> 修订：2026-10-14 二稿——补充最大泄露源（octop-assistant 技能）、移除 P3（用户裁定路径无问题）、新增 `.octop` 目录名决策项。
> 修订：2026-10-14 三稿——新增 P3（办公三件套依赖阻塞 + 全局化需求）、P2-4（docx 技能 "Claude" 字样）。
> 修订：2026-10-15 四稿——新增 P5（云端协同 BETA 彻底隐藏调研：入口全图 + 注释式方案 + 影响评估）。
> 修订：2026-10-15 五稿——新增 P8（首启默认语言英文，P1 漏网）、P9（引导密码文件名 octop-login.txt 泄露）。
> 验收口径（用户约定）：开发机体验 = VM 体验，所有修复先在开发机验收，再打回归 VM。

## P1 · 启动画面泄露（方案已定，待实施）
`desktop/src/assets/index.html` + `assets/octop-mascot-*.webp`（壳自带的独立副本，非 dashboard 那份）：
- [x] 两张红章鱼 webp → 换成用户提供的黏土女孩形象（`C:\Users\Admin\Downloads\image_830453463745123.png`，与 dashboard 欢迎屏同系列）。**加工要求**：①去除两处 AI 水印——左上"AI生成"标签、右下"千问"logo（浅灰底采样填补）✅ 2026-10-14 完成（右下用窄框定点填补，首版检测框误伤人物已修正）；②槽 CSS 去 `aspect-ratio:1` 适配横图（实际 1568×1312）
- [x] `<title>`/加载卡片品牌行/图片 alt 三处 "Octop" → 元控智能 ✅ 2026-10-14
- [x] rose 品牌色（--brand #e85d75 一族 + 进度条）→ tech 深蓝 #3a5fe0 一族（含 select 聚焦光晕 rgba）✅ 2026-10-14
- [x] 首启默认语言 `s.locale || "en"` → `"zh"`（VM 英文系统 hence 显示英文）✅ 2026-10-14（开发机静态预览+回归测试通过；zh 生效待 VM 首启回归确认）

## P2 · 身份泄露（三源，按严重度排序）

### P2-1 · `octop-assistant` 技能（最大单体泄露源，667 行）
`experts/library/general-assistant/skills/octop-assistant/SKILL.md`，随默认专家进入每个新装实例的系统提示词：
- 描述与正文自称"Octop 助手/帮助用户了解 Octop"（VM 模型自称的直接来源）
- 全套上游痕迹：docs.octop.cloud 链接表、github.com/TencentCloud/Octop、腾讯云 COS 安装脚本、LightClaw、"在腾讯云上使用"
- [x] 修复方案 A（推荐）：重写为 `metacontrol-assistant`——产品话术换元控智能，删全部上游链接/COS/LightClaw，**保留 CLI 配置能力**（配模型/通道/定时任务，演示有价值）；同步 4 个 i18n 文件与 2 个测试 ✅ 2026-10-14 完成。落地细节：目录+frontmatter 改名；删入口/文档表/安装三节（69 行）；亮点表去 FnOS/Octop Memory/Harness·Gateway 名；旧 i18n 键 `octop-assistant`/`octop_assistant` 保留但值改新标签（防旧工作区裸 slug），新增 `metacontrol-assistant` 键；3 个测试文件同步。19 个测试通过；身份类字符串（Octop 品牌名/域名/LightClaw/myqcloud/TencentCloud/FnOS/腾讯云）残留扫描清零；`octop` CLI 命令与 `~/.octop` 路径按 P2-3 裁定保留。
- 备选 B：砍产品介绍只留配置能力；备选 C：直接禁用

### P2-2 · 默认专家人格声明缺失
`experts/library/default/AGENTS.md` 无产品身份，模型从环境标识自行推断自称
- [x] 注入人格声明（用户裁定，只要前半段）："你是元控智能（MetaControl AI）的智能助手"；**不加**"不要向用户提及内部目录名/包名"约束句 ✅ 2026-10-14（仅改 L3 首句；无内容断言测试，expert_catalog 15 测试通过；同 P2-1，仅新建 Agent 生效）
- [x] **补充（2026-10-14 开发机实测发现）**：general-assistant 模板路径未覆盖——新建 Agent 走 general-assistant（无 AGENTS.md，仅 SOUL.md），问「你是谁」时无身份来源，从 `.octop` 目录名推断自称 Octop。已在 `general-assistant/SOUL.md`「你是谁」节注入同一句身份声明。注：`USER.md`/`MEMORY.md` 找不到是新工作区正常状态（bootstrap 后创建），非故障。
- [x] **全局身份提示词（2026-10-14，用户提出）**：新增 `infra/agents/global_identity.md`（默认名**小元**，用户可改名；不主动交代工作区/目录），在 `manager.py` harness 配置组装点统一前缀注入——覆盖全部模板/专家/人格，**含 bootstrap 期**（原逻辑首启置 None 正是「你是谁」测试翻车的根源）。team host 独立装配路径未注入（内部协调者，保持边界）。test_agent_manager 3 个旧语义断言更新，109 过。**生效需重打包。**

### P2-3 · 数据目录名 `.octop`（用户裁定：非常困难，暂缓，后续再评估）
- 泄露路径已实证：模型在对话中直接说出工作区路径 `c:\users\28602\.octop\agents\main`（VM 实测）
- 行业惯例（.codex/.claude/.codebuddy）下，`.octop` 读作"产品内部名叫 Octop"
- 工程量初探（2026-10-14，统计中止）：Go 壳 6 处/2 文件；Python 主包 95+ 处/15+ 文件（实际更多）
- 修复选项（存档备查）：甲=只改数据目录默认名（中等工程量）；乙=全套改（fork 级，不推荐）；丙=不改靠人格压制
- 时机备注：0 存量用户时改最划算；与 P2-1（技能重写）有文件重叠
- 状态：**暂缓**——用户裁定"非常困难，到时候再评估"

### P2-4 · docx 技能 "Claude" 字样（待裁定）
`experts/library/office-automation/skills/docx/SKILL.md:326`：编辑文档加批注时写明「使用 "Claude" 作为作者」——上游从 Anthropic 技能翻译的残留，随技能进入每个用到该技能的 Agent。
- [x] 处理：`Claude` → `元控智能`（2026-10-14）。实际波及 14 个文件：docx SKILL.md（10 处，含 9 处 XML 示例）+ docx/xlsx/pptx 三套脚本各 4 个文件（pack/comment/validate/redlining/simplify_redlines 的默认作者名）。ai-coding-coach 与 ACP 列表中的 "Claude Code" 为第三方工具名，保留。office-automation 内 Claude 残留扫描清零。

## 已移除
- ~~原 P3 向导密码提示路径~~（用户裁定：路径没有问题）

## 已核实非问题
- 初始化向导整体流程与界面品牌：✅ 正常
- 引导密码机制：防抢注的安全设计，保留

## P4 · 卸载不彻底：进程未杀导致文件删不掉（2026-10-14 VM 实测）

**现象**：应用运行中执行卸载 → NSIS 报"卸载完成"但只删了 uninstall.exe、开始菜单/桌面快捷方式 3 项；主程序文件全留在 `C:\Program Files\元控智能\`（应用和功能仍显示 223MB）；客户端窗口还活着但输入框无法打字（半卸载残废态）。

**根因**：卸载器没有先终止运行中的应用进程（桌面 exe + octop 后端子进程），运行中文件被锁，NSIS 静默跳过删除。

**修复方向**（待实施）：卸载节开头杀进程（taskkill/nsProcess：桌面 exe、octop 后端 python 进程），删完文件再移除注册表卸载项；可选：提示用户关闭应用。
- [x] `project.nsi`：卸载节 + 安装节开头各加 `nsExec::Exec 'taskkill /F /T /IM "元控智能.exe"'` + Sleep 800——后端 python 是桌面进程子进程，`/T` 连树杀；运行中覆盖安装锁死升级的同类问题一并堵上 ✅ 2026-10-14 **开发机不退进程强卸回归通过：7 项核验全过（进程/安装目录/portable/用户数据保留/HKLM/快捷方式），已提交 0ffc598b**
- [x] **P4b 完成页自动拉起** ✅ 2026-10-14 重装勾选「运行元控智能」成功拉起，已提交
- [x] 卸载器追加清除绿包运行时：读 `OCTOP_HOME` env（兼容自定义部署），默认 `%USERPROFILE%\.octop`，`RMDir /r "<home>\portable"`——`.octop` 下用户数据/备份/设置保留，符合"卸载不清理使用数据"裁定 ✅ 2026-10-14（待回归）
- 踩坑记录：①NSIS 按 ACP 读 .nsi，源文件必须全 ASCII（中文注释/em dash `—`/省略号 `…` 都会 `Bad text encoding`）——新增行一律纯 ASCII；②Git Bash 无 zip/python 时 package.sh 末尾打包失败 → staging 完整，用任意 Python `shutil.make_archive` 补打即可；③safe-delete 护栏拦 `rm -rf` staging（9999 文件）→ 先改名让路重跑
- **P4b · 完成页自动拉起失败（2026-10-14 开发机实测）**：勾选「运行元控智能」未拉起（无崩溃记录、进程未创建），手动启动正常。定性：安装器提权，finish 页直启子进程继承管理员令牌，部分环境静默失败。修复：`MUI_FINISHPAGE_RUN` 改经 `explorer.exe` 中转降权启动（业界标准做法），参数内嵌 `$\"` 转义引号防空格截断。待重装回归验证。
- **重打包完成（2026-10-14）**：`desktop/src/bin/元控智能-desktop-windows-amd64-0.1.0.exe`（214MB）——含 P1 启动画面/P2 防泄露/OfficeCLI（绿包 runtime/officecli.exe）/卸载修复全套；uv.lock 未被重写；安装器版本 0.1.0（pyproject 仍 1.0.2b7，未动 uv.lock）
- 备注：`RMDir /r "$AppData\${PRODUCT_EXECUTABLE}"` 是上游模板残留的 no-op（删的是名为"元控智能.exe"的不存在目录），未动

## P6 · 知识库嵌入模型「已下载但实际编码失败」（2026-10-15 开发机实测，根因已定位待修）

**现象**：下载 bge-small-zh-v1.5 后 UI 显示「模型权重 已下载」，但「实际编码」报 `Could not load model BAAI/bge-small-zh-v1.5 from any source`；文档上传失败；Agent 检索无内容。

**根因（实锤，绿包 Python 复现 + 源码级定位）**：
1. 下载器 `onnx_download.py:hf_cache_snapshot_dir()` 写 HF 缓存 `refs/main` 时**带尾随 `\n`**（`write_text(revision + "\n")`）
2. huggingface_hub 1.33 的 `snapshot_download` 读 refs 时 `f.read()` **不 strip** → commit_hash 变成 `"…\n"` → snapshots 目录名带换行 → 缓存探测静默失败（`LocalEntryNotFoundError`）
3. 转在线下载 → huggingface.co 国内超时（3 次重试约 40s）→ 该模型在 fastembed 0.9.0 中标记 `_deprecated_tar_struct=True`，无 GCS 兜底 → 抛错
4. UI「已下载」是 Octop 自己的 `.onnx` 递归检查（`is_model_downloaded`），与 fastembed 加载标准不一致 → 假绿灯

**波及**：所有经下载器落盘的模型（jina/e5 同样中招）；文档入库失败、检索无内容均为此因（与 WIKI_PATH 无关——数据在知识库 DB，用户查无内容是索引没建起来）。

**修复方案（待实施）**：
1. `onnx_download.py:346`：`refs/main` 写盘**去尾随换行**（一行）
2. 存量自愈：加载路径（`_build_text_embedding` 前）检测 `models--*/refs/main` 带换行的重写为无换行（几行，覆盖已下载用户）
3. 顺带：`start_download` 里 `TextEmbedding(...)` 的 `except ImportError: pass` 会吞掉加载异常假报 DONE——本次不碰（下载成功≠加载成功的状态分离属另一题，记录备查）
- [x] 实施完成 ✅ 2026-10-15：①refs 写盘去换行（对齐 hub 1.33 自身 `write_text(commit_hash)` 无换行惯例）；②`heal_hf_cache_refs()` 通用自愈（扫全部 `models--*/refs/main`，覆盖所有预置模型）挂到 `_build_text_embedding` 加载入口；③测试收紧（refs 断言去 `.strip()`）+ 新增自愈单测，onnx 单测 36 过 3 skip，ruff/mypy 绿。**生效需重打包。**
- [x] **最终候选包已产出（2026-10-15 11:43）**：`desktop/src/bin/元控智能-desktop-windows-amd64-0.1.0.exe`（224MB）——含 P5 云端协同隐藏（前端 bundle 已摇掉 bridge 页资源）+ P6 嵌入修复（已核验进包）+ 浏览器默认网址百度。uv.lock 干净。

**即时缓解（已做）**：用户开发机缓存已手动修复（refs/main 去换行），绿包 Python 实测 `TextEmbedding` 加载成功 dim=512，重启应用后重试上传应可过。
- [ ] 实施代码修复（待用户确认）

## P7 · agent 浏览器实例残留（2026-10-15 开发机发现，低优先级）

**现象**：应用退出后，agent 浏览器工具启动的受控 msedge 实例（`--user-data-dir=...\.octop\browser-profiles\user-1`，headless + 远程调试 9222）不被清理——实测残留 8 个进程，锁死 `browser-profiles` 目录（影响：卸载/迁移 `.octop` 时目录改名失败；日常使用无感）。
**修复方向（暂缓）**：应用退出/harness 停止时回收其启动的浏览器实例——生命周期属上游 octop-browser，记录备查。
- [ ] 待部署阶段评估

## P8 · 首启默认语言实际为英文（P1 漏网，2026-10-15 全新首启实测）

**现象**：全新 `.octop` 首启，启动画面与设置窗为英文（此前显示中文是因为旧数据里有中文偏好，掩盖了默认值问题）。
**根因**：`desktop/src/settings.go:29 defaultSettings()` 返回 `Locale: LocaleEN`——**显式默认非空**，压过前端 `s.locale || "zh"` 的空值兜底（P1 只修了前端空值分支）。
- [x] 修复：`Locale: LocaleEN` → `Locale: LocaleZH`（一行，含注释；用户仍可在设置窗切英文并持久化）✅ 已进工作区，**生效需重打包**。注意：修复后若想看「全新中文首启」，需在重装后删除再生的 `desktop-settings.json`（旧会话会把它写成 en）。
- [x] 已进 14:55 重打包（见 P9 条目）。

## P10 · 上下文使用环形图与模型 1M 窗口脱节（2026-10-15 调研，结论：不改）

**现象**：模型 1M 上下文，环形图分母却是 ~128k（42% = 43k/128k 口径）。
**显示逻辑**：分子 = harness 运行时快照真实分段（准确）；分母 = Agent 配置 `max_input_length`（默认 None → 硬编码 128k，`runtime_limits.py:30`）。模型元数据 `context_window`（resolved.py:43，含 per-model 编辑入口 `ModelListEditor.tsx:617`，预设含 1M）**只用于选型展示**，与环形图刻意解耦。
**不改的理由**：分母兼作历史消息截断预算（注入 `model.profile["max_input_tokens"]`），自动联动模型元数据会隐性改变截断行为（费用/超时风险），且自定义 provider 元数据可能错误缺失。需要更大窗口时在 Agent 高级设置手动调 `max_input_length`（明知的主动决策）。
- [x] 用户拍板：保持上游设计，不改。

## P9 · 引导密码文件名泄露：`octop-login.txt` → `login.txt`（2026-10-15 用户提出）

**现象**：setup 向导明示用户路径 `C:\Users\<user>\octop-login.txt`——用户可见路径带 octop（品牌泄露面，与 `.octop` 目录同类但改名成本低得多）。

**调研结论**：代码唯一定义点 `infra/setup/password_file.py:9 WIZARD_FILE_NAME`，全部读写走 `_password_path()`。波及清单：
- 代码 2 处：`password_file.py:9`（+L1 docstring）、`server.py:600` 黄框文案
- dashboard i18n 4 处：`{zh,en}.json` L624、L4983（**L4983 路径本就写错** `~/.octop/octop-login.txt`，实际在用户主目录——顺带修正）
- 测试 6 文件 ~12 处字符串：test_fnos_docker_persist / test_docker_entrypoint / cli/test_init_cmd / support/auth.py / integration/test_setup_bootstrap / test_docker_image_boot
- 文档：README×2、fnos 配置（字符串替换）；CHANGELOG 不动（历史）

**兼容性**：已完成 setup 的机器无影响（本地桌面流程文件「永久保留」但只在 setup 期读取，密码在 DB）；mid-setup 机器跨版本会断（可接受）。fnos/docker 变体把文件写在数据目录内，同函数覆盖。

- [x] 实施完成 ✅ 2026-10-15：`WIZARD_FILE_NAME` 改 `login.txt`；全仓 38 处同步（server.py 黄框 + 顺带清掉同框 "Octop first-run wizard password" 品牌字样，盒线对齐已补、i18n 4 处、测试 8 文件、docker/fnos 脚本与文档）；CHANGELOG 不动。测试 66 过 70 跳（docker 项跳过），ruff/mypy 绿。
- [x] **重打包完成（14:55）**：`元控智能-desktop-windows-amd64-0.1.0.exe` 224MB——含 P8 默认中文 + P9 login.txt + 此前 P5/P6/网址全部修复。绿包 zip 核验 40504 条目完好，staging 内 `WIZARD_FILE_NAME = "login.txt"` 已确认（踩坑：zip 补打两次被切后台中断产生 70/103MB 半截损坏文件，重跑前台完成后 217.9MB 校验通过）。

## P5 · 云端协同（BETA）彻底隐藏调研（2026-10-15 用户需求，待实施）

**需求**：Octop 自带隐藏开关只能常规隐藏；要求**完全不可见**——任何用户（含 admin）无法通过侧边栏/路由/设置发现功能存在。注释式实现（可逆），不删代码。

**功能内部代号**：`bridge`（侧边栏 key `nav.bridge`，路由 `/bridge`，API `/api/bridge/*`，CLI `octop bridge`）。

### 入口全图（2026-10-15 全仓定位）

**A. 前端可见层（必须处理，5 处）**

| # | 文件 | 位置 | 内容 |
|---|---|---|---|
| A1 | `dashboard/src/layouts/sidebarNav.tsx` | 213-219 | 侧边栏「云端协同」项：**无条件 push**（注释原文 "always available (like personalization)"），所有用户含 admin 可见，带 Beta 徽章，Cloudy 图标 |
| A2 | `dashboard/src/routes/index.tsx` | L10 / L57 / L158 | `BridgePage` 懒加载 import、path→key 映射 `"/bridge": "bridge"`、路由 `<Route path="/bridge">` 三处 |
| A3 | `dashboard/src/pages/Settings/AdvancedSettings/index.tsx` | 69-71 | 旧入口兼容：`?tab=bridge` → `<Navigate to="/bridge">` |
| A4 | `dashboard/src/context/AgentContext.tsx` | 229 | `fetchBridgeShadowAgents()` 把**对端影子专家合并进全局专家列表**——这是比侧边栏更深的织入：专家页、聊天页专家选择器、AgentSelector 都会出现带「对端」徽章的远程专家 |
| A5 | `dashboard/src/utils/permissions.ts` | 191-193 | `/bridge` 权限直通（return null） |

**B. 前端派生层（A4 停拉后自动失效，无需改动）**：`RemoteExpertHint`（AgentSelector/ExpertPickerPopover/SessionList/MinimalAgentSessionNav）、`RemoteDisconnectBanner`（PageShell 216-221）、`PeerOnlyRemoteAlert`、Experts 页 TeamCard/AgentCard/AgentExpertsTable 的「对端」徽章与 `remoteExpert.*` 文案、RemoteDisconnectBanner:35 与 AgentNotReadyScreen:115 的 `navigate("/bridge")` 按钮（无影子专家时不可达）、`utils/remoteExpert.ts`（仍被单测引用，保留）。

**C. 后端层（用户不可见，建议不动）**：`api/app.py` 132-136（bridge_proxy 中间件）/140-145（bind_asgi_app）/242（router 挂载）、`infra/bridge/` 全子系统（manager/transport/peer_auth/http_tunnel/crypto 等 11 文件）、`infra/db/repos/bridge_connections.py` + migration 019、`cli/registry.py:35`（`octop bridge` 命令，开发者面）、`infra/users/preferences.py:33`（nav key，A1 注释后自然失效）、i18n 全部 `nav.bridge`/`BRIDGE_*`/`advancedSettings.bridge`/`pageShell.bridge`/`remoteExpert.*` 键（无引用即不可见；删键会破坏前后端 locale 一致性测试，**保留**）。

### 注释式方案（前端 5 文件，约 15 行）

1. **A1** sidebarNav.tsx：注释 213-219 push 块；`Cloudy` import 仅此处用（L14），一并注释（防 `noUnusedLocals`）
2. **A2** routes/index.tsx：注释 L10 import、L57 映射、L158 路由三处；直接输 `/bridge` 将落入默认 404
3. **A3** AdvancedSettings/index.tsx：注释 69-71 三行
4. **A5** permissions.ts：注释 191-193；函数默认 `return null`（L234）覆盖，**`controlAdminPath.test.ts` 两处 `/bridge → null` 断言仍成立，测试零改动**
5. **A4** AgentContext.tsx：模块级加 `const BRIDGE_HIDDEN = true;`，`fetchBridgeShadowAgents()` 内（`const empty = {...}` 之后）加一行 `if (BRIDGE_HIDDEN) return empty;`——**不碰调用点**，所有 import/函数保持被引用，避免 noUnusedLocals 级联；恢复 = 删 2 行。`AgentContext.test.ts` 只测纯函数投影（projectChatAgentOption/selectEnabledExperts），不碰拉取行为，**测试零改动**

### 影响范围评估

- **改动面**：前端 5 文件约 15 行注释 + 1 常量；后端/DB/i18n/测试 **0 改动**
- **功能损失**：对端专家、跨实例对话、远程浏览器流（`useBrowserStream`/`useBrowserSessionState` 的 bridgeApi 路径自然不可达，本地浏览器不受影响）；后端 bridge manager 仍运行但无 UI 入口、无用户可创建连接（入站需对端凭凭证拨入，无暴露面）
- **服务端加强项（可选，未选）**：如需服务端也禁，注释 `api/app.py` 的 `install_bridge_proxy`/`bind_asgi_app`/router mount 三处——但会牵动 `infra/server.py` 启动链，风险升级，本次不做
- **可逆性**：全注释，git diff 可对照；`BRIDGE_HIDDEN` 单点开关
- **验收点**：admin 登录侧边栏无「云端协同」；直输 `/bridge` 404；专家列表/聊天选择器无「对端」专家；`npx tsc -b` + 前端单测绿

- [x] 实施上述 5 处注释 ✅ 2026-10-15（A1 侧边栏+Cloudy import、A2 路由三处、A3 旧 tab 跳转、A4 AgentContext `BRIDGE_HIDDEN` 早退、A5 权限直通；注释均带恢复说明。验证：`tsc -b` 绿 + 相关前端单测 5 文件 34 用例全过（Node 24）。**生效需重打包**。）
- [x] 补充确认（用户问）：「自定义导航」编辑器同源覆盖——`Sidebar.tsx:398 buildNavSections` 同时喂侧边栏与 customizer catalog，源头注释后编辑器列表同样不含云端协同；旧保存布局里的 bridge 摆放记录在 `sectionsFromLayout` 渲染时被 catalog 过滤，不会复活，编辑器也不显示 preserved 项。

## P3 · 办公三件套在 VM 上不可用（2026-10-14 VM 实测）

**现象**：VM 上让 Agent 生成 Word，技能按设计「报告依赖缺失后停止」——根因是缺 Node/npm。
**根因**：内置 docx/pptx/xlsx 技能（上游 Anthropic 技能翻译版）依赖外部工具，绿包一样都没带：

| 操作 | 依赖 | VM/绿包现状 |
|------|------|------------|
| 创建新文档 | Node.js（docx-js / pptxgenjs） | ❌ 阻塞 |
| .doc 转换 / 修订接受 / 导出 PDF | LibreOffice | ❌ 未装 |
| 读取/提取文本 | pandoc | ⚠️ 有解压 XML 的 Python 兜底 |
| 编辑现有文档 | 纯 Python（解压→改 XML→重打包） | ✅ 可用 |

与「无脑下一步」产品目标直接冲突：演示机上三件套只有「编辑已有文档」可用。

**候选方案**（2026-10-14 调研，待用户拍板）：
- A（AI 推荐）：集成 [OfficeCLI](https://github.com/iOfficeAI/OfficeCli)——单文件自包含二进制（.NET 已嵌入），零运行时依赖（无需 Node/Python/LibreOffice），三件套读写创建全覆盖且功能更强（350+ 公式求值、PPT 动画、模板占位符、渲染预览自修正），核心离线，Apache 2.0 可商用，自动更新可关（`OFFICECLI_SKIP_UPDATE=1`）。集成 = 绿包塞一个 exe + PATH + 薄技能文件。代价：安装包增重（几十 MB 起）。
- B：改 SKILL.md 让创建路径走 python-docx（绿包现成有 Python）。零增重，功能上限低。
- C：维持原共识，部署阶段再评估。

**新需求（用户提出）**：三件套能力应「每个模型都自带」，不绑定专家。已查清机制（2026-10-14）：
- 专家库 `skills/` 只是**创建 Agent 时的种子复制**，之后无运行时关联；改专家库只影响新建 Agent，做不到全局。
- 现成全局通道 = **`infra/agents/builtin_skills/`**：放进去的技能会在每个 Agent workspace 同步（`sync_octop_builtin_skills`，`manager.py:3006`），真·所有 Agent 自带，随 wheel 分发。这是正解路径。
- 备选：Skill Package（`~/.octop/skill-packages/`，`skills_dir` 挂载）也可复用，但需逐 Agent 挂载且仅限 local/filesystem 后端。

**决策（2026-10-14 用户拍板）**：
- ① **方案 A**（OfficeCLI）：✅ 已定。OfficeCLI 二进制由 AI 负责拉取，用户不动手。
- ② **全局化走 builtin_skills**：✅ 已定（与 A 配套）——技能放 `infra/agents/builtin_skills/`，每个 Agent 自带；OfficeCLI exe 随绿包分发并进 PATH。
- ③ docx 技能 "Claude" 字样：✅ 已完成（见 P2-4）。
- 执行节奏：用户要求一件件来，每步汇报确认后再继续。

**第 1 步 · 二进制拉取与冒烟 ✅（2026-10-14）**：
- v1.0.157 `officecli-win-x64.exe`（33.5MB 单文件）→ 暂存 `.artifacts/officecli/`（git 已忽略），SHA256 与官方 SHA256SUMS 一致
- 冒烟通过：`--version`、`create`（空白 docx）、`add`（中文段落写入）、`query`（中文读回无损）、`validate`（OpenXML 零错误）、`close`（驻留进程释放）
- 后续步骤：~~②技能文件移植~~ → ~~③绿包塞 exe + PATH~~ → ④开发机新建 Agent 实测（需重打包后随真实链路验） → ⑤VM 回归

**第 3 步 · 绿包集成 ✅（2026-10-14）**：
- 关键机制：`templates/launch.py` 启动时把 `runtime/` 前插到 PATH 且 agent shell 继承 → **exe 放 `runtime/` 即全链路可达，零代码**
- `package.sh`：Windows 打包时从 `.artifacts/officecli/officecli.exe`（可用 `OFFICECLI_WIN_BIN` 覆盖）复制到 `${staging}/runtime/officecli.exe`；二进制缺失时 WARNING 跳过不阻塞打包；`bash -n` 语法通过
- `templates/start.bat`：`set "OFFICECLI_SKIP_UPDATE=1"` 关自动更新检查（内网交付不外联），随进程 env 传入 agent shell

**第 2 步 · 技能文件移植 ✅（2026-10-14）**：
- 新增 `infra/agents/builtin_skills/office-suite/SKILL.md`：教 agent 调 officecli（前置检查 --version、路径寻址模型、常用命令表、batch/merge 真实语法已实测核实、`officecli help` 为 schema 权威来源、禁跑 install/skills/mcp/watch/open 子命令）
- office-automation 降级：docx/pptx 两个 SKILL.md 的 description 尾部 + 前置依赖加分流句——创建改走 office-suite，自身聚焦编辑分析现有文档；**xlsx 未动**（openpyxl 纯 Python 创建路径在绿包可用，无冲突）
- 测试：`test_octop_builtin_skills.py` 两处技能清单断言更新为 `["office-suite", "skill-manager"]`；builtin+expert_catalog+i18n 共 103 测试全过
