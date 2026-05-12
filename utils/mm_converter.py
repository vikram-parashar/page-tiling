"""
utils/mm_converter.py

Professional measurement conversion utilities
for HG Tile Studio

Features:
- mm ↔ px
- inch ↔ px
- cm ↔ px
- pt ↔ px
- mm ↔ inch
- cm ↔ mm
- DPI-aware conversions
- Float-safe calculations
- Geometry helpers
- Print-safe rounding

Author: HARRY GRAPHICS
"""

from decimal import Decimal


# =========================================================
# CONSTANTS
# =========================================================

MM_PER_INCH = Decimal("25.4")

CM_PER_INCH = Decimal("2.54")

POINTS_PER_INCH = Decimal("72")


# =========================================================
# MM ↔ PX
# =========================================================

def mm_to_px(
    mm,
    dpi=300,
    rounding=True,
):

    px = (
        Decimal(str(mm))
        / MM_PER_INCH
    ) * Decimal(str(dpi))

    return int(round(px)) if rounding else float(px)


def px_to_mm(
    px,
    dpi=300,
    rounding=2,
):

    mm = (
        Decimal(str(px))
        / Decimal(str(dpi))
    ) * MM_PER_INCH

    return round(float(mm), rounding)


# =========================================================
# CM ↔ PX
# =========================================================

def cm_to_px(
    cm,
    dpi=300,
    rounding=True,
):

    px = (
        Decimal(str(cm))
        / CM_PER_INCH
    ) * Decimal(str(dpi))

    return int(round(px)) if rounding else float(px)


def px_to_cm(
    px,
    dpi=300,
    rounding=2,
):

    cm = (
        Decimal(str(px))
        / Decimal(str(dpi))
    ) * CM_PER_INCH

    return round(float(cm), rounding)


# =========================================================
# INCH ↔ PX
# =========================================================

def inch_to_px(
    inch,
    dpi=300,
    rounding=True,
):

    px = (
        Decimal(str(inch))
        * Decimal(str(dpi))
    )

    return int(round(px)) if rounding else float(px)


def px_to_inch(
    px,
    dpi=300,
    rounding=3,
):

    inch = (
        Decimal(str(px))
        / Decimal(str(dpi))
    )

    return round(float(inch), rounding)


# =========================================================
# MM ↔ INCH
# =========================================================

def mm_to_inch(
    mm,
    rounding=4,
):

    inch = (
        Decimal(str(mm))
        / MM_PER_INCH
    )

    return round(float(inch), rounding)


def inch_to_mm(
    inch,
    rounding=3,
):

    mm = (
        Decimal(str(inch))
        * MM_PER_INCH
    )

    return round(float(mm), rounding)


# =========================================================
# CM ↔ MM
# =========================================================

def cm_to_mm(
    cm,
):

    return float(
        Decimal(str(cm)) * 10
    )


def mm_to_cm(
    mm,
    rounding=3,
):

    cm = (
        Decimal(str(mm)) / 10
    )

    return round(float(cm), rounding)


# =========================================================
# PT ↔ PX
# =========================================================

def pt_to_px(
    pt,
    dpi=300,
    rounding=True,
):

    px = (
        Decimal(str(pt))
        / POINTS_PER_INCH
    ) * Decimal(str(dpi))

    return int(round(px)) if rounding else float(px)


def px_to_pt(
    px,
    dpi=300,
    rounding=2,
):

    pt = (
        Decimal(str(px))
        / Decimal(str(dpi))
    ) * POINTS_PER_INCH

    return round(float(pt), rounding)


# =========================================================
# MM ↔ PT
# =========================================================

def mm_to_pt(
    mm,
    rounding=2,
):

    pt = (
        Decimal(str(mm))
        / MM_PER_INCH
    ) * POINTS_PER_INCH

    return round(float(pt), rounding)


def pt_to_mm(
    pt,
    rounding=3,
):

    mm = (
        Decimal(str(pt))
        / POINTS_PER_INCH
    ) * MM_PER_INCH

    return round(float(mm), rounding)


