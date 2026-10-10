import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const drugs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/drugs' }),
  schema: z.object({
    genericName: z.string(),
    brandName: z.string(),
    englishName: z.string(),
    aliases: z.array(z.string()),
    manufacturer: z.string(),
    drugClass: z.string(),
    dosageForm: z.string(),
    spec: z.string(),
    route: z.string(),
    dosage: z.string(),
    legalStatus: z.string(),
    insurance: z.string(),
    mechanismOfAction: z.string(),
    indications: z.array(z.string()),
    beforeUse: z.array(z.string()),
    beforeUseRisk: z.string(),
    updatedAt: z.coerce.date(),
    prices: z.array(
      z.object({
        label: z.string(),
        price: z.number(),
        unit: z.string(),
        note: z.string().optional(),
      }),
    ),
    status: z.enum(['draft', 'reviewing', 'published']),
    author: z.string(),
    reviewedBy: z.string().optional(),
    reviewedAt: z.coerce.date().optional(),
    sources: z.array(
      z.object({
        label: z.string(),
        url: z.string().url(),
        /** 来源分层：说明书/监管、指南、临床研究、价格口径、其他 */
        kind: z.enum(['label', 'guideline', 'trial', 'regulatory', 'price', 'other']).optional(),
      }),
    ),
    titleTag: z.string(),
    metaDescription: z.string(),
    image: z.string().optional(),
    imageAlt: z.string().optional(),
    imageCaption: z.string().optional(),
    /** 配图原始像素尺寸，用于预留空间避免布局偏移（未填时模板回退到 1200×800） */
    imageWidth: z.number().optional(),
    imageHeight: z.number().optional(),
    /** 首屏说明书要点：拆成独立条目，药名之下逐项确认，与文末 archive 的全字段区分 */
    labelFacts: z.array(z.object({ term: z.string(), value: z.string() })),
    /**
     * 首屏直答卡：一句结论 + 竖线分隔的补充说明
     * answer 控制在 20 字内，detail 讲清条件与例外
     */
    quickAnswers: z
      .array(
        z.object({
          question: z.string(),
          answer: z.string(),
          /** 枚举型直答：卡面只出四格选项表；answer 不上卡面，供 FAQPage 结构化数据拼完整答案 */
          options: z.array(z.string()).optional(),
          detail: z.string().optional(),
          /** 卡片底部的下一步阅读引导，应与当前问题及锚点内容一一对应 */
          nextStep: z.string(),
          /** 该条结论的来源标注：写清是哪份说明书、哪项研究或哪个政策口径 */
          source: z.string().optional(),
          anchor: z.string().optional(),
        }),
      )
      .optional(),
    /** 化学与监管档案：分子式、CAS、批准文号、执行标准、贮藏等说明书级身份字段 */
    archive: z.array(z.object({ term: z.string(), value: z.string() })).optional(),
    /** 研发与监管时间线：全球/中国获批、进医保、进基药目录等 */
    timeline: z.array(z.object({ date: z.string(), event: z.string() })).optional(),
    faq: z.array(z.object({ question: z.string(), answer: z.string() })),
  }),
});

export const collections = { drugs };
