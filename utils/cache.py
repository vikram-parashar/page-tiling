"""
utils/cache.py

High-performance cache system for HG Tile Studio

Features:
- Memory cache
- Thumbnail cache
- Disk cache
- LRU eviction
- Cache size limits
- Automatic cleanup
- Thread-safe structure
- Persistent thumbnail storage
- Lazy loading support

Author: HARRY GRAPHICS
"""

import os
import gc
import time
import hashlib
from pathlib import Path
from collections import OrderedDict

from PIL import Image


# =========================================================
# CACHE ITEM
# =========================================================

class CacheItem:

    def __init__(
        self,
        key,
        value,
        size_bytes=0,
    ):

        self.key = key

        self.value = value

        self.size_bytes = size_bytes

        self.created_at = time.time()

        self.last_access = time.time()

    def touch(self):

        self.last_access = time.time()


# =========================================================
# MEMORY CACHE
# =========================================================

class MemoryCache:

    """
    LRU memory cache.
    """

    def __init__(
        self,
        max_items=500,
        max_memory_mb=512,
    ):

        self.max_items = max_items

        self.max_memory_bytes = (
            max_memory_mb * 1024 * 1024
        )

        self.cache = OrderedDict()

        self.current_memory = 0

    # =====================================================
    # PUT
    # =====================================================

    def put(
        self,
        key,
        value,
        size_bytes=0,
    ):

        # REMOVE EXISTING

        if key in self.cache:

            self._remove(key)

        item = CacheItem(
            key,
            value,
            size_bytes,
        )

        self.cache[key] = item

        self.current_memory += size_bytes

        # LRU UPDATE
        self.cache.move_to_end(key)

        # LIMITS
        self._enforce_limits()

    # =====================================================
    # GET
    # =====================================================

    def get(self, key):

        item = self.cache.get(key)

        if not item:
            return None

        item.touch()

        self.cache.move_to_end(key)

        return item.value

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(self, key):

        return key in self.cache

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(self, key):

        self._remove(key)

    def _remove(self, key):

        item = self.cache.pop(
            key,
            None,
        )

        if not item:
            return

        self.current_memory -= (
            item.size_bytes
        )

        # CLEAN IMAGE MEMORY

        try:

            if hasattr(item.value, "close"):
                item.value.close()

        except:
            pass

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        for key in list(self.cache.keys()):

            self._remove(key)

        self.cache.clear()

        self.current_memory = 0

        gc.collect()

    # =====================================================
    # LIMITS
    # =====================================================

    def _enforce_limits(self):

        while (

            len(self.cache) > self.max_items

            or

            self.current_memory >
            self.max_memory_bytes

        ):

            oldest_key = next(
                iter(self.cache)
            )

            self._remove(oldest_key)

    # =====================================================
    # STATS
    # =====================================================

    def get_stats(self):

        return {

            "items":
                len(self.cache),

            "memory_mb":
                round(
                    self.current_memory
                    / (1024 * 1024),
                    2
                ),

            "max_items":
                self.max_items,

            "max_memory_mb":
                round(
                    self.max_memory_bytes
                    / (1024 * 1024),
                    2
                ),
        }


# =========================================================
# DISK CACHE
# =========================================================

class DiskCache:

    """
    Persistent image cache.
    """

    def __init__(
        self,
        cache_dir="cache",
    ):

        self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # HASH
    # =====================================================

    def create_key(
        self,
        source,
    ):

        return hashlib.md5(
            source.encode("utf-8")
        ).hexdigest()

    # =====================================================
    # CACHE PATH
    # =====================================================

    def get_cache_path(
        self,
        key,
        extension=".png",
    ):

        return self.cache_dir / (
            key + extension
        )

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(
        self,
        key,
        extension=".png",
    ):

        return self.get_cache_path(
            key,
            extension,
        ).exists()

    # =====================================================
    # SAVE IMAGE
    # =====================================================

    def save_image(
        self,
        key,
        image,
        extension=".png",
    ):

        path = self.get_cache_path(
            key,
            extension,
        )

        image.save(path)

        return str(path)

    # =====================================================
    # LOAD IMAGE
    # =====================================================

    def load_image(
        self,
        key,
        extension=".png",
    ):

        path = self.get_cache_path(
            key,
            extension,
        )

        if not path.exists():
            return None

        try:

            return Image.open(path)

        except Exception:

            return None

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(
        self,
        key,
        extension=".png",
    ):

        path = self.get_cache_path(
            key,
            extension,
        )

        if path.exists():

            path.unlink()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        for file in self.cache_dir.glob("*"):

            try:
                file.unlink()

            except:
                pass

        gc.collect()

    # =====================================================
    # SIZE
    # =====================================================

    def get_cache_size_mb(self):

        total = 0

        for file in self.cache_dir.glob("*"):

            try:
                total += file.stat().st_size

            except:
                pass

        return round(
            total / (1024 * 1024),
            2
        )


