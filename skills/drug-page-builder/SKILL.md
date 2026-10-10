---
name: drug-page-builder
description: 研究、规划、生成或更新结构化中文药品专题页（单药一页：说明书级专业层 + 患者直答层）。只要用户提出为某个药（通用名、商品名或研发代号，如奥希替尼/泰瑞沙/9291）建药品信息页、批量药品页面、以现有药品页为质量标准生成其他药页，或关心药品页的首屏直答卡、用法用量、不良反应发生率、医保价格、同类药对比、耐药后线、患者长尾问题，就使用本 Skill。HIMD cancer 站点（/Users/qiuzijun/workspace/website/himd-web/cancer）新增药品页时同样用本 Skill 并读 references/project-cancer.md。触发词：药品页、药物页、药品专题、说明书页、直答卡、靶向药页面、drug page。
---

# 药品页构建器

## 定位

为一个药品生成「患者读得懂、专业层查得全、数字对得上」的单页药品专题。质量基准 = cancer 站点奥希替尼页（`src/content/drugs/osimertinib.md` + 三份 docs 契约），不是任何通用百科。

与 disease-page-builder 的分工：疾病页按「病」组织（固定四卡：医院资源/药物/招募/医保），药品页按「药」组织（首屏决策链六卡 + 说明书级专业层）。同一药的信息两侧都会出现时，数字必须同源（各自 audit 目录的登记表口径一致）。

核心信条（每条都有翻车史背书，违反任何一条视为未完成）：

1. **先研究后写作。** 每个事实落到 S1–S5 某层来源；卡面/正文/FAQ/结构化数据是同一数字的多个副本，靠 numbers.json 对齐，不靠记忆。
2. **需求与事实分离。** 下拉词只证明「该回答这个问题」，永远不证明答案内容。
3. **卡面即答案。** 过不了四道闸门的问题不占卡位；装进卡的答案必须能在卡面行动，不点正文也知道怎么办。
4. **诚实的不确定性是加分项。**「说明书没有规定」「官方支付标准未公开」照写；查不到权威口径就停在该处，不编数字。
5. **每一处患者可见文本按「文化程度不高也能读懂」写**，但白话不省略条件、口径、例外；行业常用词（靶点、耐药、复查）不换成自造比喻。

## 参考文件（按需读取，动笔前必读项已标注）

| 文件 | 何时读 |
|---|---|
| [references/project-cancer.md](references/project-cancer.md) | **在 cancer 站点开工前必读**：命令、目录、模板硬约束、工具陷阱 |
| [references/source-hierarchy.md](references/source-hierarchy.md) | **阶段四必读**：S1–S5、冲突裁决、numbers.json 登记 |
| [references/serp-evidence-standard.md](references/serp-evidence-standard.md) | **阶段二必读**：六引擎采集、yaml 规范、需求→结构映射 |
| [references/card-selection-protocol.md](references/card-selection-protocol.md) | **阶段三必读**：四道闸门、落点唯一、字段预算、版式契约 |
| [references/content-depth-standard.md](references/content-depth-standard.md) | **阶段五写作前必读**：A–S 覆盖矩阵、量化验收线、章节写法 |
| [references/data-field-guide.md](references/data-field-guide.md) | **填 frontmatter 前必读**：字段渲染位置、锚点系统、发布 gate |

## 阶段零：确认输入

1. 确认药的身份：通用名（中文）、商品名、英文名、研发代号、常见误写——这五个都是搜索种子，缺一不可。拿不准别名就先查 NMPA/说明书再定。
2. 确认该药是否适用本页型：处方药、长期口服、患者会自己搜索的慢病/肿瘤药最适合；疫苗、注射剂、住院用药的决策链不同，卡面链重排但闸门不变。
3. 在 cancer 站点：`ls src/content/drugs/` 确认无同药在途页面（其他会话可能同时在写）；重读 `docs/` 三份契约与本文件（文档是活文档，快照会过期）。
4. 建审计目录 `src/content/audit/<slug>/`（cancer 站路径，见 project-cancer.md），所有中间研究记录进这里，不进对话。

## 阶段一：确定 slug 与路由

- slug = 英文通用名小写连字符（`osimertinib`、`furmonertinib`…；中国特有药名用其英文注册名，先查站内已有命名惯例）。
- cancer 站路由即文件名：`src/content/drugs/<slug>.md` → `/<slug>`。**glob 集合：文件放进去就成页**，未过校验前保持 `status: draft`。
- titleTag、metaDescription、H1 在阶段一定稿框架、阶段五定稿文字；metaDescription 前 78 个中文字符承载全部关键信息。

