"""Template helpers for the temple screens (ADR 0017)."""

from django import template

register = template.Library()


@register.filter
def focus_classes(image) -> str:
    """CSS classes placing a cropped full-screen image or video at the
    image's focal point (set by the editor in the Wagtail admin), in steps of
    10 %: e.g. "focus-x-7 focus-y-5". Classes, because the CSP allows no
    style attributes. Centre when there is no image or focal point."""
    if not image or not image.width or not image.height:
        return "focus-x-5 focus-y-5"
    if image.focal_point_x is None or image.focal_point_y is None:
        return "focus-x-5 focus-y-5"
    x = round(image.focal_point_x / image.width * 10)
    y = round(image.focal_point_y / image.height * 10)
    return f"focus-x-{min(max(x, 0), 10)} focus-y-{min(max(y, 0), 10)}"
