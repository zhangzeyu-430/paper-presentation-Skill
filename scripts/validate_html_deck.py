#!/usr/bin/env python
"""Validate an HTML-first paper presentation deck.

This catches common failures from generated group-meeting decks:
- missing controls, notes, source lines, cover/ending slides
- forbidden visible meta language
- broken local image paths and likely full-page PDF screenshots
- pages that are too shallow, too bullet-heavy, or missing claim/evidence/takeaway
- repeated dashboard-like layouts
- optional consistency with asset_manifest.json and deck_plan.json
"""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

FORBIDDEN_VISIBLE = [
    "封面把",
    "表格只保留",
    "示意图把",
    "读图时",
    "听众应该",
    "观众应该",
    "这个结果支持",
    "本页要放",
    "建议放",
    "页面用于",
    "页面内容建议",
    "TODO",
    "placeholder",
    "lorem",
    "Evidence / Visual",
]

SEMANTIC_CLASSES = {
    "claim",
    "takeaway",
    "context",
    "explain",
    "evidence-reading",
    "caption",
    "source",
    "figure",
    "table-wrap",
    "flow",
    "cards",
    "chart",
    "kpi",
    "kpi-row",
}

EVIDENCE_CLASSES = {"figure", "table-wrap", "flow", "cards", "chart", "kpi", "kpi-row", "matrix"}
EXPLAIN_CLASSES = {"context", "explain", "evidence-reading", "caption"}
LAYOUT_CLASS_RE = re.compile(r"^(layout-|pattern-)")


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides: list[dict] = []
        self.current: dict | None = None
        self.depth = 0
        self.skip_depth = 0
        self.ids: set[str] = set()
        self.document_classes: list[str] = []
        self.images: list[tuple[int, str]] = []
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs_raw):
        attrs = dict(attrs_raw)
        classes = attrs.get("class", "").split()
        self.document_classes.extend(classes)
        if "id" in attrs:
            self.ids.add(attrs["id"])

        if tag == "section" and "slide" in classes and self.current is None:
            self.current = {
                "h1": 0,
                "pager": 0,
                "notes": 0,
                "li": 0,
                "img": 0,
                "source": 0,
                "classes": set(classes),
                "semantic": set(c for c in classes if c in SEMANTIC_CLASSES),
            }
            self.depth = 1
            self._text = []
            return

        if self.current is not None:
            self.current["classes"].update(classes)
            self.current["semantic"].update(c for c in classes if c in SEMANTIC_CLASSES)
            if tag not in VOID_TAGS:
                self.depth += 1
            if tag == "aside":
                self.skip_depth += 1
            if tag == "h1":
                self.current["h1"] += 1
            if "pager" in classes:
                self.current["pager"] += 1
            if tag == "aside" and "notes" in classes:
                self.current["notes"] += 1
            if "source" in classes:
                self.current["source"] += 1
            if tag == "li":
                self.current["li"] += 1
            if tag == "img":
                self.current["img"] += 1
                slide_no = len(self.slides) + 1
                self.images.append((slide_no, attrs.get("src", "")))

    def handle_data(self, data: str):
        text = data.strip()
        if text and self.current is not None and self.skip_depth == 0:
            self._text.append(text)

    def handle_endtag(self, tag: str):
        if self.current is not None and tag not in VOID_TAGS:
            if tag == "aside" and self.skip_depth:
                self.skip_depth -= 1
            self.depth -= 1
            if self.depth == 0:
                text = " ".join(self._text)
                self.current["text"] = text
                self.current["text_len"] = len(re.sub(r"\s+", "", text))
                self.current["layout_classes"] = sorted(c for c in self.current["classes"] if LAYOUT_CLASS_RE.search(c))
                self.slides.append(self.current)
                self.current = None
                self._text = []


