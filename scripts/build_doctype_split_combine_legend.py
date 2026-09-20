#!/usr/bin/env python3
"""Build split/combine legend from 寺田 紗織 sample PDF for doctype manual."""

from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PDF = Path("/Users/mac/Desktop/AIPM/Projects/NeosAI/IDP/IDP测试票据/复杂画像分割+组合/寺田纱织.pdf")
OUT = ASSETS / "doctype-split-combine-legend.png"

BG = (255, 255, 255, 255)
INK = (51, 65, 85, 255)
MUTED = (102, 112, 133, 255)
BLUE = (25, 118, 210, 255)
GREEN = (46, 125, 50, 255)
ORANGE = (230, 126, 34, 255)
PANEL_BG = (247, 251, 253, 255)
BORDER = (201, 225, 235, 255)
PAD = 28
GAP = 18


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def render_page(doc: fitz.Document, page_no: int, width: int) -> Image.Image:
    page = doc[page_no - 1]
    scale = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def fit_height(img: Image.Image, height: int) -> Image.Image:
    if img.height == height:
        return img
    ratio = height / img.height
    return img.resize((max(1, round(img.width * ratio)), height), Image.Resampling.LANCZOS)


def fit_width(img: Image.Image, width: int) -> Image.Image:
    if img.width == width:
        return img
    ratio = width / img.width
    return img.resize((width, max(1, round(img.height * ratio))), Image.Resampling.LANCZOS)


def label_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: tuple[int, int, int, int]) -> None:
    f = font(13, bold=True)
    pad_x, pad_y = 8, 4
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle((x, y, x + tw + pad_x * 2, y + th + pad_y * 2), radius=6, fill=fill)
    draw.text((x + pad_x, y + pad_y - 1), text, fill=(255, 255, 255, 255), font=f)


def draw_arrow(draw: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int) -> None:
    draw.line((x0, y0, x1, y1), fill=BLUE, width=3)
    if x1 > x0:
        draw.polygon([(x1, y1), (x1 - 10, y1 - 5), (x1 - 10, y1 + 5)], fill=BLUE)
    elif y1 > y0:
        draw.polygon([(x1, y1), (x1 - 5, y1 - 10), (x1 + 5, y1 - 10)], fill=BLUE)


def paste_thumb(canvas: Image.Image, img: Image.Image, x: int, y: int, caption: str | None = None) -> None:
    draw = ImageDraw.Draw(canvas)
    border = 1
    draw.rectangle((x - border, y - border, x + img.width + border, y + img.height + border), outline=BORDER, width=1)
    canvas.paste(img, (x, y))
    if caption:
        f = font(12)
        draw.text((x, y + img.height + 6), caption, fill=MUTED, font=f)


