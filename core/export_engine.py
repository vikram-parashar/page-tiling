"""
core/export_engine.py

Professional export engine for HG Tile Studio

Features:
- Export PNG
- Export JPG
- Export PDF
- Multi-page support
- DPI-aware rendering
- Background support
- Cut marks support
- Memory optimized
- Template-ready architecture

Author: HARRY GRAPHICS
"""

import os
import gc
from pathlib import Path

from PIL import Image, ImageDraw

from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

from core.cutmarks import (
    CutMarksGenerator,
    CutMarkSettings,
)


# =========================================================
# UTILITIES
# =========================================================

def mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)


def mm_to_points(mm):
    """
    PDF uses points
    1 inch = 72 points
    """
    return (mm / 25.4) * 72


# =========================================================
# EXPORT SETTINGS
# =========================================================

class ExportSettings:
    def __init__(
        self,
        export_format="PNG",
        dpi=300,
        jpg_quality=95,
        background_color=(255, 255, 255),
        transparent=False,
        pdf_multi_page=True,
    ):
        self.export_format = export_format.upper()
        self.dpi = dpi
        self.jpg_quality = jpg_quality
        self.background_color = background_color
        self.transparent = transparent
        self.pdf_multi_page = pdf_multi_page


# =========================================================
# PAGE MODEL
# =========================================================

class PageData:
    """
    Represents one export page.

    image_items format:
    [
        {
            "path": "...",
            "x": int,
            "y": int,
            "w": int,
            "h": int,
            "scaling_mode": "fit"
        }
    ]
    """

    def __init__(
        self,
        width_mm,
        height_mm,
        image_items,
        background_image=None,
    ):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.image_items = image_items
        self.background_image = background_image


# =========================================================
# EXPORT ENGINE
# =========================================================

