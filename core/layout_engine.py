"""
core/layout_engine.py

Professional layout engine for HG Tile Studio

Features:
- Grid layout (auto-fit columns/rows)
- Space-between / Space-around / Space-evenly
- Packed layout
- Per-image width and height
- Separate horizontal and vertical spacing
- Content always centered on page
- DPI-aware calculations
- Portrait / landscape safe
- Pagination support

Author: HARRY GRAPHICS
"""

from dataclasses import dataclass
from typing import List


# =========================================================
# UTILITIES
# =========================================================

def mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)


# =========================================================
# IMAGE PLACEMENT MODEL
# =========================================================

@dataclass
class LayoutItem:
    path: str

    x: int
    y: int

    w: int
    h: int

    scaling_mode: str = "fit"


# =========================================================
# PAGE MODEL
# =========================================================

@dataclass
class LayoutPage:
    width_px: int
    height_px: int

    items: List[LayoutItem]


# =========================================================
# LAYOUT SETTINGS
# =========================================================

@dataclass
class LayoutSettings:

    # ---------------------------------------------
    # PAGE
    # ---------------------------------------------

    page_width_mm: float = 210
    page_height_mm: float = 297

    dpi: int = 300

    # ---------------------------------------------
    # IMAGE SIZE (per-image)
    # ---------------------------------------------

    image_width_mm: float = 35
    image_height_mm: float = 45

    # ---------------------------------------------
    # SPACING (between images)
    # ---------------------------------------------

    horizontal_gap_mm: float = 2
    vertical_gap_mm: float = 2

    # ---------------------------------------------
    # LAYOUT
    # ---------------------------------------------

    layout_mode: str = "grid"

    # grid
    columns: int = 0
    rows: int = 0

    # ---------------------------------------------
    # IMAGE MODE
    # ---------------------------------------------

    scaling_mode: str = "fit"

    # ---------------------------------------------
    # AUTO FIT
    # ---------------------------------------------

    auto_fit: bool = True


# =========================================================
# LAYOUT ENGINE
# =========================================================

