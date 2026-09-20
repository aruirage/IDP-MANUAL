#!/usr/bin/env python3
"""Compose business-scene manual screenshots: crop, merge, highlights and arrows."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MANIFEST = Path(__file__).with_name("business-scene-shots.json")

OUTPUT_SCALE = max(1, int(os.environ.get("OUTPUT_SCALE", "1")))
PAD = 24 * OUTPUT_SCALE
GAP = 28 * OUTPUT_SCALE
CAPTION_GAP = 8 * OUTPUT_SCALE
CAPTION_H = 22 * OUTPUT_SCALE
BG = (255, 255, 255, 255)
HIGHLIGHT = (229, 57, 53, 255)
ARROW = (25, 118, 210, 255)
LABEL_BG = (25, 118, 210, 255)
LABEL_FG = (255, 255, 255, 255)
CAPTION = (96, 96, 96, 255)


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def font(size: int = 18, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = max(1, round(size * OUTPUT_SCALE))
    candidates = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def crop_box(img: Image.Image, box: list[float] | None) -> Image.Image:
    if not box:
        return img
    w, h = img.size
    x0, y0, x1, y1 = box
    return img.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))


def fit_width(img: Image.Image, width: int) -> Image.Image:
    if img.width == width:
        return img
    if img.width < width:
        return img
    ratio = width / img.width
    height = max(1, round(img.height * ratio))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def fit_height(img: Image.Image, height: int) -> Image.Image:
    if img.height == height:
        return img
    if img.height < height:
        return img
    ratio = height / img.height
    width = max(1, round(img.width * ratio))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def scale_panel(img: Image.Image) -> Image.Image:
    if OUTPUT_SCALE == 1:
        return img
    return img.resize(
        (img.width * OUTPUT_SCALE, img.height * OUTPUT_SCALE),
        Image.Resampling.LANCZOS,
    )


def load_panel(source: str, crop: list[float] | None = None) -> Image.Image:
    img = load_rgba(ASSETS / source)
    return crop_box(img, crop)


def box_px(panel: dict, img: Image.Image) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = panel["box"]
    w, h = img.size
    return (round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))


def draw_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    f = font(16, bold=True)
    pad_x, pad_y = 8 * OUTPUT_SCALE, 4 * OUTPUT_SCALE
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle(
        (x, y, x + tw + pad_x * 2, y + th + pad_y * 2),
        radius=10 * OUTPUT_SCALE,
        fill=LABEL_BG,
    )
    draw.text((x + pad_x, y + pad_y - OUTPUT_SCALE), text, fill=LABEL_FG, font=f)


def draw_highlight(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], label: str | None = None) -> None:
    x0, y0, x1, y1 = rect
    line_w = max(1, 3 * OUTPUT_SCALE)
    draw.rectangle(rect, outline=HIGHLIGHT, width=line_w)
    if label:
        draw_label(draw, x0 + 6 * OUTPUT_SCALE, max(6 * OUTPUT_SCALE, y0 - 28 * OUTPUT_SCALE), label)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    x0, y0 = start
    x1, y1 = end
    line_w = max(1, 3 * OUTPUT_SCALE)
    draw.line((x0, y0, x1, y1), fill=ARROW, width=line_w)
    angle = math.atan2(y1 - y0, x1 - x0)
    size = 10 * OUTPUT_SCALE
    for da in (2.6, -2.6):
        ax = x1 - size * math.cos(angle - da)
        ay = y1 - size * math.sin(angle - da)
        draw.line((x1, y1, ax, ay), fill=ARROW, width=line_w)


def panel_anchor(
    pos: tuple[int, int, Image.Image],
    side: str,
) -> tuple[int, int]:
    x, y, img = pos
    if side == "left":
        return (x, y + img.height // 2)
    if side == "right":
        return (x + img.width, y + img.height // 2)
    if side == "top":
        return (x + img.width // 2, y)
    if side == "bottom":
        return (x + img.width // 2, y + img.height)
    if side == "center":
        return (x + img.width // 2, y + img.height // 2)
    return (x + img.width // 2, y + img.height // 2)


def resolve_anchor(pos: tuple[int, int, Image.Image], spec: dict) -> tuple[int, int]:
    if "box" in spec:
        x, y, img = pos
        rect = box_px(spec, img)
        side = spec.get("side", "center")
        rx0, ry0, rx1, ry1 = rect
        cx, cy = (rx0 + rx1) // 2, (ry0 + ry1) // 2
        if side == "left":
            return (x + rx0, y + cy)
        if side == "right":
            return (x + rx1, y + cy)
        if side == "top":
            return (x + cx, y + ry0)
        if side == "bottom":
            return (x + cx, y + ry1)
        return (x + cx, y + cy)
    return panel_anchor(pos, spec.get("side", "center"))


def apply_cell_decorations(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int, Image.Image],
    cell: dict,
) -> None:
    x, y, img = pos
    if cell.get("label"):
        draw_label(draw, x + 8 * OUTPUT_SCALE, y + 8 * OUTPUT_SCALE, cell["label"])
    for hi in cell.get("highlights", []):
        rect = box_px({"box": hi["box"]}, img)
        draw_highlight(draw, (x + rect[0], y + rect[1], x + rect[2], y + rect[3]), hi.get("label"))


def compose_grid(recipe: dict) -> Image.Image:
    cells = recipe["cells"]
    col_width_fixed = recipe.get("col_width")
    panel_imgs: list[tuple[Image.Image, dict]] = []
    max_row_heights: dict[int, int] = {}
    col_widths: dict[int, int] = {}

    for cell in cells:
        img = load_panel(cell["source"], cell.get("crop"))
        if col_width_fixed:
            img = fit_width(img, col_width_fixed * OUTPUT_SCALE)
        img = scale_panel(img)
        col = cell.get("col", 0)
        col_widths[col] = max(col_widths.get(col, 0), img.width)
        row = cell.get("row", 0)
        max_row_heights[row] = max(max_row_heights.get(row, 0), img.height + (CAPTION_H if cell.get("caption") else 0))
        panel_imgs.append((img, cell))

    rows = max(c.get("row", 0) for c in cells) + 1
    cols = max(c.get("col", 0) for c in cells) + 1
    if col_width_fixed:
        canvas_w = PAD * 2 + cols * col_width_fixed + (cols - 1) * GAP
    else:
        canvas_w = PAD * 2 + sum(col_widths.get(c, 0) for c in range(cols)) + (cols - 1) * GAP
    canvas_h = PAD * 2 + sum(max_row_heights.get(r, 0) for r in range(rows)) + (rows - 1) * GAP
    canvas = Image.new("RGBA", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(canvas)

    col_offsets = [PAD]
    for c in range(1, cols):
        prev_w = col_width_fixed if col_width_fixed else col_widths.get(c - 1, 0)
        col_offsets.append(col_offsets[-1] + prev_w + GAP)

    positions: dict[str, tuple[int, int, Image.Image]] = {}
    y_offsets = [PAD]
    for r in range(1, rows):
        y_offsets.append(y_offsets[-1] + max_row_heights[r - 1] + GAP)

    for img, cell in panel_imgs:
        col = cell.get("col", 0)
        row = cell.get("row", 0)
        x = col_offsets[col]
        y = y_offsets[row]
        canvas.alpha_composite(img, (x, y))
        positions[cell["id"]] = (x, y, img)
        apply_cell_decorations(draw, positions[cell["id"]], cell)
        if cell.get("caption"):
            f = font(14)
            draw.text((x, y + img.height + CAPTION_GAP), cell["caption"], fill=CAPTION, font=f)

    for arrow in recipe.get("arrows", []):
        src = positions[arrow["from"]]
        dst = positions[arrow["to"]]
        start = resolve_anchor(src, arrow.get("from_anchor", {"side": "right"}))
        end = resolve_anchor(dst, arrow.get("to_anchor", {"side": "left"}))
        draw_arrow(draw, start, end)

    return canvas.convert("RGB")


def compose_stack(recipe: dict) -> Image.Image:
    cells = recipe["cells"]
    imgs = [scale_panel(load_panel(c["source"], c.get("crop"))) for c in cells]
    if recipe.get("width"):
        imgs = [fit_width(im, recipe["width"] * OUTPUT_SCALE) for im in imgs]
    content_w = max(im.width for im in imgs)
    extra = sum(CAPTION_H for c in cells if c.get("caption"))
    canvas_h = PAD * 2 + sum(im.height for im in imgs) + GAP * (len(imgs) - 1) + extra
    canvas = Image.new("RGBA", (content_w + PAD * 2, canvas_h), BG)
    draw = ImageDraw.Draw(canvas)
    positions: dict[str, tuple[int, int, Image.Image]] = {}
    y = PAD
    for cell, img in zip(cells, imgs):
        x = PAD
        canvas.alpha_composite(img, (x, y))
        positions[cell["id"]] = (x, y, img)
        apply_cell_decorations(draw, positions[cell["id"]], cell)
        y += img.height
        if cell.get("caption"):
            f = font(14)
            draw.text((x, y + CAPTION_GAP), cell["caption"], fill=CAPTION, font=f)
            y += CAPTION_H
        y += GAP

    for arrow in recipe.get("arrows", []):
        src = positions[arrow["from"]]
        dst = positions[arrow["to"]]
        start = resolve_anchor(src, arrow.get("from_anchor", {"side": "bottom"}))
        end = resolve_anchor(dst, arrow.get("to_anchor", {"side": "top"}))
        draw_arrow(draw, start, end)

    return canvas.convert("RGB")


def compose_side_by_side(recipe: dict) -> Image.Image:
    left = scale_panel(load_panel(recipe["left"]["source"], recipe["left"].get("crop")))
    right = scale_panel(load_panel(recipe["right"]["source"], recipe["right"].get("crop")))
    if recipe.get("height"):
        height = recipe["height"] * OUTPUT_SCALE
        left = fit_height(left, height)
        right = fit_height(right, height)
    canvas_w = PAD * 2 + left.width + GAP + right.width
    canvas_h = PAD * 2 + max(left.height, right.height)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(canvas)
    lx, ly = PAD, PAD
    rx, ry = PAD + left.width + GAP, PAD
    canvas.alpha_composite(left, (lx, ly))
    canvas.alpha_composite(right, (rx, ry))
    positions = {
        recipe["left"]["id"]: (lx, ly, left),
        recipe["right"]["id"]: (rx, ry, right),
    }
    apply_cell_decorations(draw, positions[recipe["left"]["id"]], recipe["left"])
    apply_cell_decorations(draw, positions[recipe["right"]["id"]], recipe["right"])

    for arrow in recipe.get("arrows", []):
        src = positions[arrow["from"]]
        dst = positions[arrow["to"]]
        start = resolve_anchor(src, arrow.get("from_anchor", {"box": arrow.get("from_box", [0.5, 0.5, 0.5, 0.5]), "side": "right"}))
        end = resolve_anchor(dst, arrow.get("to_anchor", {"box": arrow.get("to_box", [0.5, 0.5, 0.5, 0.5]), "side": "left"}))
        draw_arrow(draw, start, end)

    return canvas.convert("RGB")


def compose_single(recipe: dict) -> Image.Image:
    img = scale_panel(load_panel(recipe["source"], recipe.get("crop")))
    if recipe.get("width"):
        img = fit_width(img, recipe["width"] * OUTPUT_SCALE)
    canvas = Image.new("RGBA", (img.width + PAD * 2, img.height + PAD * 2), BG)
    draw = ImageDraw.Draw(canvas)
    x, y = PAD, PAD
    canvas.alpha_composite(img, (x, y))
    pos = (x, y, img)
    cell = {"highlights": recipe.get("highlights", []), "label": recipe.get("label")}
    apply_cell_decorations(draw, pos, cell)
    return canvas.convert("RGB")


def run_recipe(recipe: dict) -> Path:
    layout = recipe["layout"]
    if layout == "grid":
        out = compose_grid(recipe)
    elif layout == "stack":
        out = compose_stack(recipe)
    elif layout == "side_by_side":
        out = compose_side_by_side(recipe)
    elif layout == "single":
        out = compose_single(recipe)
    else:
        raise ValueError(f"Unknown layout: {layout}")
    dest = ASSETS / recipe["output"]
    out.save(dest, format="PNG", compress_level=3, optimize=False)
    return dest


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if OUTPUT_SCALE != 1:
        print(f"OUTPUT_SCALE={OUTPUT_SCALE}")
    for recipe in data["recipes"]:
        path = run_recipe(recipe)
        im = Image.open(path)
        print(f"Wrote {path.name} {im.size[0]}x{im.size[1]} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
