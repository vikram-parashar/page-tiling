"""
utils/dpi.py

DPI and print utility system for HG Tile Studio

Features:
- mm ↔ px conversion
- inch ↔ px conversion
- DPI calculations
- Print size calculations
- Aspect ratio helpers
- Recommended print resolutions
- Safe print validation
- Bleed calculations

Author: HARRY GRAPHICS
"""

from dataclasses import dataclass


# =========================================================
# CONSTANTS
# =========================================================

MM_PER_INCH = 25.4


# =========================================================
# DPI PROFILE
# =========================================================

@dataclass
class DPIProfile:

    name: str
    dpi: int
    description: str


# =========================================================
# COMMON DPI PROFILES
# =========================================================

COMMON_DPI_PROFILES = [

    DPIProfile(
        "Screen",
        72,
        "Low quality screen preview",
    ),

    DPIProfile(
        "Draft",
        150,
        "Fast low quality printing",
    ),

    DPIProfile(
        "Standard",
        300,
        "Professional print quality",
    ),

    DPIProfile(
        "High Quality",
        600,
        "Ultra sharp print",
    ),

    DPIProfile(
        "Photo",
        1200,
        "Premium photo printing",
    ),
]


# =========================================================
# MM TO PX
# =========================================================

def mm_to_px(
    mm,
    dpi,
):

    return int(
        (mm / MM_PER_INCH) * dpi
    )


# =========================================================
# PX TO MM
# =========================================================

def px_to_mm(
    px,
    dpi,
):

    return (
        px / dpi
    ) * MM_PER_INCH


# =========================================================
# INCH TO PX
# =========================================================

def inch_to_px(
    inch,
    dpi,
):

    return int(
        inch * dpi
    )


# =========================================================
# PX TO INCH
# =========================================================

def px_to_inch(
    px,
    dpi,
):

    return px / dpi


# =========================================================
# MM TO INCH
# =========================================================

def mm_to_inch(
    mm,
):

    return mm / MM_PER_INCH


# =========================================================
# INCH TO MM
# =========================================================

def inch_to_mm(
    inch,
):

    return inch * MM_PER_INCH


# =========================================================
# CALCULATE PRINT SIZE
# =========================================================

def calculate_print_size_mm(
    width_px,
    height_px,
    dpi,
):

    width_mm = px_to_mm(
        width_px,
        dpi,
    )

    height_mm = px_to_mm(
        height_px,
        dpi,
    )

    return (
        round(width_mm, 2),
        round(height_mm, 2),
    )


# =========================================================
# REQUIRED PIXELS
# =========================================================

def required_pixels_for_print(
    width_mm,
    height_mm,
    dpi,
):

    width_px = mm_to_px(
        width_mm,
        dpi,
    )

    height_px = mm_to_px(
        height_mm,
        dpi,
    )

    return (
        width_px,
        height_px,
    )


# =========================================================
# ASPECT RATIO
# =========================================================

def calculate_aspect_ratio(
    width,
    height,
):

    if height == 0:
        return 0

    return width / height


# =========================================================
# FIT INSIDE
# =========================================================

def fit_inside(
    source_width,
    source_height,
    target_width,
    target_height,
):

    ratio = min(

        target_width / source_width,

        target_height / source_height,

    )

    return (

        int(source_width * ratio),

        int(source_height * ratio),

    )


# =========================================================
# COVER AREA
# =========================================================

def cover_area(
    source_width,
    source_height,
    target_width,
    target_height,
):

    ratio = max(

        target_width / source_width,

        target_height / source_height,

    )

    return (

        int(source_width * ratio),

        int(source_height * ratio),

    )


# =========================================================
# SAFE PRINT CHECK
# =========================================================

def is_print_quality_good(
    image_width_px,
    image_height_px,
    target_width_mm,
    target_height_mm,
    minimum_dpi=300,
):

    required_w = mm_to_px(
        target_width_mm,
        minimum_dpi,
    )

    required_h = mm_to_px(
        target_height_mm,
        minimum_dpi,
    )

    return (

        image_width_px >= required_w

        and

        image_height_px >= required_h

    )


# =========================================================
# DPI FROM IMAGE SIZE
# =========================================================

def calculate_effective_dpi(
    image_width_px,
    image_height_px,
    print_width_mm,
    print_height_mm,
):

    width_inch = mm_to_inch(
        print_width_mm
    )

    height_inch = mm_to_inch(
        print_height_mm
    )

    dpi_x = (
        image_width_px / width_inch
    )

    dpi_y = (
        image_height_px / height_inch
    )

    return (
        round(dpi_x, 2),
        round(dpi_y, 2),
    )


# =========================================================
# BLEED
# =========================================================

def add_bleed_mm(
    width_mm,
    height_mm,
    bleed_mm,
):

    return (

        width_mm + (bleed_mm * 2),

        height_mm + (bleed_mm * 2),

    )


# =========================================================
# SAFE MARGIN
# =========================================================

def safe_margin_area(
    width_mm,
    height_mm,
    margin_mm,
):

    return (

        width_mm - (margin_mm * 2),

        height_mm - (margin_mm * 2),

    )


# =========================================================
# PAPER PRESETS
# =========================================================

PAPER_SIZES_MM = {

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

def get_paper_size_mm(
    name,
):

    return PAPER_SIZES_MM.get(
        name,
        None,
    )


# =========================================================
# ORIENTATION
# =========================================================

def apply_orientation(
    width_mm,
    height_mm,
    orientation="portrait",
):

    orientation = orientation.lower()

    if orientation == "landscape":

        if height_mm > width_mm:

            return (
                height_mm,
                width_mm,
            )

    else:

        if width_mm > height_mm:

            return (
                height_mm,
                width_mm,
            )

    return (
        width_mm,
        height_mm,
    )


# =========================================================
# RECOMMENDED DPI
# =========================================================

def recommend_dpi(
    use_case="print",
):

    table = {

        "screen": 72,

        "draft": 150,

        "print": 300,

        "photo": 600,

        "fine-art": 1200,

    }

    return table.get(
        use_case.lower(),
        300,
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========== DPI TEST ==========\n")

    # MM TO PX

    px = mm_to_px(
        35,
        300,
    )

    print("35mm @300dpi =", px)

    # PX TO MM

    mm = px_to_mm(
        px,
        300,
    )

    print("Back to mm =", mm)

    # PRINT SIZE

    size = calculate_print_size_mm(
        1200,
        1800,
        300,
    )

    print("Print size =", size)

    # REQUIRED PIXELS

    req = required_pixels_for_print(
        35,
        45,
        300,
    )

    print("Required pixels =", req)

    # QUALITY CHECK

    quality = is_print_quality_good(
        1200,
        1800,
        35,
        45,
    )

    print("Quality OK =", quality)

    # EFFECTIVE DPI

    dpi = calculate_effective_dpi(
        1200,
        1800,
        35,
        45,
    )

    print("Effective DPI =", dpi)

    # ORIENTATION

    paper = apply_orientation(
        210,
        297,
        "landscape",
    )

    print("Landscape =", paper)