class ExportEngine:

    SUPPORTED_FORMATS = ["PNG", "JPG", "PDF"]

    def __init__(self):
        pass

    # =====================================================
    # MAIN EXPORT
    # =====================================================

    def export_pages(
        self,
        pages,
        output_folder,
        filename_pattern,
        export_settings: ExportSettings,
        cutmark_settings: CutMarkSettings = None,
    ):

        os.makedirs(output_folder, exist_ok=True)

        export_format = export_settings.export_format

        if export_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {export_format}")

        if export_format == "PDF":
            self._export_pdf(
                pages,
                output_folder,
                filename_pattern,
                export_settings,
            )
        else:
            self._export_images(
                pages,
                output_folder,
                filename_pattern,
                export_settings,
                cutmark_settings,
            )

    # =====================================================
    # IMAGE EXPORT
    # =====================================================

    def _export_images(
        self,
        pages,
        output_folder,
        filename_pattern,
        export_settings,
        cutmark_settings,
    ):

        for page_index, page in enumerate(pages, start=1):

            filename = self._build_filename(
                filename_pattern,
                page_index,
                export_settings.export_format.lower(),
            )

            output_path = os.path.join(output_folder, filename)

            canvas = self._render_page(
                page,
                export_settings,
                cutmark_settings,
            )

            save_kwargs = {}

            if export_settings.export_format == "JPG":
                save_kwargs["quality"] = export_settings.jpg_quality

            canvas.save(
                output_path,
                dpi=(export_settings.dpi, export_settings.dpi),
                **save_kwargs
            )

            print(f"Exported: {output_path}")

            canvas.close()

            gc.collect()

    # =====================================================
    # PDF EXPORT
    # =====================================================

    def _export_pdf(
        self,
        pages,
        output_folder,
        filename_pattern,
        export_settings,
    ):

        filename = self._build_filename(
            filename_pattern,
            1,
            "pdf",
        )

        output_path = os.path.join(output_folder, filename)

        first_page = pages[0]

        page_width_pt = mm_to_points(first_page.width_mm)
        page_height_pt = mm_to_points(first_page.height_mm)

        pdf = pdf_canvas.Canvas(
            output_path,
            pagesize=(page_width_pt, page_height_pt),
        )

        for page in pages:

            rendered = self._render_page(
                page,
                export_settings,
                cutmark_settings=None,
            )

            img_reader = ImageReader(rendered)

            pdf.drawImage(
                img_reader,
                0,
                0,
                width=page_width_pt,
                height=page_height_pt,
            )

            pdf.showPage()

            rendered.close()

            gc.collect()

        pdf.save()

        print(f"Exported PDF: {output_path}")

    # =====================================================
    # PAGE RENDERING
    # =====================================================

    def _render_page(
        self,
        page: PageData,
        export_settings: ExportSettings,
        cutmark_settings: CutMarkSettings = None,
    ):

        dpi = export_settings.dpi

        width_px = mm_to_px(page.width_mm, dpi)
        height_px = mm_to_px(page.height_mm, dpi)

        # -----------------------------------------------
        # CREATE CANVAS
        # -----------------------------------------------

        if export_settings.transparent:
            canvas = Image.new(
                "RGBA",
                (width_px, height_px),
                (0, 0, 0, 0),
            )
        else:
            canvas = Image.new(
                "RGB",
                (width_px, height_px),
                export_settings.background_color,
            )

        draw = ImageDraw.Draw(canvas)

        # -----------------------------------------------
        # BACKGROUND IMAGE
        # -----------------------------------------------

        if page.background_image:

            try:
                bg = Image.open(page.background_image)

                bg = bg.resize((width_px, height_px))

                canvas.paste(bg, (0, 0))

                bg.close()

            except Exception as e:
                print(f"Background image error: {e}")

        # -----------------------------------------------
        # PLACE IMAGES
        # -----------------------------------------------

        rects = []

        for item in page.image_items:

            try:
                img = Image.open(item["path"])

                x = item["x"]
                y = item["y"]
                w = item["w"]
                h = item["h"]

                scaling_mode = item.get(
                    "scaling_mode",
                    "fit"
                )

                final_img = self._scale_image(
                    img,
                    w,
                    h,
                    scaling_mode,
                )

                paste_x = x
                paste_y = y

                canvas.paste(
                    final_img,
                    (paste_x, paste_y),
                )

                rects.append((x, y, w, h))

                img.close()
                final_img.close()

            except Exception as e:
                print(f"Image placement error: {e}")

        # -----------------------------------------------
        # CUT MARKS
        # -----------------------------------------------

        if cutmark_settings and cutmark_settings.enabled:

            cutmark_gen = CutMarksGenerator(dpi=dpi)

            cutmark_gen.draw_multiple(
                draw,
                rects,
                cutmark_settings,
            )

        return canvas

    # =====================================================
    # IMAGE SCALING
    # =====================================================

    def _scale_image(
        self,
        img,
        target_w,
        target_h,
        mode="fit",
    ):

        mode = mode.lower()

        if mode == "stretch":

            return img.resize((target_w, target_h))

        elif mode in ["fit", "contain"]:

            copy = img.copy()

            copy.thumbnail((target_w, target_h))

            bg = Image.new(
                "RGB",
                (target_w, target_h),
                (255, 255, 255),
            )

            x = (target_w - copy.width) // 2
            y = (target_h - copy.height) // 2

            bg.paste(copy, (x, y))

            copy.close()

            return bg

        elif mode in ["fill", "cover"]:

            ratio = max(
                target_w / img.width,
                target_h / img.height,
            )

            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)

            resized = img.resize((new_w, new_h))

            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2

            cropped = resized.crop(
                (
                    left,
                    top,
                    left + target_w,
                    top + target_h,
                )
            )

            resized.close()

            return cropped

        elif mode == "original":

            return img.copy()

        else:
            return img.resize((target_w, target_h))

    # =====================================================
    # FILENAME BUILDER
    # =====================================================

    def _build_filename(
        self,
        pattern,
        page_number,
        extension,
    ):

        from datetime import datetime

        now = datetime.now()

        filename = pattern

        filename = filename.replace(
            "{page}",
            str(page_number).zfill(3)
        )

        filename = filename.replace(
            "{date}",
            now.strftime("%Y%m%d")
        )

        filename = filename.replace(
            "{time}",
            now.strftime("%H%M%S")
        )

        filename = f"{filename}.{extension}"

        return filename


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    settings = ExportSettings(
        export_format="PNG",
        dpi=300,
    )

    cutmarks = CutMarkSettings(
        enabled=True,
        length_mm=3,
        thickness_px=2,
    )

    page = PageData(
        width_mm=210,
        height_mm=297,
        image_items=[
            {
                "path": "sample.jpg",
                "x": 100,
                "y": 100,
                "w": 400,
                "h": 500,
                "scaling_mode": "fit",
            }
        ]
    )

    engine = ExportEngine()

    engine.export_pages(
        pages=[page],
        output_folder="exports",
        filename_pattern="sheet_{page}",
        export_settings=settings,
        cutmark_settings=cutmarks,
    )