# =========================================================
# PAGE AREA
# =========================================================

def calculate_area_mm(
    width_mm,
    height_mm,
    rounding=2,
):

    area = (
        Decimal(str(width_mm))
        * Decimal(str(height_mm))
    )

    return round(float(area), rounding)


# =========================================================
# ASPECT RATIO
# =========================================================

def aspect_ratio(
    width,
    height,
    rounding=4,
):

    if height == 0:
        return 0

    ratio = (
        Decimal(str(width))
        / Decimal(str(height))
    )

    return round(float(ratio), rounding)


# =========================================================
# FIT INSIDE RECTANGLE
# =========================================================

def fit_inside(
    source_w,
    source_h,
    target_w,
    target_h,
):

    scale = min(
        target_w / source_w,
        target_h / source_h,
    )

    return (

        int(source_w * scale),

        int(source_h * scale),

    )


# =========================================================
# COVER RECTANGLE
# =========================================================

def cover_area(
    source_w,
    source_h,
    target_w,
    target_h,
):

    scale = max(
        target_w / source_w,
        target_h / source_h,
    )

    return (

        int(source_w * scale),

        int(source_h * scale),

    )


# =========================================================
# SAFE ROUNDING
# =========================================================

def safe_round(
    value,
    decimals=2,
):

    return round(
        float(
            Decimal(str(value))
        ),
        decimals,
    )


# =========================================================
# BLEED ADDITION
# =========================================================

def add_bleed(
    width_mm,
    height_mm,
    bleed_mm,
):

    return (

        width_mm + (bleed_mm * 2),

        height_mm + (bleed_mm * 2),

    )


# =========================================================
# REMOVE BLEED
# =========================================================

def remove_bleed(
    width_mm,
    height_mm,
    bleed_mm,
):

    return (

        width_mm - (bleed_mm * 2),

        height_mm - (bleed_mm * 2),

    )


# =========================================================
# SAFE PRINT MARGIN
# =========================================================

def safe_print_area(
    width_mm,
    height_mm,
    margin_mm,
):

    return (

        width_mm - (margin_mm * 2),

        height_mm - (margin_mm * 2),

    )


# =========================================================
# ORIENTATION
# =========================================================

def apply_orientation(
    width,
    height,
    orientation="portrait",
):

    orientation = orientation.lower()

    if orientation == "landscape":

        if height > width:

            return (
                height,
                width,
            )

    else:

        if width > height:

            return (
                height,
                width,
            )

    return (
        width,
        height,
    )


# =========================================================
# PAPER PRESETS
# =========================================================

PAPER_PRESETS_MM = {

    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),

    "Letter": (216, 279),
    "Legal": (216, 356),

}


# =========================================================
# GET PAPER SIZE
# =========================================================

def get_paper_size(
    name,
):

    return PAPER_PRESETS_MM.get(
        name,
        None,
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========== MM CONVERTER TEST ==========\n")

    # MM TO PX

    print(
        "35mm @300dpi =",
        mm_to_px(35, 300),
        "px"
    )

    # PX TO MM

    print(
        "413px @300dpi =",
        px_to_mm(413, 300),
        "mm"
    )

    # CM TO PX

    print(
        "5cm @300dpi =",
        cm_to_px(5, 300),
        "px"
    )

    # MM TO INCH

    print(
        "35mm =",
        mm_to_inch(35),
        "inch"
    )

    # PT TO MM

    print(
        "72pt =",
        pt_to_mm(72),
        "mm"
    )

    # FIT INSIDE

    print(
        "Fit:",
        fit_inside(
            1200,
            1800,
            600,
            600,
        )
    )

    # COVER

    print(
        "Cover:",
        cover_area(
            1200,
            1800,
            600,
            600,
        )
    )

    # PAPER SIZE

    print(
        "A4:",
        get_paper_size("A4")
    )

    # ORIENTATION

    print(
        "Landscape:",
        apply_orientation(
            210,
            297,
            "landscape"
        )
    )