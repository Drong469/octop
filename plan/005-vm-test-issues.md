# 005 · VM 全新环境测试问题清单（D3 实测）

> 2026-10-14 VM 首测发现。全部待批量修复；修复后需重打包并回归。
> 修订：2026-10-14 二稿——补充最大泄露源（octop-assistant 技能）、移除 P3（用户裁定路径无问题）、新增 `.octop` 目录名决策项。
> 修订：2026-10-14 三稿——新增 P3（办公三件套依赖阻塞 + 全局化需求）、P2-4（docx 技能 "Claude" 字样）。
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
