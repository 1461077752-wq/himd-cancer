# 数据字段指南（frontmatter → 渲染位置）

schema 定义在 `src/content.config.ts`（zod，`drugs` 集合 = `src/content/drugs/*.md`）。**glob 收集：放进 `src/content/drugs/` 的任意 .md 都会成为页面**，半成品不要放进去（或放但设 `status: draft`）。本文件说明每个字段渲染在哪、哪些字段页面根本不读——填了不渲染的字段等于没写，关键信息必须落在渲染字段或正文里。

## 一、字段 → 渲染位置对照

| 字段 | 渲染位置 | 备注 |
|---|---|---|
| `genericName` | H1、titleTag、JSON-LD Drug.name | 引用最多（8 处），别名的补位责任在它和 FAQ |
| `titleTag` | `<title>`、OG | 必须含 `genericName`；别名/关键卖点放这里，≤ 合理长度 |
| `metaDescription` | meta description | 搜索结果只展示约 78 个中文字符，**前 78 字外全是无效字符**（基准页曾写到 250+） |
| `labelFacts[]` | 首屏 `<dl>`（移动端在 H1 下、桌面在侧栏） | 页面渲染的「说明书要点」。**面向患者的 term 用白话**：正式药名/属于哪类药/国家批准治什么/怎么吃/常见不舒服/医保 |
| `quickAnswers[]` | 首屏 6 张直答卡 | 见 card-selection-protocol.md |
| `faq[]` | 页尾 FAQ + FAQPage JSON-LD | 与卡面合并进结构化数据；去重只按完全同问 |
| `sources[]` | JSON-LD（按 `kind` 分组） | kind ∈ label|guideline|trial|regulatory|price|other；正文节末来源是**手写的 `.source-note` 文本**，不从这里生成 |
| `prices[]` | JSON-LD Offer | {label,price,unit,note?}；**页面可见的价格写在正文表格里**，两处必须同值（numbers.json） |
| `image/imageAlt/imageCaption/imageWidth/imageHeight` | hero 分子结构图 | 见下文图片规则 |
| `status` | 不进产物时即门槛 | 见发布 gate |
| `author/reviewedBy/reviewedAt/updatedAt` | reviewedBy 进 JSON-LD 与审核署名；updatedAt 只进 JSON-LD `lastReviewed` | **页面不渲染更新日期**；无审核人时 `MedicalWebPage.lastReviewed` 会被读成「已医学复核」，属已知风险 |
| `mechanismOfAction/drugClass/indications/dosage/dosageForm/route/legalStatus/manufacturer/englishName/brandName/aliases` | 主要进 JSON-LD | **用户在页面上大多看不到**——需要患者可见的信息必须同时写进 `labelFacts` 或正文，不能只填这些字段（基准页教训：`spec` 与 `insurance` 填了但全站零引用） |
| `beforeUse/beforeUseRisk/archive/timeline` | **模板已不渲染**（浮层与全档案被移除，字段留存） | 数据保留供未来档案页；新页面填了要清楚它们不上页 |

## 二、章节骨架与锚点（模板硬约束）

`src/pages/[slug].astro` 的 `chapters` 数组**硬编码了 11 个标题前缀**（肺癌处方药骨架）：

```
哪些人适合用 / 怎么吃 / 副作用 / 疗效 / 要花多少钱 / 耐药 / 同类药
+ tier:'pro': 药盒里 / 肝不好 / 药在身体里 / 平时要注意
```

- 目录项按前缀 `startsWith` 匹配 H2/H3，**匹配不到就静默消失**——新药若不沿用这套 H2 前缀，目录会缺项且无任何报错。
- 因此：**新药品页的正文 H2/H3 必须命中这 11 个前缀（缺哪个主题就不硬凑，删该卡面引用即可）**；主题确实不同的药种（非肿瘤药没有「耐药」）目前要么改 `chapters`（全站模板，动前想清楚），要么保留前缀并把标题写成该药等价问题。改 `chapters` 属全站级决定，逐药生成时**默认不动模板**。
- 卡面 `anchor` 与导航 target 同理：只要前缀；标题末尾加「？」不影响 slug。
- 目录尾部固定两项 slug：`sources`（页尾来源区）、`trials`（招募区）。
- `hrefOf()` 解析失败会**静默回落到目录第一项**：页面上看不出坏，校验脚本必须硬拦不唯一/不命中的 anchor。

## 三、发布 gate 与状态

- `getStaticPaths` 生产构建只渲染 `status: 'published'`；`reviewing` 仅 dev 可见；`published` 必须有 `reviewedBy`+`reviewedAt`。
- 生成流水线默认停在 `status: reviewing`：**署名审核是人工 gate，不得为通过构建自行置 published 或填假审核人**。
- 路由 = 文件名（`osimertinib.md` → `/osimertinib`，`trailingSlash:'never'` + `build.format:'file'`），slug 用英文通用名小写连字符。

## 四、图片规则

- hero 图 = **该药分子结构式**（用户明确否决过用肺部插画代替药品结构图）。来源 Wikimedia Commons 公有领域（依 PubChem 绘制），SVG 优先。
- 下载前实测 `upload.wikimedia.org` 可达性，许可按 `LicenseShortName` 核对，出处登记 `sources` 审计目录（不进页面）。
- `imageWidth/imageHeight` 必须与实际文件一致（防 CLS）；`imageAlt`、`imageCaption` 必填，图注含来源。
- 禁用药品实物/药盒照片（合规风险）；「药盒图片」需求用规格文字承接。

## 五、已知模板债务（逐药生成时会撞上，勿当 bug 修）

1. 侧栏购药链接 `source_page=/osimertinib` **硬编码**——新药页会带错误归因参数；发现后列入待办，全站改还是逐页参数化属模板级决定，不在单药任务里擅动。
2. `isAvailableGenerically: true` 在 JSON-LD 里硬编码，未读 frontmatter。
3. 站内导航 `/drugs/`、`/diseases/`、`/trials/`、`/about/` 与 robots.txt/sitemap 缺失（快照时点状态，动手前实测最新）。
4. `beforeUse/beforeUseRisk/archive/timeline/spec/insurance/intro` 等字段渲染与否的边界见第一节表——增页前先 `grep 'd\.<字段>' 'src/pages/[slug].astro'` 复核模板没被其他会话改动。
