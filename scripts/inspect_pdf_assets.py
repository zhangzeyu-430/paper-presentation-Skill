#!/usr/bin/env python
"""Inspect a paper PDF for candidate figures, tables, captions, and image blocks.

This script does not replace human judgment. It gives Codex a deterministic
starting point for building asset_manifest.json before cropping figures.

Usage:
  python inspect_pdf_assets.py paper.pdf --out outputs/paper_asset_candidates.json
  python inspect_pdf_assets.py paper.pdf --pages 1-4,8,12 --out outputs/candidates.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import fitz


CAPTION_RE = re.compile(r"\b(Figure|Fig\.|Table|Tab\.)\s*([A-Za-z0-9.\-]+)", re.IGNORECASE)
FORMULA_HINT_RE = re.compile(r"(where|Equation|Eq\.|\bloss\b|\bobjective\b|公式|损失|目标函数)", re.IGNORECASE)


def parse_pages(value: str | None, total: int) -> list[int]:
    if not value:
        return list(range(1, total + 1))
    pages: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(x) for x in part.split("-", 1)]
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return [p for p in sorted(pages) if 1 <= p <= total]


def rect_to_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]


def nearby_rect(caption: fitz.Rect, page_rect: fitz.Rect) -> list[float]:
    """Guess a figure/table crop above the caption.

    Captions usually sit below figures/tables. The guessed region is intentionally
    conservative and should be reviewed before using crop_pdf_region.py.
    """

    top = max(page_rect.y0 + 24, caption.y0 - page_rect.height * 0.42)
    bottom = min(page_rect.y1 - 24, caption.y0 + 12)
    left = max(page_rect.x0 + 24, caption.x0 - 18)
    right = min(page_rect.x1 - 24, page_rect.x1 - 24)
    if bottom <= top + 20:
        top = max(page_rect.y0 + 24, caption.y0 - 220)
        bottom = caption.y0
    return rect_to_list(fitz.Rect(left, top, right, bottom))


def iter_text_blocks(page: fitz.Page) -> Iterable[dict]:
    for block in page.get_text("blocks"):
        if len(block) < 5:
            continue
        x0, y0, x1, y1, text = block[:5]
        text = " ".join(str(text).split())
        if text:
            yield {"bbox": fitz.Rect(x0, y0, x1, y1), "text": text}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", help="1-based page list/ranges, e.g. 1-4,8,12")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-caption-chars", type=int, default=520)
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    doc = fitz.open(args.pdf)
    pages = parse_pages(args.pages, len(doc))
    candidates: list[dict] = []

    for page_no in pages:
        page = doc[page_no - 1]
        page_rect = page.rect

        for idx, image in enumerate(page.get_images(full=True), 1):
            xref = image[0]
            rects = page.get_image_rects(xref)
            for rect_idx, rect in enumerate(rects, 1):
                area_ratio = (rect.width * rect.height) / max(page_rect.width * page_rect.height, 1)
                candidates.append(
                    {
                        "id": f"p{page_no}_image_{idx}_{rect_idx}",
                        "type": "image_block",
                        "page": page_no,
                        "bbox": rect_to_list(rect),
                        "area_ratio": round(area_ratio, 4),
                        "caption_or_context": "",
                        "crop_command_hint": f"--page {page_no} --rect {','.join(map(str, rect_to_list(rect)))}",
                        "review_note": "Review whether this is a real figure/table or only an embedded sub-image.",
                    }
                )

        for block in iter_text_blocks(page):
            text = block["text"]
            match = CAPTION_RE.search(text)
            if match:
                label = match.group(0).replace(" ", "_").replace(".", "")
                caption = text[: args.max_caption_chars]
                guess = nearby_rect(block["bbox"], page_rect)
                candidates.append(
                    {
                        "id": f"p{page_no}_{label}",
                        "type": "caption_candidate",
                        "page": page_no,
                        "bbox": rect_to_list(block["bbox"]),
                        "suggested_crop_bbox": guess,
                        "caption_or_context": caption,
                        "crop_command_hint": f"--page {page_no} --rect {','.join(map(str, guess))}",
                        "review_note": "Suggested crop is a heuristic region above the caption; adjust before final use.",
                    }
                )
            elif FORMULA_HINT_RE.search(text):
                candidates.append(
                    {
                        "id": f"p{page_no}_formula_context_{len(candidates)+1}",
                        "type": "formula_or_method_text",
                        "page": page_no,
                        "bbox": rect_to_list(block["bbox"]),
                        "caption_or_context": text[: args.max_caption_chars],
                        "review_note": "Potential formula/method context for faithful redraw or explanation.",
                    }
                )

    result = {
        "pdf": str(args.pdf),
        "page_count": len(doc),
        "inspected_pages": pages,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.out)
    print(f"candidates: {len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
