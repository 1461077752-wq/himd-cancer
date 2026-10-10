# 项目适配：cancer 站（Astro）

目标项目是 `/Users/qiuzijun/workspace/website/himd-web/cancer` 时，本文件是 Skill 的项目适配层。
开工前重读项目权威文档（见文末清单），冲突时按本文件写明的优先级判断。

## 技术栈与命令

- Astro 7 + content collections + Tailwind 4（`@tailwindcss/vite`）。Node ≥ 22.12。
- 开发服务器按项目 `AGENTS.md`：`astro dev --background`，用 `astro dev status` / `astro dev logs` / `astro dev stop` 管理。起新的之前先 `astro dev status`，端口统一维护在上级目录 `dev-ports.json`（键 `cancer`）。
- 构建 `pnpm build`（即 `astro build`）；`trailingSlash: 'never'` + `build.format: 'file'`，产出 `/<slug>` 对应 `dist/<slug>.html`。
- **项目没有 git 仓库**，改动不可回滚。改任何共享文件前先备份副本；用「起点标记→终点标记」做区间替换时，终点必须取紧邻的下一个标记，不能取更外层的 `</div>`（出过整块误删事故）。

## 输出结构

```text
src/content/drugs/<slug>.md                  # 一页一药，全部内容与元数据都在这个文件
src/content/audit/<slug>/serp-keywords.yaml  # 需求证据池（审计数据，不渲染）
src/content/audit/<slug>/numbers.json        # 数字登记表（单一事实源，见 source-hierarchy.md）
src/content/audit/<slug>/skill-run.json      # 调用凭证
public/images/drugs/<slug>-<name>.<ext>      # hero 配图
```

- **`drugs` 集合 loader 是 `glob('**/*.md')`**：`src/content/drugs/` 下任何 `.md` 都会生成一个页面。样稿、片段、审计文件一律不得放进该目录。审计数据放 `src/content/audit/`（无 loader，不参与渲染）。
- slug = 文件名 = 路由：`osimertinib.md` → `/osimertinib`（根级路径，无 `/drugs/` 前缀，对齐线上 himd.com）。
- schema 在 `src/content.config.ts`，逐字段口径见 [data-field-guide.md](data-field-guide.md)。

## 渲染模板的硬约定（`src/pages/[slug].astro`）

- H1、面包屑、首屏、直答卡、FAQ、来源分组、招募块、右栏全部由模板渲染；内容文件**只写正文 Markdown，不写 H1**。
- **页内目录 `chapters` 的分节标题前缀是硬编码的**（哪些人适合用 / 怎么吃 / 副作用 / 疗效 / 要花多少钱 / 耐药 / 同类药 / 药盒里 / 肝不好 / 药在身体里 / 平时要注意），后四节标 `tier: pro`（说明书级）。新药的 H2 若命不中这些前缀，目录项会**静默消失**。此时先输出结构差异与章节方案给用户确认，不要悄悄改共享模板；模板改一处影响所有页面。
- **卡面锚点按「标题文本前缀」匹配**（`slugOf(prefix)`，`h.text.startsWith(prefix)`），匹配范围含 H2/H3。`hrefOf()` 匹配不到时**兜底跳到目录第一项**——不报错但落点错误，校验脚本硬拦。标题末尾加「？」不改变锚点。
- 正文可用组件（样式已在 `src/styles/global.css` 定义）：
  - 每节下第一句：`**加粗直答句**`（结论先行，硬要求）
  - `<p class="section-caveat">` 逐节定制免责（禁止同一句复制多节）
  - `<p class="source-note">来源：…` 每节末整节出处
  - `<div class="danger-band">` 危险信号——**全页唯一强对比色块**
  - `<div class="stat-band">` 数字带（疗效、费用），值/标签/出处三层，出处必含口径
  - `<details><summary>` 折叠块；`<div class="lead-form">` 购药信息收集入口
- 首屏是两套**互斥断点变体**（`<sm` 药名+图两列网格、图在标题右；`≥sm` 原左文右图）。改移动端时桌面必须逐像素不变（项目铁律，改完实测基准几何）。
- JSON-LD 自动生成：Drug / MedicalWebPage / BreadcrumbList / FAQPage。`FAQPage` = quickAnswers（与 FAQ 完全同问句去重）+ faq 全量；卡面与 FAQ 的**近义问句会同时进结构化数据**，写作时控制。
- **模板右栏两个服务入口的 `source_page=/osimertinib` 是硬编码**——新增药品页时若不改模板（应改成 `/${entry.id}`），线索归因会全部记到奥希替尼页。属模板层待办，开工时提醒用户拍板。

## 发布 gate（设计如此，不是 bug）

- `getStaticPaths` 只渲染 `status === 'published'` 的页面（dev 环境全渲染）。
- `reviewing` / `draft` 页面生产构建**没有产物**，只能 dev 预览。AI 不得为「让页面出来」擅自改 status；`published` 必须同时有 `reviewedBy` + `reviewedAt`（真人署名，PRD 硬要求）。
- 页面**不渲染**「内容整理 / 最近更新 / 医学审核」行（已按用户要求移除）；`updatedAt`、审核信息只作审计数据与 JSON-LD。

## 项目权威文档（冲突时读原文，不凭本文件记忆）

| 文档 | 用途 | 状态 |
|---|---|---|
| `docs/drug-page-benchmark-v0.1.md` | 信息厚度 A~S 维度表、可验收标准、三层策略 | 冻结快照 |
| `docs/drug-card-set-v0.1.md` | 卡面四闸门 + 落点唯一性；**以第七节定稿为准**（九卡是推演记录） | 活文档 |
| `docs/autocomplete-audit-osimertinib-v0.1.md` | 下拉词取证方法、需求簇、口径冲突反例 | 冻结快照 |
| `docs/prd-site-v0.2.md`、`docs/site-architecture-v0.2.md` | 产品原则（页面克制三原则、不贩卖焦虑）、SEO/收录 | 现行 |
| `src/content/drugs/osimertinib.md` | 唯一样例页：结构、深度、交互基准 | 基准（`reviewing`） |

冻结快照里的旧措辞（如「能活多久」）不得改写——带日期的证据保持原样；只有活文档随实践更新。

## 已知的全局陷阱

- `site-chrome.css`（HIMD 外壳）曾有全局 `.hidden{display:!important}` 压死 `hidden lg:block` 的事故；从外部项目搬 CSS 必须收窄作用域。
- 判断「浮层压没压住内容」量的是**文字墨迹行盒**（`Range.getClientRects()`），不是盒子边界。
- 间距由 `@tailwindcss/typography` 插件基线控制：`.prose p { margin:1.25em }` 会吃掉子组件手写 margin（em 随字号缩放）。组件内间距优先用 `padding`，改完实测。
- 沙箱里 shell 的 `grep` 不可靠、`rg` 未安装——查文件内容用 Grep 工具或 Python。
- 校验脚本需要 PyYAML；系统 python3 没有。已验证可用：`/Users/qiuzijun/.workbuddy-ai/binaries/python/envs/default/bin/python`（缺时装：`.../bin/pip install pyyaml`）。
