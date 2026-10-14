---
name: office-suite
description: 创建、读取、编辑 Word (.docx)、Excel (.xlsx)、PowerPoint (.pptx) 文档时必须使用此技能。通过 officecli 命令行零依赖完成：新建文档、添加/修改/删除段落、表格、图片、形状、幻灯片，按路径精确定位元素，模板占位符批量填充，OpenXML 校验。触发场景：生成报告/表格/演示文稿、修改现有文档、查询文档结构、模板合并。深度 XML 级修订与批注编辑用 office-automation 专家技能。
metadata:
  octop:
    emoji: "📊"
    label:
      zh: "Office 文档"
      en: "Office Documents"
    summary:
      zh: "用 officecli 创建、读取、编辑 Word/Excel/PPT 文档，零外部依赖。"
      en: "Create, read, and edit Word/Excel/PPT documents via officecli with zero external dependencies."
---

# Office 文档（officecli）

## 前置

- 先执行 `officecli --version` 确认工具在 PATH 中可用；缺失时报告依赖问题并停止，**不要**尝试安装。
- 只使用本文档列出的子命令；**不要**运行 `officecli install`、`skills`、`mcp`、`watch`、`open`。

## 核心模型

文档是元素树，所有操作用路径寻址：

| 格式 | 路径示例 |
|------|----------|
| docx | `/body/p[1]`、`/body/table[1]/table-row[2]/table-cell[1]` |
| xlsx | `/sheet[1]/row[1]/cell[1]` |
| pptx | `/slide[1]/shape[1]` |

元素类型与属性不确定时查 schema（权威来源，**不要凭记忆编造**）：

```bash
officecli help docx              # 列出全部元素
officecli help docx add p        # 查看某元素支持的属性
officecli help all --jsonl       # 全量 schema
```

## 常用操作（输出建议加 --json）

```bash
# 新建（拒绝覆盖已存在文件；确认后才能加 --force）
officecli create report.docx --json

# 查看结构与内容
officecli get doc.docx "/" --json
officecli query doc.docx p --json          # CSS 式选择器

# 增删改（\n 开新段落，\v 段内换行）
officecli add doc.docx /body --type p --prop "text=第一段" --json
officecli set doc.docx "/body/p[1]" --prop "text=修改后的文本" --json
officecli remove doc.docx "/body/p[2]" --json
officecli move doc.docx "/body/p[2]" --to "/body/p[1]" --json

# 批量修改（JSON 数组一次提交，替代多条单命令）
officecli batch doc.docx --commands '[
  {"command":"add","parent":"/body","type":"p","props":{"text":"标题"}},
  {"command":"set","path":"/body/p[1]","props":{"bold":"true"}}
]' --json

# 模板填充（模板里写 {{key}} 占位符，一次设计 N 次生成）
officecli merge template.docx output.docx --data '{"name":"张三","date":"2026-10-14"}' --json

# 校验与预览
officecli validate doc.docx --json         # 写完必跑；失败不要盲目重试
officecli view doc.docx html --json        # 渲染结果，可自查排版

# 查看原始 XML（调试兜底）
officecli raw doc.docx
```

## 与其他技能的分工

- **本技能**：创建新文档、结构化读写、批量修改、模板填充——零外部依赖，**优先使用**。
- **office-automation 专家技能**：现有文档的深度 XML 编辑（修订追踪、批注、解压改 XML 重打包）。

## 行为规则

1. 变更前先 `get`/`query` 展示现状；变更后 `validate`。
2. `create`/`merge` 默认拒绝覆盖；覆盖前必须向用户确认。
3. 表格、图片、图表等复杂元素先查 `officecli help <格式> <元素>` 再动手。