class LayoutEngine:

    SUPPORTED_LAYOUTS = [
        "grid",
        "space-between",
        "space-around",
        "space-evenly",
        "packed",
        "auto-fit",
    ]

    def __init__(self):
        pass

    # =====================================================
    # MAIN LAYOUT FUNCTION
    # =====================================================

    def generate_layout(
        self,
        image_paths,
        settings: LayoutSettings,
    ) -> List[LayoutPage]:

        if settings.layout_mode not in self.SUPPORTED_LAYOUTS:
            raise ValueError(
                f"Unsupported layout: {settings.layout_mode}"
            )

        page_width_px = mm_to_px(
            settings.page_width_mm,
            settings.dpi,
        )

        page_height_px = mm_to_px(
            settings.page_height_mm,
            settings.dpi,
        )

        # ---------------------------------------------
        # SPACING
        # ---------------------------------------------

        h_gap = mm_to_px(
            settings.horizontal_gap_mm,
            settings.dpi,
        )

        v_gap = mm_to_px(
            settings.vertical_gap_mm,
            settings.dpi,
        )

        # ---------------------------------------------
        # IMAGE SIZE
        # ---------------------------------------------

        img_w = mm_to_px(
            settings.image_width_mm,
            settings.dpi,
        )

        img_h = mm_to_px(
            settings.image_height_mm,
            settings.dpi,
        )

        # ---------------------------------------------
        # AUTO FIT: calculate columns and rows
        # ---------------------------------------------

        columns = settings.columns
        rows = settings.rows

        if settings.auto_fit or settings.layout_mode == "auto-fit":

            columns = max(
                1,
                (page_width_px + h_gap)
                // (img_w + h_gap)
            )

            rows = max(
                1,
                (page_height_px + v_gap)
                // (img_h + v_gap)
            )

        capacity = columns * rows

        if capacity <= 0:
            raise ValueError("Invalid layout capacity")

        # ---------------------------------------------
        # PAGINATION
        # ---------------------------------------------

        pages = []

        for start in range(0, len(image_paths), capacity):

            chunk = image_paths[start:start + capacity]

            items = self._generate_page_items(
                chunk,
                columns,
                rows,
                img_w,
                img_h,
                page_width_px,
                page_height_px,
                h_gap,
                v_gap,
                settings,
            )

            page = LayoutPage(
                width_px=page_width_px,
                height_px=page_height_px,
                items=items,
            )

            pages.append(page)

        return pages

    # =====================================================
    # GENERATE PAGE ITEMS
    # =====================================================

    def _generate_page_items(
        self,
        image_paths,
        columns,
        rows,
        img_w,
        img_h,
        page_width_px,
        page_height_px,
        h_gap,
        v_gap,
        settings,
    ):

        items = []

        # How many images actually placed this page
        actual_count = len(image_paths)
        actual_rows = (actual_count + columns - 1) // columns

        # ---------------------------------------------
        # DYNAMIC SPACING
        # ---------------------------------------------

        total_grid_width = (
            columns * img_w
        ) + (
            (columns - 1) * h_gap
        )

        total_grid_height = (
            actual_rows * img_h
        ) + (
            (actual_rows - 1) * v_gap
        )

        extra_x = max(
            0,
            page_width_px - total_grid_width
        )

        extra_y = max(
            0,
            page_height_px - total_grid_height
        )

        dynamic_h_gap = h_gap
        dynamic_v_gap = v_gap

        mode = settings.layout_mode.lower()

        # ---------------------------------------------
        # SPACE BETWEEN
        # ---------------------------------------------

        if mode == "space-between":

            if columns > 1:
                dynamic_h_gap = (
                    page_width_px
                    - (columns * img_w)
                ) // (columns - 1)

            if actual_rows > 1:
                dynamic_v_gap = (
                    page_height_px
                    - (actual_rows * img_h)
                ) // (actual_rows - 1)

        # ---------------------------------------------
        # SPACE AROUND
        # ---------------------------------------------

        elif mode == "space-around":

            dynamic_h_gap = (
                extra_x // (columns * 2)
            ) if columns > 0 else h_gap

            dynamic_v_gap = (
                extra_y // (actual_rows * 2)
            ) if actual_rows > 0 else v_gap

        # ---------------------------------------------
        # SPACE EVENLY
        # ---------------------------------------------

        elif mode == "space-evenly":

            dynamic_h_gap = (
                extra_x // (columns + 1)
            ) if columns > 0 else h_gap

            dynamic_v_gap = (
                extra_y // (actual_rows + 1)
            ) if actual_rows > 0 else v_gap

        # ---------------------------------------------
        # PACKED
        # ---------------------------------------------

        elif mode == "packed":

            dynamic_h_gap = 0
            dynamic_v_gap = 0

        # ---------------------------------------------
        # COMPUTE CONTENT SIZE AND CENTER ON PAGE
        # ---------------------------------------------

        content_width = (
            columns * img_w
        ) + (
            (columns - 1) * dynamic_h_gap
        )

        content_height = (
            actual_rows * img_h
        ) + (
            (actual_rows - 1) * dynamic_v_gap
        )

        # Always center the content on the page
        start_x = (page_width_px - content_width) // 2
        start_y = (page_height_px - content_height) // 2

        # ---------------------------------------------
        # PLACE ITEMS
        # ---------------------------------------------

        for index, path in enumerate(image_paths):

            row = index // columns
            col = index % columns

            x = start_x + (
                col * (img_w + dynamic_h_gap)
            )

            y = start_y + (
                row * (img_h + dynamic_v_gap)
            )

            item = LayoutItem(
                path=path,
                x=x,
                y=y,
                w=img_w,
                h=img_h,
                scaling_mode=settings.scaling_mode,
            )

            items.append(item)

        return items


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    image_paths = []

    for i in range(35):
        image_paths.append(f"image_{i}.jpg")

    settings = LayoutSettings(

        page_width_mm=210,
        page_height_mm=297,

        dpi=300,

        image_width_mm=35,
        image_height_mm=45,

        horizontal_gap_mm=2,
        vertical_gap_mm=2,

        layout_mode="grid",

        auto_fit=True,

        scaling_mode="fit",
    )

    engine = LayoutEngine()

    pages = engine.generate_layout(
        image_paths,
        settings,
    )

    print("\n========== LAYOUT ==========")

    print(f"Pages: {len(pages)}")

    for p_index, page in enumerate(pages):

        print(
            f"\nPage {p_index + 1}"
        )

        for item in page.items:

            print(
                item.path,
                item.x,
                item.y,
                item.w,
                item.h,
            )
