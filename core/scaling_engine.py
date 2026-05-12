"""
core/scaling_engine.py

Professional image scaling engine for HG Tile Studio

Features:
- Fit
- Fill
- Stretch
- Original
- Contain
- Cover
- Smart crop placeholder
- DPI-safe resizing
- Alpha transparency support
- High quality resizing
- Memory optimized

Author: HARRY GRAPHICS
"""

from PIL import Image, ImageOps


# =========================================================
# SCALING ENGINE
# =========================================================

class ScalingEngine:

    SUPPORTED_MODES = [
        "fit",
        "fill",
        "stretch",
        "original",
        "contain",
        "cover",
        "smart-crop",
    ]

    def __init__(self):
        pass

    # =====================================================
    # MAIN SCALE FUNCTION
    # =====================================================

    def scale_image(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int,
        mode="fit",
        background_color=(255, 255, 255),
    ) -> Image.Image:

        mode = mode.lower()

        if mode not in self.SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported scaling mode: {mode}"
            )

        # ---------------------------------------------
        # SAFETY COPY
        # ---------------------------------------------

        img = image.copy()

        # ---------------------------------------------
        # MODE HANDLING
        # ---------------------------------------------

        if mode in ["fit", "contain"]:

            return self._fit(
                img,
                target_width,
                target_height,
                background_color,
            )

        elif mode in ["fill", "cover"]:

            return self._fill(
                img,
                target_width,
                target_height,
            )

        elif mode == "stretch":

            return self._stretch(
                img,
                target_width,
                target_height,
            )

        elif mode == "original":

            return self._original(
                img,
                target_width,
                target_height,
                background_color,
            )

        elif mode == "smart-crop":

            return self._smart_crop(
                img,
                target_width,
                target_height,
            )

        else:

            return self._fit(
                img,
                target_width,
                target_height,
                background_color,
            )

    # =====================================================
    # FIT / CONTAIN
    # =====================================================

    def _fit(
        self,
        img,
        target_width,
        target_height,
        background_color,
    ):

        # Maintain aspect ratio
        img.thumbnail(
            (target_width, target_height),
            Image.LANCZOS,
        )

        background = self._create_background(
            target_width,
            target_height,
            background_color,
        )

        x = (target_width - img.width) // 2
        y = (target_height - img.height) // 2

        self._safe_paste(
            background,
            img,
            (x, y),
        )

        return background

    # =====================================================
    # FILL / COVER
    # =====================================================

    def _fill(
        self,
        img,
        target_width,
        target_height,
    ):

        ratio = max(
            target_width / img.width,
            target_height / img.height,
        )

        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)

        resized = img.resize(
            (new_width, new_height),
            Image.LANCZOS,
        )

        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2

        cropped = resized.crop(
            (
                left,
                top,
                left + target_width,
                top + target_height,
            )
        )

        resized.close()

        return cropped

    # =====================================================
    # STRETCH
    # =====================================================

    def _stretch(
        self,
        img,
        target_width,
        target_height,
    ):

        return img.resize(
            (target_width, target_height),
            Image.LANCZOS,
        )

    # =====================================================
    # ORIGINAL
    # =====================================================

    def _original(
        self,
        img,
        target_width,
        target_height,
        background_color,
    ):

        background = self._create_background(
            target_width,
            target_height,
            background_color,
        )

        x = (target_width - img.width) // 2
        y = (target_height - img.height) // 2

        self._safe_paste(
            background,
            img,
            (x, y),
        )

        return background

    # =====================================================
    # SMART CROP (PLACEHOLDER)
    # =====================================================

    def _smart_crop(
        self,
        img,
        target_width,
        target_height,
    ):

        """
        Future AI-based face-aware crop.

        Currently fallback to cover mode.
        """

        return self._fill(
            img,
            target_width,
            target_height,
        )

    # =====================================================
    # CREATE BACKGROUND
    # =====================================================

    def _create_background(
        self,
        width,
        height,
        color,
    ):

        return Image.new(
            "RGB",
            (width, height),
            color,
        )

    # =====================================================
    # SAFE PASTE
    # =====================================================

    def _safe_paste(
        self,
        background,
        image,
        position,
    ):

        if image.mode == "RGBA":

            background.paste(
                image,
                position,
                image,
            )

        else:

            background.paste(
                image,
                position,
            )

    # =====================================================
    # AUTO ORIENTATION HELPER
    # =====================================================

    def auto_rotate_if_needed(
        self,
        image,
        target_width,
        target_height,
    ):

        """
        Auto rotate portrait/landscape
        if orientation mismatch detected.
        """

        img_ratio = image.width / image.height
        target_ratio = target_width / target_height

        # Opposite orientation
        if (
            (img_ratio > 1 and target_ratio < 1)
            or
            (img_ratio < 1 and target_ratio > 1)
        ):

            return image.rotate(
                90,
                expand=True,
            )

        return image

    # =====================================================
    # ADD PADDING
    # =====================================================

    def add_padding(
        self,
        image,
        left,
        top,
        right,
        bottom,
        color=(255, 255, 255),
    ):

        return ImageOps.expand(
            image,
            border=(left, top, right, bottom),
            fill=color,
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    engine = ScalingEngine()

    img = Image.open("sample.jpg")

    modes = [
        "fit",
        "fill",
        "stretch",
        "original",
        "contain",
        "cover",
        "smart-crop",
    ]

    for mode in modes:

        result = engine.scale_image(
            img,
            target_width=600,
            target_height=800,
            mode=mode,
        )

        result.save(f"test_{mode}.jpg")

        result.close()

        print(f"Saved: test_{mode}.jpg")

    img.close()