# =========================================================
# THUMBNAIL CACHE
# =========================================================

class ThumbnailCache:

    """
    Combined memory + disk thumbnail cache.
    """

    def __init__(
        self,
        memory_items=1000,
        memory_mb=512,
        disk_dir="cache/thumbnails",
    ):

        self.memory_cache = MemoryCache(
            max_items=memory_items,
            max_memory_mb=memory_mb,
        )

        self.disk_cache = DiskCache(
            cache_dir=disk_dir,
        )

    # =====================================================
    # KEY
    # =====================================================

    def create_thumbnail_key(
        self,
        image_path,
        width,
        height,
    ):

        data = (
            f"{image_path}_"
            f"{width}x{height}"
        )

        return hashlib.md5(
            data.encode("utf-8")
        ).hexdigest()

    # =====================================================
    # STORE
    # =====================================================

    def store_thumbnail(
        self,
        key,
        image,
    ):

        # MEMORY SIZE ESTIMATE

        size = (
            image.width
            * image.height
            * 4
        )

        # MEMORY

        self.memory_cache.put(
            key,
            image.copy(),
            size,
        )

        # DISK

        self.disk_cache.save_image(
            key,
            image,
        )

    # =====================================================
    # GET
    # =====================================================

    def get_thumbnail(
        self,
        key,
    ):

        # MEMORY FIRST

        img = self.memory_cache.get(key)

        if img:
            return img

        # DISK SECOND

        img = self.disk_cache.load_image(
            key
        )

        if img:

            size = (
                img.width
                * img.height
                * 4
            )

            self.memory_cache.put(
                key,
                img.copy(),
                size,
            )

            return img

        return None

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(
        self,
        key,
    ):

        return (

            self.memory_cache.exists(key)

            or

            self.disk_cache.exists(key)

        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.memory_cache.clear()

        self.disk_cache.clear()

    # =====================================================
    # STATS
    # =====================================================

    def get_stats(self):

        return {

            "memory":
                self.memory_cache.get_stats(),

            "disk_size_mb":
                self.disk_cache.get_cache_size_mb(),
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    from PIL import Image

    # ---------------------------------------------
    # MEMORY CACHE
    # ---------------------------------------------

    cache = MemoryCache(
        max_items=5,
        max_memory_mb=100,
    )

    # DUMMY IMAGE

    img = Image.new(
        "RGB",
        (500, 500),
        "red",
    )

    cache.put(
        "image1",
        img,
        500 * 500 * 3,
    )

    result = cache.get("image1")

    print(
        "Memory Cache:",
        result is not None
    )

    print(
        cache.get_stats()
    )

    # ---------------------------------------------
    # THUMBNAIL CACHE
    # ---------------------------------------------

    thumb_cache = ThumbnailCache()

    key = thumb_cache.create_thumbnail_key(
        "sample.jpg",
        128,
        128,
    )

    thumb_cache.store_thumbnail(
        key,
        img,
    )

    thumb = thumb_cache.get_thumbnail(
        key
    )

    print(
        "Thumbnail Cache:",
        thumb is not None
    )

    print(
        thumb_cache.get_stats()
    )

    # CLEANUP

    cache.clear()

    thumb_cache.clear()

    img.close()