## 阶段二：需求取证（SERP）

按 [references/serp-evidence-standard.md](references/serp-evidence-standard.md) 执行：

1. 六引擎、多批种子实拉下拉词（无网络/无法采集时按该文件第四节降级，**禁止凭常识伪造**）。
2. 聚主题簇、算引擎共识度，产出 S/A 级词表。
3. 逐条做「需求 × 拟定结构」对照：✅ 已承接 / 🟡 答非所问风险 / ❌ 缺口；缺口要么进本药正文，要么记 `rejected_queries` 附理由。
4. 结果写 `audit/<slug>/serp-keywords.yaml`（块式），`used_in` 指向卡号/章节/FAQ。

## 阶段三：卡面选品

按 [references/card-selection-protocol.md](references/card-selection-protocol.md) 执行：

1. 候选问题池 = S/A 级词 + 说明书强制告知项（禁忌、停药条件、危险信号）。
2. 逐条过四道闸门（终局性/单一答案/高频/错答有代价）与语气检查；被闸掉的写明去向（正文哪一节/FAQ/拒绝）。
3. 定 6 张卡、按该药决策链排序；**数锚点：6 卡 6 个不同落点**，落点不足先拆正文结构。
4. 产出决策表：候选 × 闸门结果 × 去向，存 `audit/<slug>/`。

## 阶段四：来源研究与数字登记

按 [references/source-hierarchy.md](references/source-hierarchy.md) 执行：

1. 抓 S1 说明书全文（中国口径为主，中美差异逐条记）；S2 医保/目录/获批公告；S3 每项关键研究回原文核 DOI；S4 指南线次与检测路径；S5 价格找政府披露。
2. 来源逐条实测可达性（403/412=反爬可收，NXDOMAIN=死链必换）；≥15 条、一手 ≥5。
3. 建 `audit/<slug>/numbers.json`：所有将出现在 ≥2 处的数字先登记（值、口径、来源、核验日期、副本位置），写作只从登记表取数。
4. 覆盖矩阵（content-depth-standard A–S）逐行标：适用/正文位置/来源层/排除理由。矩阵完成前不写正文。

## 阶段五：生成页面

按 [references/content-depth-standard.md](references/content-depth-standard.md) + [references/data-field-guide.md](references/data-field-guide.md) 执行；从 [assets/page-template.md](assets/page-template.md) 复制起步（模板含注释标明每个字段的去处，交稿前删净全部模板注释）：

1. frontmatter：必填 schema 全给；患者要看的进 `labelFacts`/`quickAnswers`/正文，只进 JSON-LD 的字段不能当露出。
2. 正文：命中模板 `chapters` 前缀的 H2 骨架（缺主题不硬凑，不擅动模板）；**每个问句标题第一句 = 加粗直答**；每节末「定制免责 → 来源」两件；表格克制（三列长文本必折行就改叙述）。
3. FAQ ≥15 条，覆盖别名词、停药、忌口、价格、生存期解读；与卡面不同字。
4. hero 图 = 分子结构式（公有领域，实测可达再下载），出处进 audit。
5. `status: reviewing` 起步；页面无任何渲染日期；内部流程词零出现。

## 阶段六：校验与交付

```bash
python3 skills/drug-page-builder/scripts/validate_drug_pages.py src/content/drugs/<slug>.md
```

（cancer 站用 workbuddy python 环境，见 project-cancer.md 工具陷阱。）

脚本只是结构 gate，人工再过一遍：

- 数字三副本抽查：任选 numbers.json 三条，卡面/正文/FAQ 全对得上
- 锚点全量配对：每个 `anchor` 前缀命中唯一标题；href 与 id 逐对核
- 语气与正面回答：标题与卡面无「能活多久」「买不到」式刺眼/否定开场
- 可读性：任意三节，无医学背景读者能否复述下一步
- 构建 + dev 预览实测 320/390/768/1440 无横向溢出、六卡渲染、目录无缺项
- 交付说明列：生成文件、被闸掉的问题及去向、待人工医学审核项

校验失败 = 未完成。修内容或补证据后重跑，不得只在交付说明里报告错误。`status` 停在 `reviewing` 等署名，不自行 published。

## 批量模式

逐药完成「取证→选卡→来源→页面→校验」全环再下一个，**严格串行**；不先铺所有药的空模板。共享来源（同一指南、同一目录文件）仍要逐药核对适用人群与年份。任一药缺 SERP 或权威证据：只暂停该药（audit 记阻塞原因），继续下一个。批量开头记录契约文档指纹，中途契约被改则后续页面注明用的是新版。
