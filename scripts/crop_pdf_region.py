#!/usr/bin/env python
"""Crop figures/tables from a PDF into image assets for HTML PPT decks.

Usage examples:
  python crop_pdf_region.py paper.pdf --out outputs/assets --page 3 --rect 45,42,565,430 --name figure2.png
  python crop_pdf_region.py paper.pdf --out outputs/assets --page 3 --full-page --name page03.png

Coordinates are PDF points: x0,y0,x1,y1 in page coordinate space.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def parse_rect(value: str) -> fitz.Rect:
    parts = [float(x.strip()) for x in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--rect must be x0,y0,x1,y1")
    x0, y0, x1, y1 = parts
    if x1 <= x0 or y1 <= y0:
        raise argparse.ArgumentTypeError("--rect must satisfy x1>x0 and y1>y0")
    return fitz.Rect(x0, y0, x1, y1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--page", type=int, required=True, help="1-based page number")
    parser.add_argument("--rect", type=parse_rect, help="crop rectangle x0,y0,x1,y1")
    parser.add_argument("--full-page", action="store_true", help="render whole page, only for QA/backups")
    parser.add_argument("--name", required=True)
    parser.add_argument("--zoom", type=float, default=2.6)
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")
    if not args.full_page and args.rect is None:
        raise SystemExit("Provide --rect unless --full-page is set.")

    args.out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    if args.page < 1 or args.page > len(doc):
        raise SystemExit(f"--page out of range: {args.page}; PDF has {len(doc)} pages")
    page = doc[args.page - 1]
    clip = None if args.full_page else args.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(args.zoom, args.zoom), clip=clip, alpha=False)
    dest = args.out / args.name
    pix.save(dest)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
