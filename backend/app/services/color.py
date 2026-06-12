"""Color parsing and conversions for hex / rgb() / hsl() inputs."""

from __future__ import annotations

import math
import re

_HEX = re.compile(r"^#?([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", re.IGNORECASE)
_RGB = re.compile(r"^rgba?\(([^)]+)\)$", re.IGNORECASE)
_HSL = re.compile(r"^hsla?\(([^)]+)\)$", re.IGNORECASE)


def _parse_components(s: str) -> list[float]:
    return [float(x.strip().rstrip("%")) for x in s.split(",")]


def parse_color(s: str) -> tuple[int, int, int]:
    """Return (r, g, b) ∈ [0, 255]."""
    s = s.strip()
    m = _HEX.match(s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            r, g, b = (int(c * 2, 16) for c in h)
        elif len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        else:  # 8 — strip alpha
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r, g, b
    m = _RGB.match(s)
    if m:
        comps = _parse_components(m.group(1))[:3]
        return tuple(int(round(c)) for c in comps)  # type: ignore[return-value]
    m = _HSL.match(s)
    if m:
        h, sat, light = _parse_components(m.group(1))[:3]
        return _hsl_to_rgb(h, sat / 100, light / 100)
    raise ValueError(f"Unrecognized color: {s!r}")


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:  # noqa: E741
    h = h % 360
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int(round((r + m) * 255)), int(round((g + m) * 255)), int(round((b + m) * 255)))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    rn, gn, bn = r / 255, g / 255, b / 255
    mx, mn = max(rn, gn, bn), min(rn, gn, bn)
    l = (mx + mn) / 2  # noqa: E741
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == rn:
            h = ((gn - bn) / d + (6 if gn < bn else 0)) * 60
        elif mx == gn:
            h = ((bn - rn) / d + 2) * 60
        else:
            h = ((rn - gn) / d + 4) * 60
    return (round(h, 1), round(s * 100, 1), round(l * 100, 1))


def _srgb_to_linear(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: int, g: int, b: int) -> float:
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    light, dark = max(l1, l2), min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


def rgb_to_oklch(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert sRGB 0-255 to OKLCH (L*, C, h°). Reference: https://bottosson.github.io/posts/oklab/"""
    rl, gl, bl = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    l_ = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl
    m_ = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl
    s_ = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl
    l_, m_, s_ = l_ ** (1 / 3), m_ ** (1 / 3), s_ ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_ = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = math.hypot(a, b_)
    h = math.degrees(math.atan2(b_, a)) % 360
    return (round(L, 4), round(C, 4), round(h, 1))
