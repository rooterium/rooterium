"""Contrast checks for the colour tokens in site.css (WCAG AA).

Text needs 4.5:1, large text and UI parts (borders of controls, focus
rings, map markers) 3:1. The pairs mirror the rules in
docs/PROJECT_BRIEF.md, section 6.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

CSS = Path(settings.BASE_DIR) / "core/static/core/css/site.css"


def tokens() -> dict[str, str]:
    root = re.search(r":root\s*{(.*?)}", CSS.read_text(), re.S).group(1)
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", root))


def luminance(hex_colour: str) -> float:
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_colour[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class ContrastTests(SimpleTestCase):
    TEXT = 4.5
    UI = 3.0

    def setUp(self):
        self.t = tokens()

    def check(self, fg, bg, minimum):
        ratio = contrast(self.t[fg], self.t[bg])
        self.assertGreaterEqual(
            ratio, minimum, f"--{fg} on --{bg}: {ratio:.2f}:1 < {minimum}:1"
        )

    def test_palette_v2_is_used(self):
        self.assertEqual(self.t["bg"].lower(), "#0b0a09")
        self.assertEqual(self.t["accent"].lower(), "#a6352c")

    def test_text_colours_on_backgrounds(self):
        for fg in ("text", "text-secondary", "text-muted", "accent-2"):
            for bg in ("bg", "surface"):
                with self.subTest(fg=fg, bg=bg):
                    self.check(fg, bg, self.TEXT)

    def test_text_on_buttons(self):
        self.check("text", "accent", self.TEXT)
        self.check("text", "accent-hover", self.TEXT)

    def test_ui_colours(self):
        for fg in ("gold", "muted", "accent-2"):
            with self.subTest(fg=fg):
                self.check(fg, "bg", self.UI)

    def test_accent_is_not_enough_for_text(self):
        # Documents why --accent must never be used as a text colour.
        self.assertLess(contrast(self.t["accent"], self.t["bg"]), self.TEXT)
