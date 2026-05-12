"""
core/image_loader.py

High-performance image loading system for HG Tile Studio

Features:
- Recursive folder scanning
- Supported image filtering
- Corrupted file protection
- Thumbnail generation
- Lazy loading helpers
- Memory optimized
- Multithread-ready structure
- DPI-safe loading

Author: HARRY GRAPHICS
"""

import os
import gc
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image, UnidentifiedImageError


# =========================================================
# SUPPORTED FORMATS
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
    ".tiff",
}


# =========================================================
# IMAGE DATA MODEL
# =========================================================

@dataclass
class ImageItem:
    path: str
    filename: str
    extension: str

    width: int = 0
    height: int = 0

    dpi_x: int = 72
    dpi_y: int = 72

    file_size: int = 0

    thumbnail = None

    corrupted: bool = False


# =========================================================
# IMAGE LOADER
# =========================================================

class ImageLoader:

    def __init__(
        self,
        include_subfolders=True,
        generate_thumbnails=True,
        thumbnail_size=(256, 256),
    ):

        self.include_subfolders = include_subfolders
        self.generate_thumbnails = generate_thumbnails
        self.thumbnail_size = thumbnail_size

        self.images: List[ImageItem] = []

    # =====================================================
    # SCAN FOLDER
    # =====================================================

    def scan_folder(
        self,
        folder_path: str,
    ) -> List[ImageItem]:

        self.images.clear()

        if not os.path.exists(folder_path):
            raise FileNotFoundError(folder_path)

        if self.include_subfolders:
            self._scan_recursive(folder_path)
        else:
            self._scan_single(folder_path)

        return self.images

    # =====================================================
    # NON-RECURSIVE SCAN
    # =====================================================

    def _scan_single(self, folder_path):

        for entry in os.scandir(folder_path):

            if entry.is_file():

                self._process_file(entry.path)

    # =====================================================
    # RECURSIVE SCAN
    # =====================================================

    def _scan_recursive(self, folder_path):

        for root, dirs, files in os.walk(folder_path):

            # Ignore hidden folders
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".")
            ]

            for file in files:

                path = os.path.join(root, file)

                self._process_file(path)

    # =====================================================
    # PROCESS IMAGE FILE
    # =====================================================

    def _process_file(self, file_path):

        ext = Path(file_path).suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            return

        try:

            with Image.open(file_path) as img:

                width, height = img.size

                dpi = img.info.get("dpi", (72, 72))

                item = ImageItem(
                    path=file_path,
                    filename=os.path.basename(file_path),
                    extension=ext,
                    width=width,
                    height=height,
                    dpi_x=int(dpi[0]),
                    dpi_y=int(dpi[1]),
                    file_size=os.path.getsize(file_path),
                )

                # -----------------------------------------
                # THUMBNAIL GENERATION
                # -----------------------------------------

                if self.generate_thumbnails:

                    item.thumbnail = self.generate_thumbnail(
                        file_path
                    )

                self.images.append(item)

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):

            corrupted_item = ImageItem(
                path=file_path,
                filename=os.path.basename(file_path),
                extension=ext,
                corrupted=True,
            )

            self.images.append(corrupted_item)

    # =====================================================
    # THUMBNAIL GENERATION
    # =====================================================

    def generate_thumbnail(
        self,
        image_path,
        size=None,
    ):

        if size is None:
            size = self.thumbnail_size

        try:

            with Image.open(image_path) as img:

                # Convert safely
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                thumb = img.copy()

                thumb.thumbnail(
                    size,
                    Image.LANCZOS,
                )

                return thumb

        except Exception as e:

            print(
                f"Thumbnail generation failed: {image_path}"
            )

            print(e)

            return None

    # =====================================================
    # LAZY LOAD FULL IMAGE
    # =====================================================

    def load_full_image(
        self,
        image_item: ImageItem,
    ) -> Optional[Image.Image]:

        try:

            img = Image.open(image_item.path)

            return img

        except Exception as e:

            print(f"Failed loading image: {e}")

            return None

    # =====================================================
    # MEMORY CLEANUP
    # =====================================================

    def clear_thumbnails(self):

        for item in self.images:

            if item.thumbnail:

                try:
                    item.thumbnail.close()
                except:
                    pass

                item.thumbnail = None

        gc.collect()

    # =====================================================
    # FILTER IMAGES
    # =====================================================

    def get_valid_images(self):

        return [
            img for img in self.images
            if not img.corrupted
        ]

    def get_corrupted_images(self):

        return [
            img for img in self.images
            if img.corrupted
        ]

    # =====================================================
    # IMAGE STATISTICS
    # =====================================================

    def get_statistics(self):

        valid = len(self.get_valid_images())
        corrupted = len(self.get_corrupted_images())

        total_size = sum(
            img.file_size
            for img in self.get_valid_images()
        )

        return {
            "total_images": len(self.images),
            "valid_images": valid,
            "corrupted_images": corrupted,
            "total_size_mb": round(
                total_size / (1024 * 1024),
                2
            ),
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    loader = ImageLoader(
        include_subfolders=True,
        generate_thumbnails=True,
        thumbnail_size=(128, 128),
    )

    folder = "sample_images"

    images = loader.scan_folder(folder)

    stats = loader.get_statistics()

    print("\n========== STATS ==========")

    for k, v in stats.items():
        print(f"{k}: {v}")

    print("\n========== FILES ==========")

    for item in images:

        print(
            f"{item.filename} | "
            f"{item.width}x{item.height} | "
            f"Corrupted={item.corrupted}"
        )

    # Cleanup
    loader.clear_thumbnails()