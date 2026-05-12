"""
core/template_manager.py

Template management system for HG Tile Studio

Features:
- Save templates
- Load templates
- Delete templates
- Rename templates
- List templates
- JSON based
- Auto template directory creation
- Corrupted template protection
- Export/import template support

Author: HARRY GRAPHICS
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


# =========================================================
# TEMPLATE MANAGER
# =========================================================

class TemplateManager:

    def __init__(
        self,
        template_dir="templates",
    ):

        self.template_dir = Path(template_dir)

        self.template_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # SAVE TEMPLATE
    # =====================================================

    def save_template(
        self,
        template_name,
        data,
        overwrite=True,
    ):

        template_path = self._get_template_path(
            template_name
        )

        if template_path.exists() and not overwrite:

            raise FileExistsError(
                f"Template already exists: {template_name}"
            )

        payload = {
            "template_name": template_name,
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "data": data,
        }

        with open(
            template_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                payload,
                f,
                indent=4,
            )

        return str(template_path)

    # =====================================================
    # LOAD TEMPLATE
    # =====================================================

    def load_template(
        self,
        template_name,
    ):

        template_path = self._get_template_path(
            template_name
        )

        if not template_path.exists():

            raise FileNotFoundError(
                f"Template not found: {template_name}"
            )

        try:

            with open(
                template_path,
                "r",
                encoding="utf-8"
            ) as f:

                payload = json.load(f)

            return payload

        except json.JSONDecodeError:

            raise ValueError(
                f"Corrupted template: {template_name}"
            )

    # =====================================================
    # DELETE TEMPLATE
    # =====================================================

    def delete_template(
        self,
        template_name,
    ):

        template_path = self._get_template_path(
            template_name
        )

        if template_path.exists():

            template_path.unlink()

            return True

        return False

    # =====================================================
    # RENAME TEMPLATE
    # =====================================================

    def rename_template(
        self,
        old_name,
        new_name,
    ):

        old_path = self._get_template_path(old_name)
        new_path = self._get_template_path(new_name)

        if not old_path.exists():

            raise FileNotFoundError(
                f"Template not found: {old_name}"
            )

        if new_path.exists():

            raise FileExistsError(
                f"Template already exists: {new_name}"
            )

        old_path.rename(new_path)

        return str(new_path)

    # =====================================================
    # LIST TEMPLATES
    # =====================================================

    def list_templates(self):

        templates = []

        for file in self.template_dir.glob("*.json"):

            try:

                with open(
                    file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    payload = json.load(f)

                templates.append({
                    "name": payload.get(
                        "template_name",
                        file.stem,
                    ),
                    "file": file.name,
                    "created_at": payload.get(
                        "created_at",
                        "",
                    ),
                    "version": payload.get(
                        "version",
                        "Unknown",
                    ),
                })

            except Exception:

                templates.append({
                    "name": file.stem,
                    "file": file.name,
                    "created_at": "Corrupted",
                    "version": "Unknown",
                })

        templates.sort(
            key=lambda x: x["name"].lower()
        )

        return templates

    # =====================================================
    # TEMPLATE EXISTS
    # =====================================================

    def template_exists(
        self,
        template_name,
    ):

        return self._get_template_path(
            template_name
        ).exists()

    # =====================================================
    # EXPORT TEMPLATE
    # =====================================================

    def export_template(
        self,
        template_name,
        export_path,
    ):

        template_path = self._get_template_path(
            template_name
        )

        if not template_path.exists():

            raise FileNotFoundError(
                f"Template not found: {template_name}"
            )

        shutil.copy2(
            template_path,
            export_path,
        )

        return export_path

    # =====================================================
    # IMPORT TEMPLATE
    # =====================================================

    def import_template(
        self,
        import_path,
        overwrite=False,
    ):

        import_path = Path(import_path)

        if not import_path.exists():

            raise FileNotFoundError(import_path)

        try:

            with open(
                import_path,
                "r",
                encoding="utf-8"
            ) as f:

                payload = json.load(f)

        except json.JSONDecodeError:

            raise ValueError(
                "Invalid template file"
            )

        template_name = payload.get(
            "template_name",
            import_path.stem,
        )

        destination = self._get_template_path(
            template_name
        )

        if destination.exists() and not overwrite:

            raise FileExistsError(
                f"Template already exists: {template_name}"
            )

        shutil.copy2(
            import_path,
            destination,
        )

        return str(destination)

    # =====================================================
    # GET TEMPLATE PATH
    # =====================================================

    def _get_template_path(
        self,
        template_name,
    ):

        safe_name = self._sanitize_filename(
            template_name
        )

        return self.template_dir / f"{safe_name}.json"

    # =====================================================
    # SANITIZE FILENAME
    # =====================================================

    def _sanitize_filename(
        self,
        name,
    ):

        invalid_chars = r'<>:"/\|?*'

        for ch in invalid_chars:
            name = name.replace(ch, "_")

        return name.strip()

    # =====================================================
    # CREATE DEFAULT TEMPLATE
    # =====================================================

    def create_default_template(self):

        default_data = {

            "canvas": {
                "preset": "A4",
                "width_mm": 210,
                "height_mm": 297,
                "orientation": "portrait",
                "dpi": 300,
            },

            "layout": {
                "layout_mode": "auto-fit",
                "image_width_mm": 35,
                "image_height_mm": 45,
                "horizontal_gap_mm": 2,
                "vertical_gap_mm": 2,
            },

            "margins": {
                "left_mm": 5,
                "right_mm": 5,
                "top_mm": 5,
                "bottom_mm": 5,
            },

            "scaling": {
                "mode": "fit",
            },

            "background": {
                "type": "solid",
                "color": [255, 255, 255],
            },

            "cutmarks": {
                "enabled": False,
                "length_mm": 3,
                "offset_mm": 1,
                "thickness_px": 1,
            },

            "export": {
                "format": "PNG",
                "jpg_quality": 95,
            },
        }

        return self.save_template(
            "default_template",
            default_data,
            overwrite=True,
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    manager = TemplateManager()

    # ---------------------------------------------
    # SAVE
    # ---------------------------------------------

    data = {
        "canvas": {
            "width_mm": 210,
            "height_mm": 297,
            "dpi": 300,
        },

        "layout": {
            "mode": "grid",
            "image_width_mm": 35,
            "image_height_mm": 45,
        }
    }

    manager.save_template(
        "passport_layout",
        data,
    )

    print("Template saved")

    # ---------------------------------------------
    # LIST
    # ---------------------------------------------

    print("\n========== TEMPLATES ==========")

    templates = manager.list_templates()

    for t in templates:
        print(t)

    # ---------------------------------------------
    # LOAD
    # ---------------------------------------------

    loaded = manager.load_template(
        "passport_layout"
    )

    print("\n========== LOADED ==========")

    print(
        json.dumps(
            loaded,
            indent=4,
        )
    )

    # ---------------------------------------------
    # CREATE DEFAULT
    # ---------------------------------------------

    manager.create_default_template()

    print("\nDefault template created")