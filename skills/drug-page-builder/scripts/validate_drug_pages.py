#!/usr/bin/env python3
"""Validate the structural contract for a generated drug page.

Usage:
    python3 validate_drug_pages.py src/content/drugs/<slug>.md [--audit-dir DIR]

Errors fail the build gate (exit 1); warnings are advisory. The audit
directory defaults to src/content/audit/<slug> resolved from the page path.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "需要 PyYAML：/Users/qiuzijun/.workbuddy-ai/binaries/python/envs/default/bin/pip install pyyaml"
    )
    sys.exit(2)

REQUIRED_STR = {
    "genericName", "brandName", "englishName", "manufacturer", "drugClass",
    "dosageForm", "spec", "route", "dosage", "legalStatus", "insurance",
    "mechanismOfAction", "beforeUseRisk", "titleTag", "metaDescription", "author",
}
REQUIRED_LIST = {
    "aliases", "indications", "beforeUse", "prices", "sources", "labelFacts", "faq",
}
PRIMARY_KINDS = {"label", "guideline", "trial", "regulatory"}
STATUS_ENUM = {"draft", "reviewing", "published"}

CARD_QUESTION_MAX = 26
CARD_ANSWER_MAX = 28
CARD_DETAIL_MIN = 20
CARD_DETAIL_MAX = 80
FAQ_MIN = 15
SOURCES_MIN = 15
PRIMARY_MIN = 5
META_VISIBLE_CJK = 78
META_HARD_MAX = 160

JARGON = re.compile(
    r"stat-band|danger-band|section-caveat|source-note|labelFacts|quickAnswers"
    r"|nextStep|serp_evidence|evidence_id|numbers\.json|SERP|下拉词|槽位|引擎共识"
    r"|证据表|待替换|占位图|审计|流水线"
)
RENDERED_DATES = re.compile(r"更新日期|最后更新|核验日期")

NUM_UNIT = r"(?:%|％|个月|元|万)"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    return (match.group(1), match.group(2)) if match else (None, text)


def norm(text: str) -> str:
    return re.sub(r"[\s？?。，,！!]+", "", text or "")


def cn_len(text: str) -> int:
    return len(text or "")


def headings(body: str) -> list[tuple[int, str]]:
    found = []
    for line in body.splitlines():
        match = re.match(r"^(#{1,3})\s+(.*)$", line)
        if match:
            found.append((len(match.group(1)), match.group(2).strip()))
    return found


def visible_strings(data: dict) -> str:
    parts: list[str] = [data.get("titleTag", ""), data.get("metaDescription", "")]
    for row in data.get("labelFacts", []) or []:
        if isinstance(row, dict):
            parts.extend([str(row.get("term", "")), str(row.get("value", ""))])
    for card in data.get("quickAnswers", []) or []:
        if isinstance(card, dict):
            parts.extend(str(card.get(key, "")) for key in
                          ("question", "answer", "detail", "nextStep", "source"))
    for item in data.get("faq", []) or []:
        if isinstance(item, dict):
            parts.extend([str(item.get("question", "")), str(item.get("answer", ""))])
    return "\n".join(parts)


def validate(page: Path, audit_dir: Path | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = page.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(text)
    if fm_raw is None:
        return [f"{page.name}: missing YAML frontmatter"], warnings

    try:
        data = yaml.safe_load(fm_raw)
    except yaml.YAMLError as exc:
        return [f"{page.name}: invalid frontmatter YAML: {exc}"], warnings
    if not isinstance(data, dict):
        return [f"{page.name}: frontmatter must be a mapping"], warnings

    slug = page.stem
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        errors.append(f"slug「{slug}」不是小写连字符格式")

    for key in sorted(REQUIRED_STR):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key}: required non-empty string missing")
    for key in sorted(REQUIRED_LIST):
        value = data.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"{key}: required non-empty list missing")

    status = data.get("status")
    if status not in STATUS_ENUM:
        errors.append(f"status must be one of {sorted(STATUS_ENUM)}")
    elif status == "published":
        for key in ("reviewedBy", "reviewedAt"):
            if not data.get(key):
                errors.append(f"status=published 要求 {key} 非空（署名 gate，不得造假）")

    generic = str(data.get("genericName", ""))
    title_tag = str(data.get("titleTag", ""))
    if generic and generic not in title_tag:
        errors.append("titleTag 必须包含通用名")
    meta = str(data.get("metaDescription", ""))
    if cn_len(meta) > META_HARD_MAX:
        errors.append(f"metaDescription {cn_len(meta)} 字，超过 {META_HARD_MAX} 硬上限")
    elif cn_len(meta) > META_VISIBLE_CJK:
        warnings.append(
            f"metaDescription {cn_len(meta)} 字：搜索结果只展示约 {META_VISIBLE_CJK} 个中文字符，"
            "关键信息必须落在前 78 字内"
        )

    aliases = [str(a) for a in data.get("aliases", []) or [] if str(a).strip()]
    if len(aliases) < 2:
        warnings.append("aliases 少于 2 条：商品名/研发代号/常见误写都是独立搜索需求")

    body_headings = headings(body)
    if any(depth == 1 for depth, _ in body_headings):
        errors.append("正文不得写 H1（页面标题由 frontmatter/模板承担）")
    h2_titles = [t for d, t in body_headings if d == 2]
    h3_titles = [t for d, t in body_headings if d == 3]
    all_titles = [t for _, t in body_headings if _ >= 2]

    brand_hits = [
        name for name in [str(data.get("brandName", "")), str(data.get("englishName", "")), *aliases]
        if name and name in (title_tag + visible_strings(data) + body)
    ]
    if not brand_hits:
        errors.append("商品名/英文名/别名在 titleTag、labelFacts、FAQ 与正文中零露出（读者无法认领搜索词）")

    tables = len(re.findall(r"(?m)^\s*\|[\s:|-]*-{3,}[\s:|-]*\|\s*$", body))
    if tables < 6:
        warnings.append(f"正文表格 {tables} 个（量化线 ≥6；改叙述的表不算缺，但需有登记理由）")
    if len(h2_titles) < 8:
        warnings.append(f"正文 H2 仅 {len(h2_titles)} 节，核对覆盖矩阵是否有整层缺失")
    source_notes = body.count("来源：")
    if source_notes < len(h2_titles):
        errors.append(f"节末来源 {source_notes} 处 < H2 节数 {len(h2_titles)}（每节必须有 source-note）")

    qa = data.get("quickAnswers")
    if not isinstance(qa, list) or not qa:
        errors.append("quickAnswers 缺失：首屏直答卡是药品页硬要求")
        qa = []
    if qa and len(qa) != 6:
        errors.append(f"quickAnswers 必须 6 张，当前 {len(qa)} 张")
    anchors: list[str] = []
    for index, card in enumerate(qa):
        if not isinstance(card, dict):
            errors.append(f"quickAnswers[{index}] 必须是对象")
            continue
        question = str(card.get("question", "")).strip()
        answer = str(card.get("answer", "")).strip()
        detail = str(card.get("detail", "") or "").strip()
        next_step = str(card.get("nextStep", "") or "").strip()
        source = str(card.get("source", "") or "").strip()
        anchor = str(card.get("anchor", "") or "").strip()
        tag = f"quickAnswers[{index}]「{question[:12]}」"
        if not question:
            errors.append(f"{tag}: question 必填")
        elif cn_len(question) > CARD_QUESTION_MAX:
            errors.append(f"{tag}: question {cn_len(question)} 字，超过 {CARD_QUESTION_MAX}")
        elif "？" not in question and "?" not in question:
            warnings.append(f"{tag}: question 不是问句")
        if not answer:
            errors.append(f"{tag}: answer 必填（普通卡是卡面结论；枚举卡不上卡面，供 FAQPage 拼完整答案）")
        elif cn_len(answer) > CARD_ANSWER_MAX:
            errors.append(f"{tag}: answer {cn_len(answer)} 字，超过 {CARD_ANSWER_MAX}（结论必须一句）")
        options = card.get("options") or []
        if options:
            if len(options) > 8:
                errors.append(f"{tag}: 枚举卡选项 {len(options)} 项 > 8，卡面四格表格装不下，改成正文列表")
            elif len(options) % 2:
                warnings.append(f"{tag}: 枚举卡选项 {len(options)} 项为奇数，两列网格会留半格空")
        if not detail:
            errors.append(f"{tag}: detail 必填（解释为什么是这个结论）")
        elif cn_len(detail) < CARD_DETAIL_MIN:
            errors.append(f"{tag}: detail {cn_len(detail)} 字 < {CARD_DETAIL_MIN}，解释不成立")
        elif cn_len(detail) > CARD_DETAIL_MAX:
            if cn_len(detail) > 90:
                errors.append(f"{tag}: detail {cn_len(detail)} 字 > 90（契约 34–64，只答为什么是结论）")
            else:
                warnings.append(
                    f"{tag}: detail {cn_len(detail)} 字，超契约 34–64 档——"
                    "操作细节应撤到正文，且撤出前核对正文有完整版本兜底"
                )
        if not next_step:
            errors.append(f"{tag}: nextStep 必填")
        if not source:
            errors.append(f"{tag}: source 必填（到字段级出处）")
        if not anchor:
            errors.append(f"{tag}: anchor 必填（标题前缀）")
        else:
            anchors.append(anchor)
            matches = [t for t in all_titles if t.startswith(anchor)]
            if not matches:
                errors.append(
                    f"{tag}: anchor「{anchor}」解析不到任何标题"
                    "（模板会静默回落到目录第一项，页面看不出坏）"
                )
            elif len(matches) > 1:
                warnings.append(f"{tag}: anchor「{anchor}」命中多个标题：{'、'.join(matches)}")
    duplicates = sorted({a for a in anchors if anchors.count(a) > 1})
    if duplicates:
        errors.append(f"卡面落点重复（落点唯一性）：{'、'.join(duplicates)}")

    faq = data.get("faq", []) or []
    if len(faq) < FAQ_MIN:
        errors.append(f"FAQ {len(faq)} 条 < {FAQ_MIN} 条量化线")
    q_norms = [norm(str(item.get("question", ""))) for item in faq if isinstance(item, dict)]
    dup_faq = sorted({q for q in q_norms if q and q_norms.count(q) > 1})
    if dup_faq:
        errors.append(f"FAQ 问题重复：{'、'.join(dup_faq)}")
    qa_questions = {norm(str(card.get("question", ""))) for card in qa if isinstance(card, dict)}
    same = sorted(set(q_norms) & qa_questions)
    if same:
        errors.append(f"FAQ 与卡面问句完全同问（FAQPage 会重复收录）：{'、'.join(same)}")

    sources = data.get("sources", []) or []
    if len(sources) < SOURCES_MIN:
        errors.append(f"来源 {len(sources)} 条 < {SOURCES_MIN} 条量化线")
    kinds = [str(s.get("kind", "")) for s in sources if isinstance(s, dict)]
    primary = sum(1 for k in kinds if k in PRIMARY_KINDS)
    if kinds and any(kinds):
        if primary < PRIMARY_MIN:
            errors.append(f"一手来源 {primary} 条 < {PRIMARY_MIN}（说明书/指南/研究/监管）")
    else:
        warnings.append("sources[].kind 全部缺省，无法核对一手来源占比")
    urls = [str(s.get("url", "")) for s in sources if isinstance(s, dict)]
    bad_urls = [u for u in urls if not u.startswith(("http://", "https://"))]
    if bad_urls:
        errors.append(f"来源 URL 非法：{bad_urls[:3]}")
    dup_urls = sorted({u for u in urls if u and urls.count(u) > 1})
    for url in dup_urls:
        warnings.append(f"来源 URL 重复：{url}")

    # 只剥真正的标签：正文里的「<18 岁」这类数学符号不能被当成标签起点，
    # 否则会把两个符号之间的整段文字从检查中抹掉。
    haystack = re.sub(r"</?[a-zA-Z][^<>]*>", " ", body) + "\n" + visible_strings(data)
    jargon_hits = sorted(set(JARGON.findall(haystack)))
    if jargon_hits:
        errors.append(f"患者可见文本出现内部流程词：{'、'.join(jargon_hits)}")
    date_hits = sorted(set(RENDERED_DATES.findall(body)))
    if date_hits:
        errors.append(f"正文渲染了日期字段：{'、'.join(date_hits)}（页面不渲染更新日期）")

    prices = data.get("prices", []) or []
    for item in prices:
        if not isinstance(item, dict):
            continue
        price = item.get("price")
        if not isinstance(price, (int, float)):
            errors.append(f"prices「{item.get('label', '?')}」price 必须是数字")
            continue
        forms = {f"{price:g}", f"{price}", f"{int(price)}"}
        if not any(form in haystack for form in forms):
            warnings.append(
                f"prices「{item.get('label')}」= {price} 未出现在页面文本（JSON-LD 与页面口径脱节）"
            )

    if audit_dir is None:
        for parent in page.parents:
            if parent.name == "drugs" and parent.parent.name == "content":
                audit_dir = parent.parent / "audit" / slug
                break
    if audit_dir is None:
        errors.append("无法定位 audit 目录，请用 --audit-dir 指定")
        return errors, warnings

    numbers_path = audit_dir / "numbers.json"
    if not numbers_path.exists():
        errors.append(
            f"缺少数字登记表 {numbers_path}：所有出现 ≥2 处的数字必须先登记再使用"
        )
    else:
        try:
            registry = json.loads(numbers_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"numbers.json 无效：{exc}")
            registry = None
        if isinstance(registry, dict):
            entries = registry.get("entries")
            if not isinstance(entries, list) or not entries:
                errors.append("numbers.json 需要非空 entries 数组")
                entries = []
            # 第一遍：按锚点收集登记表允许的全部数值，避免同一锚点多口径时
            # 因条目先后顺序误报冲突（如「职工约」下 1490 元与 745 元两处测算）。
            allowed_by_anchor: dict[str, set[str]] = {}
            pending: list[tuple[str, str, str]] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    errors.append("numbers.json: entry 必须是对象")
                    continue
                name = str(entry.get("name", "")).strip()
                value = str(entry.get("value", "")).strip()
                if not name or not value:
                    errors.append(f"numbers.json: entry 需要 name/value：{entry}")
                    continue
                if not entry.get("source") or not entry.get("checked_at"):
                    errors.append(f"numbers.json:「{name}」缺 source 或 checked_at")
                if value not in haystack:
                    errors.append(f"numbers.json:「{name}」登记值「{value}」在页面任何位置都不存在")
                anchor = str(entry.get("anchor", "") or "").strip()
                if not anchor:
                    stem = re.split(r"[（(]", name)[0].strip()
                    anchor = next(
                        (stem[:i] for i in range(len(stem), 1, -1) if stem[:i] in haystack),
                        stem,
                    )
                elif anchor not in haystack:
                    errors.append(f"numbers.json:「{name}」锚点「{anchor}」在页面找不到")
                pending.append((name, anchor, value))
                allowed_by_anchor.setdefault(anchor, set()).add(value)
            # 第二遍：逐锚点扫描页面，同锚点只报一次
            scanned: set[tuple[str, str]] = set()
            for name, anchor, value in pending:
                registered_nums = set(
                    re.findall(r"\d+(?:\.\d+)?", " ".join(allowed_by_anchor[anchor]))
                )
                for match in re.finditer(
                    rf"{re.escape(anchor)}[^\n]{{0,14}}?(\d+(?:\.\d+)?)\s*{NUM_UNIT}",
                    haystack,
                ):
                    found_num = match.group(1)
                    if found_num in registered_nums or (anchor, found_num) in scanned:
                        continue
                    scanned.add((anchor, found_num))
                    errors.append(
                        f"数字口径冲突：「{anchor}」在页面出现 {found_num}（{name}），"
                        f"登记表只允许 {'、'.join(sorted(registered_nums)) or '（无数值）'}"
                        f"——回 numbers.json 统一后再改页面"
                    )
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", type=Path, help="src/content/drugs/<slug>.md")
    parser.add_argument("--audit-dir", type=Path, default=None)
    args = parser.parse_args()
    if not args.page.exists():
        print(f"FAIL {args.page}: 文件不存在")
        return 1
    errors, warnings = validate(args.page, args.audit_dir)
    name = args.page.name
    if errors:
        print(f"FAIL {name}: {len(errors)} 个错误")
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print(f"PASS {name}")
    for warning in warnings:
        print(f"  ! {warning}")
    if warnings and not errors:
        print(f"（{len(warnings)} 条警告，不阻塞交付，但逐条确认）")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
