"""Share/preview assets (Open Graph images).

This module intentionally keeps generation lightweight and dependency-minimal.
We use Pillow (PIL) which is commonly available in many environments.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Query
from fastapi.responses import Response

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]
    ImageDraw = None  # type: ignore[assignment]
    ImageFont = None  # type: ignore[assignment]


router = APIRouter(prefix="/share", tags=["share"])


@dataclass(frozen=True)
class ShareCardSpec:
    """Specification for a share card image."""

    title: str
    subtitle: str


def _safe_text(value: str, *, max_len: int) -> str:
    """Clamp user-provided text for safe rendering."""

    cleaned = (value or "").strip().replace("\n", " ")
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 1].rstrip() + "…"


def _render_share_card_png(spec: ShareCardSpec) -> bytes:
    """Render a simple Open Graph share card.

    Args:
        spec: Share card specification.

    Returns:
        PNG bytes.

    Raises:
        RuntimeError: If Pillow is not installed.
    """

    if Image is None:
        raise RuntimeError("Pillow is required to render share cards")

    width, height = 1200, 630
    bg = (10, 13, 20)
    fg = (245, 246, 250)
    accent = (99, 102, 241)

    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    # Background accent shapes
    draw.rectangle([0, 0, width, 18], fill=accent)
    draw.rectangle([0, height - 18, width, height], fill=accent)

    margin_x = 84
    y = 120

    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()

    title = _safe_text(spec.title, max_len=70)
    subtitle = _safe_text(spec.subtitle, max_len=120)

    draw.text((margin_x, y), title, fill=fg, font=title_font)
    y += 60
    draw.text((margin_x, y), subtitle, fill=(200, 205, 220), font=subtitle_font)

    # Footer branding
    footer = "reposcape"
    draw.text((margin_x, height - 80), footer, fill=fg, font=subtitle_font)

    # Simple sparkline
    x0, y0 = width - 420, 160
    points = [
        (x0 + 0, y0 + 220),
        (x0 + 60, y0 + 170),
        (x0 + 120, y0 + 190),
        (x0 + 180, y0 + 120),
        (x0 + 240, y0 + 140),
        (x0 + 300, y0 + 80),
        (x0 + 360, y0 + 100),
    ]
    draw.line(points, fill=accent, width=6, joint="curve")

    out = bytearray()
    img.save(out, format="PNG")
    return bytes(out)


@router.get("/card.png")
def share_card(
    title: str = Query(default="Reposcape", max_length=120),
    subtitle: str = Query(default="Turn any GitHub repo into a beautiful visual story", max_length=200),
) -> Response:
    """Generate a share card suitable for Open Graph previews."""

    spec = ShareCardSpec(title=title, subtitle=subtitle)
    png_bytes = _render_share_card_png(spec)
    return Response(content=png_bytes, media_type="image/png")
