"""
utils/filename_builder.py

Professional filename generation system for HG Tile Studio

Features:
- Variable-based naming
- Auto numbering
- Date/time variables
- Template-safe filenames
- Invalid character cleanup
- Sequence formatting
- Batch-safe generation
- Collision protection
- Preview filename generation

Supported Variables:
- {page}
- {index}
- {date}
- {time}
- {datetime}
- {template}
- {width}
- {height}
- {dpi}
- {format}

Example:
sheet_{page}_{date}

Author: HARRY GRAPHICS
"""

import os
import re
from datetime import datetime


# =========================================================
# FILENAME BUILDER
# =========================================================

class FilenameBuilder:

    INVALID_CHARS = r'<>:"/\|?*'

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        pass

    # =====================================================
    # BUILD
    # =====================================================

    def build_filename(
        self,
        pattern,
        extension="png",

        page=1,
        index=1,

        template_name="template",

        width=None,
        height=None,

        dpi=None,

        ensure_safe=True,
    ):

        now = datetime.now()

        values = {

            "page":
                str(page).zfill(3),

            "index":
                str(index).zfill(3),

            "date":
                now.strftime("%Y%m%d"),

            "time":
                now.strftime("%H%M%S"),

            "datetime":
                now.strftime(
                    "%Y%m%d_%H%M%S"
                ),

            "template":
                template_name,

            "width":
                str(width) if width else "",

            "height":
                str(height) if height else "",

            "dpi":
                str(dpi) if dpi else "",

            "format":
                extension.lower(),
        }

        filename = pattern

        # ---------------------------------------------
        # REPLACE VARIABLES
        # ---------------------------------------------

        for key, value in values.items():

            filename = filename.replace(
                "{" + key + "}",
                value,
            )

        # ---------------------------------------------
        # CLEAN UNKNOWN VARIABLES
        # ---------------------------------------------

        filename = re.sub(
            r"\{.*?\}",
            "",
            filename,
        )

        # ---------------------------------------------
        # SAFE NAME
        # ---------------------------------------------

        if ensure_safe:

            filename = self.sanitize(
                filename
            )

        # ---------------------------------------------
        # REMOVE EXTRA SPACES
        # ---------------------------------------------

        filename = re.sub(
            r"\s+",
            "_",
            filename.strip(),
        )

        # ---------------------------------------------
        # REMOVE DOUBLE UNDERSCORES
        # ---------------------------------------------

        filename = re.sub(
            r"_+",
            "_",
            filename,
        )

        # ---------------------------------------------
        # ADD EXTENSION
        # ---------------------------------------------

        if not filename.lower().endswith(
            "." + extension.lower()
        ):

            filename += "." + extension.lower()

        return filename

    # =====================================================
    # SANITIZE
    # =====================================================

    def sanitize(
        self,
        filename,
    ):

        for char in self.INVALID_CHARS:

            filename = filename.replace(
                char,
                "_",
            )

        return filename.strip()

    # =====================================================
    # UNIQUE PATH
    # =====================================================

    def build_unique_path(
        self,
        directory,
        filename,
    ):

        base, ext = os.path.splitext(
            filename
        )

        candidate = os.path.join(
            directory,
            filename,
        )

        counter = 1

        while os.path.exists(candidate):

            candidate = os.path.join(

                directory,

                f"{base}_{counter}{ext}"

            )

            counter += 1

        return candidate

    # =====================================================
    # PREVIEW
    # =====================================================

    def preview(
        self,
        pattern,
        extension="png",
    ):

        return self.build_filename(
            pattern=pattern,
            extension=extension,
            page=1,
            index=1,
            template_name="sample",
            width=210,
            height=297,
            dpi=300,
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate_pattern(
        self,
        pattern,
    ):

        if not pattern:

            return False, "Pattern cannot be empty"

        invalid = [

            "<",
            ">",
            ":",
            '"',
            "/",
            "\\",
            "|",
            "?",
            "*",
        ]

        for ch in invalid:

            if ch in pattern:

                return (
                    False,
                    f"Invalid character: {ch}"
                )

        return True, "OK"

    # =====================================================
    # VARIABLES
    # =====================================================

    def available_variables(self):

        return [

            "{page}",
            "{index}",
            "{date}",
            "{time}",
            "{datetime}",
            "{template}",
            "{width}",
            "{height}",
            "{dpi}",
            "{format}",

        ]


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    builder = FilenameBuilder()

    # ---------------------------------------------
    # TEST PATTERNS
    # ---------------------------------------------

    patterns = [

        "sheet_{page}",

        "passport_{date}_{page}",

        "{template}_{datetime}",

        "A4_{width}x{height}_{dpi}",

        "job_{index}",

    ]

    print("\n========== TEST ==========\n")

    for pattern in patterns:

        filename = builder.build_filename(

            pattern=pattern,

            extension="png",

            page=12,

            index=44,

            template_name="passport",

            width=210,
            height=297,

            dpi=300,
        )

        print(pattern)
        print(" -> ", filename)
        print()

    # ---------------------------------------------
    # PREVIEW
    # ---------------------------------------------

    print("\n========== PREVIEW ==========\n")

    preview = builder.preview(
        "sheet_{page}_{date}"
    )

    print(preview)

    # ---------------------------------------------
    # VARIABLES
    # ---------------------------------------------

    print("\n========== VARIABLES ==========\n")

    for v in builder.available_variables():

        print(v)