def main() -> None:
    doc = fitz.open(PDF)
    title_f = font(18, bold=True)
    section_f = font(15, bold=True)
    body_f = font(13)

    split_h = 150
    p14 = fit_height(render_page(doc, 14, 170), split_h)
    p10 = fit_height(render_page(doc, 10, 220), split_h)
    p15 = fit_height(render_page(doc, 15, 120), 130)
    p16 = fit_height(render_page(doc, 16, 120), 130)
    p17 = fit_height(render_page(doc, 17, 120), 130)

    out_w = 1040
    out_h = 780
    canvas = Image.new("RGBA", (out_w, out_h), BG)
    draw = ImageDraw.Draw(canvas)

    y = PAD
    draw.text((PAD, y), "実例：寺田 紗織.pdf（20 ページ）— 画像分割と組合", fill=INK, font=title_f)
    y += 34
    draw.text(
        (PAD, y),
        "1 つの PDF に区切りシート・請求書・診療明細書が混在するケース。前処理で論理帳票へ切り分け、同一帳票タイプ内では組合キーで再統合します。",
        fill=MUTED,
        font=body_f,
    )
    y += 34

    # Split section panel
    panel_top = y
    panel_h = 250
    draw.rounded_rectangle((PAD, panel_top, out_w - PAD, panel_top + panel_h), radius=10, fill=PANEL_BG, outline=BORDER, width=1)
    label_chip(draw, PAD + 12, panel_top + 12, "画像分割", BLUE)
    draw.text((PAD + 110, panel_top + 16), "1 枚のスキャン画像に複数の論理帳票が含まれる場合", fill=INK, font=section_f)

    row1_y = panel_top + 52
    draw.text((PAD + 16, row1_y), "例 A", fill=ORANGE, font=section_f)
    paste_thumb(canvas, p14, PAD + 56, row1_y + 4, "14 ページ：請求書 × 2")
    ax = PAD + 56 + p14.width + 28
    ay = row1_y + split_h // 2 + 4
    draw_arrow(draw, ax - 18, ay, ax + 8, ay)
    tx = ax + 20
    box_w, box_h = 118, 58
    for i, cap in enumerate(["論理ファイル A", "論理ファイル B"], start=1):
        by = row1_y + 8 + (i - 1) * (box_h + 10)
        draw.rounded_rectangle((tx, by, tx + box_w, by + box_h), radius=6, fill=(255, 255, 255, 255), outline=GREEN, width=2)
        draw.text((tx + 10, by + 18), cap, fill=GREEN, font=body_f)
    draw.text((tx, row1_y + split_h + 18), "縦に 2 枚の請求書 → 2 ファイルに分割", fill=MUTED, font=font(12))

    row2_y = panel_top + 148
    draw.text((PAD + 16, row2_y), "例 B", fill=ORANGE, font=section_f)
    paste_thumb(canvas, p10, PAD + 56, row2_y + 4, "10 ページ：横並び 3 帳票")
    ax2 = PAD + 56 + p10.width + 28
    ay2 = row2_y + split_h // 2 + 4
    draw_arrow(draw, ax2 - 18, ay2, ax2 + 8, ay2)
    tx2 = ax2 + 20
    for i, cap in enumerate(["論理ファイル 1", "論理ファイル 2", "論理ファイル 3"], start=1):
        bx = tx2 + (i - 1) * (box_w + 8)
        by = row2_y + 24
        draw.rounded_rectangle((bx, by, bx + box_w, by + box_h), radius=6, fill=(255, 255, 255, 255), outline=GREEN, width=2)
        draw.text((bx + 8, by + 18), cap, fill=GREEN, font=body_f)
    draw.text((tx2, row2_y + split_h + 18), "横並び 3 帳票 → 3 ファイルに分割", fill=MUTED, font=font(12))

    y = panel_top + panel_h + GAP

    # Combine section panel
    comb_h = 250
    draw.rounded_rectangle((PAD, y, out_w - PAD, y + comb_h), radius=10, fill=PANEL_BG, outline=BORDER, width=1)
    label_chip(draw, PAD + 12, y + 12, "組合", GREEN)
    draw.text((PAD + 88, y + 16), "分割後、同一帳票タイプの複数画像を 1 論理ファイルへ", fill=INK, font=section_f)

    cy = y + 52
    thumbs = [(p15, "15 ページ\n1/2"), (p16, "16 ページ\n2/3"), (p17, "17 ページ\n3/3")]
    cx = PAD + 56
    for img, cap in thumbs:
        paste_thumb(canvas, img, cx, cy, cap.replace("\n", " "))
        cx += img.width + 14
    mid_y = cy + 130 // 2
    draw_arrow(draw, cx + 4, mid_y, cx + 34, mid_y)
    rx = cx + 46
    rw, rh = 170, 130
    draw.rounded_rectangle((rx, cy, rx + rw, cy + rh), radius=8, fill=(255, 255, 255, 255), outline=GREEN, width=2)
    draw.text((rx + 14, cy + 24), "1 論理ファイル", fill=GREEN, font=section_f)
    draw.text((rx + 14, cy + 52), "診療明細書（3 ページ）", fill=INK, font=body_f)
    draw.text((rx + 14, cy + 76), "患者番号：018334", fill=MUTED, font=font(12))
    draw.text((rx + 14, cy + 94), "帯広病院 · 同一請求期間", fill=MUTED, font=font(12))

    key_y = y + comb_h - 54
    draw.text((PAD + 16, key_y), "組合必須キー", fill=INK, font=body_f)
    draw.rounded_rectangle((PAD + 108, key_y - 2, PAD + 188, key_y + 22), radius=4, fill=(234, 245, 251, 255), outline=BORDER)
    draw.text((PAD + 116, key_y + 1), "患者番号", fill=BLUE, font=body_f)
    draw.rounded_rectangle((PAD + 198, key_y - 2, PAD + 278, key_y + 22), radius=4, fill=(234, 245, 251, 255), outline=BORDER)
    draw.text((PAD + 206, key_y + 1), "発行日", fill=BLUE, font=body_f)
    draw.text((PAD + 292, key_y), "＋  組合任意キー", fill=INK, font=body_f)
    draw.rounded_rectangle((PAD + 418, key_y - 2, PAD + 518, key_y + 22), radius=4, fill=(234, 245, 251, 255), outline=BORDER)
    draw.text((PAD + 426, key_y + 1), "医療機関名", fill=BLUE, font=body_f)
    draw.text((PAD + 536, key_y), "（いずれか一致）", fill=MUTED, font=font(12))

    doc.close()
    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
