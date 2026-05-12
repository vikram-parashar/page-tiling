"""
core/cutmarks.py

Professional cut marks generator for print layouts.

Features:
- Draw crop/cut marks around image cells
- Adjustable:
    - length
    - thickness
    - offset
    - color
- Pillow-based rendering
- DPI-aware
- Supports page edges and internal image cells

Author: HARRY GRAPHICS
"""

from PIL import ImageDraw


class CutMarkSettings:
    def __init__(
        self,
        enabled=True,
        length_mm=3,
        thickness_px=1,
        offset_mm=1,
        color=(0, 0, 0),
    ):
        self.enabled = enabled
        self.length_mm = length_mm
        self.thickness_px = thickness_px
        self.offset_mm = offset_mm
        self.color = color


def mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)


class CutMarksGenerator:
    def __init__(self, dpi=300):
        self.dpi = dpi

    def draw_cut_marks(
        self,
        draw: ImageDraw.ImageDraw,
        x,
        y,
        w,
        h,
        settings: CutMarkSettings,
    ):
        """
        Draw cut marks around a rectangle.

        Parameters:
            draw      : PIL.ImageDraw object
            x, y      : top-left position
            w, h      : width and height
            settings  : CutMarkSettings object
        """

        if not settings.enabled:
            return

        length = mm_to_px(settings.length_mm, self.dpi)
        offset = mm_to_px(settings.offset_mm, self.dpi)

        t = settings.thickness_px
        c = settings.color

        # Outer positions
        left = x - offset
        right = x + w + offset
        top = y - offset
        bottom = y + h + offset

        # -------------------------
        # TOP LEFT
        # -------------------------

        # Horizontal
        draw.line(
            [(left - length, top), (left, top)],
            fill=c,
            width=t,
        )

        # Vertical
        draw.line(
            [(left, top - length), (left, top)],
            fill=c,
            width=t,
        )

        # -------------------------
        # TOP RIGHT
        # -------------------------

        draw.line(
            [(right, top), (right + length, top)],
            fill=c,
            width=t,
        )

        draw.line(
            [(right, top - length), (right, top)],
            fill=c,
            width=t,
        )

        # -------------------------
        # BOTTOM LEFT
        # -------------------------

        draw.line(
            [(left - length, bottom), (left, bottom)],
            fill=c,
            width=t,
        )

        draw.line(
            [(left, bottom), (left, bottom + length)],
            fill=c,
            width=t,
        )

        # -------------------------
        # BOTTOM RIGHT
        # -------------------------

        draw.line(
            [(right, bottom), (right + length, bottom)],
            fill=c,
            width=t,
        )

        draw.line(
            [(right, bottom), (right, bottom + length)],
            fill=c,
            width=t,
        )

    def draw_multiple(
        self,
        draw: ImageDraw.ImageDraw,
        rects,
        settings: CutMarkSettings,
    ):
        """
        Draw cut marks for multiple rectangles.

        rects format:
        [
            (x, y, w, h),
            ...
        ]
        """

        if not settings.enabled:
            return

        for rect in rects:
            self.draw_cut_marks(
                draw,
                rect[0],
                rect[1],
                rect[2],
                rect[3],
                settings,
            )


# ---------------------------------------------------
# TEST
# ---------------------------------------------------

if __name__ == "__main__":
    from PIL import Image

    DPI = 300

    img = Image.new("RGB", (2000, 1400), "white")
    draw = ImageDraw.Draw(img)

    settings = CutMarkSettings(
        enabled=True,
        length_mm=4,
        thickness_px=2,
        offset_mm=1,
        color=(0, 0, 0),
    )

    generator = CutMarksGenerator(dpi=DPI)

    rects = [
        (200, 200, 300, 400),
        (700, 200, 300, 400),
        (1200, 200, 300, 400),
    ]

    # Draw image placeholders
    for r in rects:
        draw.rectangle(
            [r[0], r[1], r[0] + r[2], r[1] + r[3]],
            outline="blue",
            width=2,
        )

    # Draw cut marks
    generator.draw_multiple(draw, rects, settings)

    img.save("cutmarks_test.png")

    print("Saved: cutmarks_test.png")