def md_slide_count(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            count += 1
    return count


def likely_full_page_image(path: Path) -> bool:
    if Image is None or not path.exists():
        return False
    with Image.open(path) as im:
        w, h = im.size
    ratio = w / max(h, 1)
    # A4/letter page screenshot often has a tall page-like ratio.
    return 0.68 < ratio < 0.86 and h > w * 1.18


def local_image_path(html_path: Path, src: str) -> Path:
    parsed = urlparse(src)
    clean = parsed.path
    return (html_path.parent / clean).resolve()


def load_json(path: Path | None) -> dict | list | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def plan_pages(plan: dict | list | None) -> list[dict]:
    if plan is None:
        return []
    if isinstance(plan, list):
        return [p for p in plan if isinstance(p, dict)]
    for key in ("slides", "pages", "deck", "plan"):
        value = plan.get(key) if isinstance(plan, dict) else None
        if isinstance(value, list):
            return [p for p in value if isinstance(p, dict)]
    return []


def manifest_asset_ids(manifest: dict | list | None) -> set[str]:
    if manifest is None:
        return set()
    assets = manifest if isinstance(manifest, list) else manifest.get("assets", [])
    ids = set()
    if isinstance(assets, list):
        for asset in assets:
            if isinstance(asset, dict) and asset.get("id"):
                ids.add(str(asset["id"]))
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--md", type=Path, help="optional HTML展示稿.md for slide count comparison")
    parser.add_argument("--manifest", type=Path, help="optional *_asset_manifest.json")
    parser.add_argument("--plan", type=Path, help="optional *_deck_plan.json")
    parser.add_argument("--min-images", type=int, default=1)
    parser.add_argument("--min-visual-ratio", type=float, default=0.70)
    args = parser.parse_args()

    html = args.html.read_text(encoding="utf-8")
    p = DeckParser()
    p.feed(html)

    problems: list[str] = []
    warnings: list[str] = []

    if args.md:
        md_pages = md_slide_count(args.md)
        if md_pages != len(p.slides):
            problems.append(f"slide count mismatch: html={len(p.slides)} md={md_pages}")

    manifest = load_json(args.manifest)
    plan = load_json(args.plan)
    plan_items = plan_pages(plan)
    manifest_ids = manifest_asset_ids(manifest)

    if args.plan and len(plan_items) != len(p.slides):
        problems.append(f"deck_plan slide count mismatch: html={len(p.slides)} plan={len(plan_items)}")
    if args.manifest and not manifest_ids:
        problems.append("asset_manifest has no asset ids")

    for req in ["prevBtn", "nextBtn", "noteBtn", "progressBar"]:
        if req not in p.ids:
            problems.append(f"missing control id: {req}")

    if "controls" not in p.document_classes:
        problems.append("missing .controls navigation container")

    if not p.slides:
        problems.append("no slides found")
    else:
        cover = p.slides[0]["text"]
        ending = p.slides[-1]["text"]
        if not any(x in cover for x in ["汇报人", "Reporter", "Presenter"]) or not any(x in cover for x in ["汇报时间", "Date", "日期"]):
            problems.append("cover missing reporter/date fields")
        if any(x in cover for x in ["动机", "方法", "实验"]) and len(cover) < 180:
            problems.append("cover looks like a content section, not an academic title slide")
        if not ("Q&A" in ending or "谢谢" in ending or "Thanks" in ending):
            problems.append("ending slide missing Q&A/thanks")
        if not ("Code" in ending or "References" in ending or "参考" in ending or "论文" in ending or "arXiv" in ending):
            problems.append("ending slide missing references/code/paper info")

    visible_text = "\n".join(slide.get("text", "") for slide in p.slides)
    for phrase in FORBIDDEN_VISIBLE:
        if phrase.lower() in visible_text.lower():
            problems.append(f"forbidden visible phrase: {phrase}")

    visual_slides = 0
    layout_sequence: list[str] = []
    generic_two_panel = 0
    for i, slide in enumerate(p.slides, 1):
        classes = set(slide["classes"])
        semantic = set(slide["semantic"])
        is_cover_or_end = i == 1 or i == len(p.slides)

        if i != 1 and slide["h1"] < 1:
            problems.append(f"slide {i} missing h1")
        if slide["notes"] < 1:
            problems.append(f"slide {i} missing notes")
        if i != 1 and slide["pager"] < 1:
            problems.append(f"slide {i} missing pager")
        if i != 1 and slide["source"] < 1:
            problems.append(f"slide {i} missing .source")
        if slide["li"] > 6:
            problems.append(f"slide {i} has too many bullets: {slide['li']}")

        has_evidence = bool(classes & EVIDENCE_CLASSES) or slide["img"] > 0
        if has_evidence:
            visual_slides += 1
        if not is_cover_or_end and not has_evidence:
            problems.append(f"slide {i} missing evidence visual component")

        if not is_cover_or_end and {"grid", "text-panel", "visual-panel"}.issubset(classes):
            generic_two_panel += 1
        if not is_cover_or_end and "takeaway" in classes:
            text = slide.get("text", "")
            if len(text) > 80:
                problems.append(f"slide {i} has a visible takeaway block that may obstruct content")

        has_claim_or_takeaway = bool({"claim", "takeaway"} & semantic)
        if not is_cover_or_end and not has_claim_or_takeaway:
            problems.append(f"slide {i} missing claim/takeaway semantic component")

        explain_count = len(semantic & EXPLAIN_CLASSES)
        if not is_cover_or_end and explain_count < 2:
            problems.append(f"slide {i} has too few explanation nodes: {explain_count}")

        if not is_cover_or_end:
            if slide["text_len"] < 120:
                problems.append(f"slide {i} visible text too shallow: {slide['text_len']} chars")
            if slide["text_len"] > 760:
                warnings.append(f"slide {i} visible text may be too dense: {slide['text_len']} chars")

        layout = ",".join(slide["layout_classes"]) or "unknown"
        layout_sequence.append(layout)
        if i >= 3 and layout_sequence[-1] == layout_sequence[-2] == layout_sequence[-3] and layout != "unknown":
            problems.append(f"slides {i-2}-{i} repeat the same layout: {layout}")

    if p.slides:
        ratio = visual_slides / len(p.slides)
        if ratio < args.min_visual_ratio:
            problems.append(f"visual component ratio too low: {ratio:.2f} < {args.min_visual_ratio:.2f}")
        content_count = max(1, len(p.slides) - 2)
        generic_ratio = generic_two_panel / content_count
        if generic_ratio > 0.55:
            problems.append(f"too many generic left-text/right-visual slides: {generic_two_panel}/{content_count}")

    if len(p.images) < args.min_images:
        problems.append(f"too few local figure images: {len(p.images)} < {args.min_images}")

    for slide_no, src in p.images:
        if src.startswith(("http://", "https://", "data:")):
            continue
        path = local_image_path(args.html, src)
        if not path.exists():
            problems.append(f"broken image path on slide {slide_no}: {src}")
        elif likely_full_page_image(path):
            problems.append(f"possible full-page PDF screenshot instead of cropped figure on slide {slide_no}: {src}")

    if plan_items and manifest_ids:
        for idx, item in enumerate(plan_items, 1):
            evidence_ids = item.get("evidence_ids") or []
            if isinstance(evidence_ids, str):
                evidence_ids = [evidence_ids]
            missing = [eid for eid in evidence_ids if str(eid) not in manifest_ids]
            if missing:
                problems.append(f"deck_plan slide {idx} references unknown evidence ids: {missing}")
            if not item.get("layout_pattern"):
                problems.append(f"deck_plan slide {idx} missing layout_pattern")
            if not item.get("claim") and idx not in (1, len(plan_items)):
                problems.append(f"deck_plan slide {idx} missing claim")

    print(f"slides: {len(p.slides)}")
    print(f"images: {len(p.images)}")
    print(f"visual_ratio: {(visual_slides / len(p.slides)) if p.slides else 0:.2f}")
    print(f"controls: {all(x in p.ids for x in ['prevBtn', 'nextBtn', 'noteBtn', 'progressBar'])}")
    print(f"warnings: {len(warnings)}")
    for warning in warnings:
        print(f"! {warning}")
    print(f"problems: {len(problems)}")
    for problem in problems:
        print(f"- {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
