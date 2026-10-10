---
# ═══ 身份（全部必填；渲染位置见 references/data-field-guide.md）═══
genericName: 通用名（中文）
brandName: 商品名
englishName: EnglishName
aliases: [商品名, 研发代号, 常见误写]   # 每个别名都是独立搜索需求，≥2 条
manufacturer: 上市许可持有人
drugClass: 药物类别（患者可见处用白话进 labelFacts）
dosageForm: 剂型
spec: 规格（如 80mg×30片/盒）          # 注意：模板不渲染此字段，须在正文露出
route: 给药途径
dosage: 标准剂量（如 每日一次，每次 80mg）
legalStatus: 处方药
insurance: 医保状态                     # 同上，不渲染，写进 labelFacts「医保」条
mechanismOfAction: 作用机制一句话
indications:
  - 逐条获批适应症（各自获批年份写进正文 B 维度）
beforeUse: [用药前必须确认项]           # 模板已不渲染，数据留存
beforeUseRisk: 用药前风险提示            # 同上
# ═══ 首屏说明书要点（患者可见的身份区）═══
labelFacts:
  - term: 正式药名        # term 用白话，不用「通用名/药物类别」
    value: …
  - term: 属于哪类药
    value: …
  - term: 国家批准治什么
    value: …
  - term: 怎么吃
    value: …
  - term: 常见不舒服
    value: …             # 数字必须来自 audit/<slug>/numbers.json 登记值
  - term: 医保
    value: …
# ═══ 首屏直答卡（恰好 6 张；闸门与预算见 card-selection-protocol.md）═══
quickAnswers:
  - question: 患者原话问句（≤26 字，一个疑问点）
    answer: 一句话结论（11–24 字）
    detail: 只解释为什么是这个结论（34–64 字），操作细节撤到正文
    nextStep: 看××、××（与正文当前结构一致）
    source: 到字段级的出处（如 ××说明书（用法用量））
    anchor: 标题前缀（必填；6 卡 6 个不同前缀）
  # …共 6 张
# ═══ 数据层 ═══
updatedAt: YYYY-MM-DD        # 只进 JSON-LD，页面不渲染
status: draft                # 校验通过后改 reviewing；published 必须有真人 reviewedBy，不得自填
author: AI 初稿（内容流水线）
prices:
  - label: 原研
    price: 0
    unit: 元/盒
    note: 年份与口径（数字与 numbers.json 一致）
sources:                      # ≥15 条、一手 ≥5；URL 收录前逐条实测可达
  - label: ××说明书
    url: https://…
    kind: label               # label|guideline|trial|regulatory|price|other
archive: []                   # 化学/监管档案（数据留存，页面暂不渲染）
timeline: []                  # 获批/进医保/基药时间线（同上）
# ═══ 长尾问答（≥15 条；与卡面问句不同字；覆盖别名/停药/忌口/价格/生存期解读）═══
faq:
  - question: …
    answer: 第一句直接回答该问句
# ═══ SEO ═══
titleTag: 通用名 商品名 效果 用法 医保 – 站点名   # 必须含通用名；别名进 titleTag 或 FAQ
metaDescription: 前 78 个中文字符承载全部关键信息，全条 ≤160。
# ═══ 配图：该药分子结构式（公有领域，出处登记 audit 目录）═══
image: /images/drugs/<slug>-structure.svg
imageAlt: <通用名>分子结构式
imageCaption: <通用名>分子结构式 · 图片来源：…（公有领域）
imageWidth: 512
imageHeight: 512
---

<!--
正文骨架：H2 前缀须命中模板 chapters（哪些人适合用/怎么吃/副作用/疗效/要花多少钱/耐药/同类药
+ 药盒里/肝不好/药在身体里/平时要注意）。缺的主题不硬凑；不擅动 [slug].astro。
每个问句标题下第一句 = **加粗直答**。每节末尾固定两件：<p class="section-caveat">定制免责（逐节措辞不同）</p>
和 <p class="source-note">来源：…</p>，顺序固定。
危险信号集中一个 <div class="danger-band">（全页唯一）；主结论数字带 <div class="stat-band">。
全部文案规则见 references/content-depth-standard.md。-->

## 哪些人适合用××？

**一句话直答。**条件、分叉、例外……

<p class="section-caveat">按本节内容定制的免责句。</p>
<p class="source-note">来源：…（S 层级来源与口径）</p>

## 疗效怎么样，生存期能延长多少？

**数字直答（与 numbers.json 同值）。**

<p class="section-caveat">人群统计，不能预测某个人的结局。</p>
<p class="source-note">来源：…</p>

## 要花多少钱，医保能报多少？

### 医保能报多少

### 在哪里能买？

**凭医生处方，在医院药房或定点药房取药。**（正面回答，限制条件退第二句）

### 仿制药能替代吗？

## 怎么吃？忘吃了怎么办？

## 副作用有哪些？怎么应对？

### 需要立即找医生的情况

<div class="danger-band">…全页唯一强对比色块…</div>

## 耐药了怎么办？

## 同类药怎么选？

## 药盒里那张说明书，重点都在这

## 肝不好、肾不好、年纪大、怀孕了怎么办？

## 药在身体里怎么走、怎么起效

## 平时要注意什么、多久复查一次
