"""
gui/main_window.py

Main application window for HG Tile Studio

Features:
- Splitter layout
- Controls panel
- Live preview panel
- Status bar
- Toolbar
- Menu bar
- Template integration
- Export integration
- Full pipeline: ImageLoader -> LayoutEngine -> Preview / ExportEngine

Framework:
PySide6

Author: HARRY GRAPHICS
"""

import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (

    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QStatusBar,
    QFileDialog,
    QMessageBox,
)

from gui.controls_panel import ControlsPanel
from gui.preview_panel import PreviewPanel

from gui.dialogs import (

    TemplateSaveDialog,
    TemplateLoadDialog,
    ExportProgressDialog,
    AboutDialog,

    show_error,
    show_success,
    show_info,
)

from core.template_manager import TemplateManager
from core.layout_engine import LayoutEngine, LayoutSettings
from core.export_engine import ExportEngine, ExportSettings, PageData
from core.image_loader import ImageLoader
from core.cutmarks import CutMarkSettings


# =========================================================
# MAIN WINDOW
# =========================================================

class MainWindow(QMainWindow):

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "HG Tile Studio"
        )

        self.resize(1600, 900)

        # ---------------------------------------------
        # ENGINES
        # ---------------------------------------------

        self.template_manager = TemplateManager()
        self.layout_engine = LayoutEngine()
        self.export_engine = ExportEngine()
        self.image_loader = None  # created per job

        # ---------------------------------------------
        # UI
        # ---------------------------------------------

        self._build_ui()

        self._connect_signals()

        self._apply_styles()

    # =====================================================
    # BUILD UI
    # =====================================================

    def _build_ui(self):

        # ---------------------------------------------
        # CENTRAL
        # ---------------------------------------------

        central = QWidget()

        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # ---------------------------------------------
        # SPLITTER
        # ---------------------------------------------

        splitter = QSplitter(Qt.Horizontal)

        # ---------------------------------------------
        # LEFT: CONTROLS
        # ---------------------------------------------

        self.controls = ControlsPanel()

        splitter.addWidget(self.controls)

        # ---------------------------------------------
        # RIGHT: PREVIEW
        # ---------------------------------------------

        self.preview_panel = PreviewPanel()

        splitter.addWidget(self.preview_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        splitter.setSizes([350, 1200])

        layout.addWidget(splitter)

        # ---------------------------------------------
        # STATUS BAR
        # ---------------------------------------------

        status = QStatusBar()

        self.setStatusBar(status)

        self.statusBar().showMessage(
            "Ready"
        )

        # ---------------------------------------------
        # MENU
        # ---------------------------------------------

        self._build_menu()

        # ---------------------------------------------
        # TOOLBAR
        # ---------------------------------------------

        self._build_toolbar()

    # =====================================================
    # MENU
    # =====================================================

    def _build_menu(self):

        menu = self.menuBar()

        # FILE MENU

        file_menu = menu.addMenu("File")

        open_input = QAction(
            "Select Input Folder",
            self,
        )

        open_output = QAction(
            "Select Output Folder",
            self,
        )

        exit_action = QAction(
            "Exit",
            self,
        )

        open_input.triggered.connect(
            self.controls.select_input_folder
        )

        open_output.triggered.connect(
            self.controls.select_output_folder
        )

        exit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(open_input)
        file_menu.addAction(open_output)

        file_menu.addSeparator()

        file_menu.addAction(exit_action)

        # TEMPLATE MENU

        template_menu = menu.addMenu(
            "Templates"
        )

        save_template = QAction(
            "Save Template",
            self,
        )

        load_template = QAction(
            "Load Template",
            self,
        )

        save_template.triggered.connect(
            self.save_template
        )

        load_template.triggered.connect(
            self.load_template
        )

        template_menu.addAction(
            save_template
        )

        template_menu.addAction(
            load_template
        )

        # HELP MENU

        help_menu = menu.addMenu("Help")

        about_action = QAction(
            "About",
            self,
        )

        about_action.triggered.connect(
            self.show_about
        )

        help_menu.addAction(
            about_action
        )

    # =====================================================
    # TOOLBAR
    # =====================================================

    def _build_toolbar(self):

        toolbar = self.addToolBar(
            "Main Toolbar"
        )

        preview_action = QAction(
            "Preview",
            self,
        )

        generate_action = QAction(
            "Generate",
            self,
        )

        preview_action.triggered.connect(
            self.generate_preview
        )

        generate_action.triggered.connect(
            self.generate_output
        )

        toolbar.addAction(preview_action)
        toolbar.addAction(generate_action)

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        self.controls.preview_requested.connect(
            self.generate_preview
        )

        self.controls.generate_requested.connect(
            self.generate_output
        )

        self.controls.template_save_requested.connect(
            self.save_template
        )

        self.controls.template_load_requested.connect(
            self.load_template
        )

    # =====================================================
    # BUILD LAYOUT SETTINGS FROM CONTROLS
    # =====================================================

    def _build_layout_settings(self):

        s = self.controls.get_settings()

        settings = LayoutSettings(

            page_width_mm=s["page_width_mm"],
            page_height_mm=s["page_height_mm"],

            dpi=s["dpi"],

            margin_left_mm=s["margin_left_mm"],
            margin_right_mm=s["margin_right_mm"],
            margin_top_mm=s["margin_top_mm"],
            margin_bottom_mm=s["margin_bottom_mm"],

            horizontal_gap_mm=s["horizontal_gap_mm"],
            vertical_gap_mm=s["vertical_gap_mm"],

            image_width_mm=s["image_width_mm"],
            image_height_mm=s["image_height_mm"],

            layout_mode=s["layout_mode"],

            scaling_mode=s["scaling_mode"],

            auto_fit=True,
        )

        return settings

    # =====================================================
    # COLLECT IMAGE PATHS
    # =====================================================

    def _collect_image_paths(self):

        s = self.controls.get_settings()

        input_folder = s.get("input_folder", "")

        if not input_folder:
            return None, "No input folder selected."

        include_subfolders = s.get("include_subfolders", True)

        self.image_loader = ImageLoader(
            include_subfolders=include_subfolders,
            generate_thumbnails=False,
        )

        self.image_loader.scan_folder(input_folder)

        valid = self.image_loader.get_valid_images()

        if not valid:
            return None, "No valid images found in the input folder."

        paths = [img.path for img in valid]

        return paths, None

    # =====================================================
    # PREVIEW
    # =====================================================

    def generate_preview(self):

        try:

            paths, err = self._collect_image_paths()

            if err:
                QMessageBox.warning(
                    self,
                    "Preview",
                    err,
                )
                return

            settings = self._build_layout_settings()

            pages = self.layout_engine.generate_layout(
                paths,
                settings,
            )

            self.preview_panel.draw_multi_page_preview(
                pages,
            )

            self.statusBar().showMessage(
                f"Preview: {len(paths)} images, "
                f"{len(pages)} page(s)"
            )

        except Exception as e:

            show_error(
                self,
                "Preview Error",
                str(e),
                traceback.format_exc(),
            )

    # =====================================================
    # GENERATE OUTPUT
    # =====================================================

    def generate_output(self):

        try:

            s = self.controls.get_settings()

            output_folder = s.get("output_folder", "")

            if not output_folder:

                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select an output folder.",
                )

                return

            paths, err = self._collect_image_paths()

            if err:
                QMessageBox.warning(
                    self,
                    "Export",
                    err,
                )
                return

            settings = self._build_layout_settings()

            layout_pages = self.layout_engine.generate_layout(
                paths,
                settings,
            )

            # -----------------------------------------
            # BUILD EXPORT SETTINGS
            # -----------------------------------------

            export_settings = ExportSettings(
                export_format=s["export_format"],
                dpi=s["dpi"],
                jpg_quality=s["jpg_quality"],
                background_color=tuple(
                    s["background_color"][:3]
                ),
                transparent=(
                    s.get("background_type", "Solid Color")
                    == "Transparent"
                ),
            )

            # -----------------------------------------
            # BUILD CUT MARK SETTINGS
            # -----------------------------------------

            cutmark_settings = CutMarkSettings(
                enabled=s["cutmarks_enabled"],
                length_mm=s["cutmark_length_mm"],
                offset_mm=s["cutmark_offset_mm"],
            )

            # -----------------------------------------
            # BUILD PAGE DATA
            # -----------------------------------------

            export_pages = []

            for page in layout_pages:

                image_items = []

                for item in page.items:

                    image_items.append({
                        "path": item.path,
                        "x": item.x,
                        "y": item.y,
                        "w": item.w,
                        "h": item.h,
                        "scaling_mode": item.scaling_mode,
                    })

                page_data = PageData(
                    width_mm=settings.page_width_mm,
                    height_mm=settings.page_height_mm,
                    image_items=image_items,
                )

                export_pages.append(page_data)

            # -----------------------------------------
            # PROGRESS DIALOG
            # -----------------------------------------

            progress_dlg = ExportProgressDialog(self)
            progress_dlg.show()

            progress_dlg.update_progress(
                10,
                "Rendering pages...",
            )

            # -----------------------------------------
            # EXPORT
            # -----------------------------------------

            filename_pattern = "sheet_{page}_{date}"

            self.export_engine.export_pages(
                pages=export_pages,
                output_folder=output_folder,
                filename_pattern=filename_pattern,
                export_settings=export_settings,
                cutmark_settings=cutmark_settings,
            )

            progress_dlg.update_progress(
                100,
                "Export completed!",
            )

            progress_dlg.accept()

            self.statusBar().showMessage(
                f"Export completed: "
                f"{len(export_pages)} page(s)"
            )

            show_success(
                self,
                "Export Complete",
                f"Successfully exported "
                f"{len(export_pages)} page(s) to:\n"
                f"{output_folder}",
            )

        except Exception as e:

            show_error(
                self,
                "Export Error",
                str(e),
                traceback.format_exc(),
            )

    # =====================================================
    # SAVE TEMPLATE
    # =====================================================

    def save_template(self):

        try:

            dlg = TemplateSaveDialog(self)

            if not dlg.exec():
                return

            template_name = (
                dlg.get_template_name()
            )

            settings = (
                self.controls.get_settings()
            )

            self.template_manager.save_template(
                template_name,
                settings,
            )

            show_success(
                self,
                "Success",
                f"Template saved:\n{template_name}",
            )

            self.statusBar().showMessage(
                f"Template saved: {template_name}"
            )

        except Exception as e:

            show_error(
                self,
                "Template Save Error",
                str(e),
                traceback.format_exc(),
            )

    # =====================================================
    # LOAD TEMPLATE
    # =====================================================

    def load_template(self):

        try:

            templates = (
                self.template_manager.list_templates()
            )

            dlg = TemplateLoadDialog(
                templates=templates,
                parent=self,
            )

            if not dlg.exec():
                return

            selected = (
                dlg.get_selected_template()
            )

            if not selected:
                return

            name = selected["name"]

            template = (
                self.template_manager.load_template(
                    name
                )
            )

            data = template.get("data", {})

            # -----------------------------------------
            # APPLY TEMPLATE DATA TO CONTROLS
            # -----------------------------------------

            self._apply_template_to_controls(data)

            self.statusBar().showMessage(
                f"Template loaded: {name}"
            )

            show_success(
                self,
                "Template Loaded",
                f"Loaded template:\n{name}",
            )

        except Exception as e:

            show_error(
                self,
                "Template Load Error",
                str(e),
                traceback.format_exc(),
            )

    # =====================================================
    # APPLY TEMPLATE DATA TO CONTROLS
    # =====================================================

    def _apply_template_to_controls(self, data):

        """Apply template data dictionary to the controls panel."""

        # CANVAS

        canvas = data.get("canvas", {})

        if canvas:
            preset = canvas.get("preset", "")

            if preset:
                index = self.controls.canvas_preset.findText(
                    preset
                )
                if index >= 0:
                    self.controls.canvas_preset.setCurrentIndex(
                        index
                    )

            width = canvas.get("width_mm")
            if width is not None:
                self.controls.width_spin.setValue(width)

            height = canvas.get("height_mm")
            if height is not None:
                self.controls.height_spin.setValue(height)

            orientation = canvas.get("orientation", "")
            if orientation:
                idx = self.controls.orientation_combo.findText(
                    orientation.capitalize()
                )
                if idx >= 0:
                    self.controls.orientation_combo.setCurrentIndex(
                        idx
                    )

            dpi = canvas.get("dpi")
            if dpi is not None:
                self.controls.dpi_spin.setValue(dpi)

        # LAYOUT

        layout_data = data.get("layout", {})

        if layout_data:
            mode = layout_data.get("layout_mode")
            if mode:
                idx = self.controls.layout_mode.findText(mode)
                if idx >= 0:
                    self.controls.layout_mode.setCurrentIndex(
                        idx
                    )

            img_w = layout_data.get("image_width_mm")
            if img_w is not None:
                self.controls.image_width.setValue(img_w)

            img_h = layout_data.get("image_height_mm")
            if img_h is not None:
                self.controls.image_height.setValue(img_h)

            h_gap = layout_data.get("horizontal_gap_mm")
            if h_gap is not None:
                self.controls.h_gap.setValue(h_gap)

            v_gap = layout_data.get("vertical_gap_mm")
            if v_gap is not None:
                self.controls.v_gap.setValue(v_gap)

        # MARGINS

        margins = data.get("margins", {})

        if margins:
            left = margins.get("left_mm")
            if left is not None:
                self.controls.margin_left.setValue(left)

            right = margins.get("right_mm")
            if right is not None:
                self.controls.margin_right.setValue(right)

            top = margins.get("top_mm")
            if top is not None:
                self.controls.margin_top.setValue(top)

            bottom = margins.get("bottom_mm")
            if bottom is not None:
                self.controls.margin_bottom.setValue(bottom)

        # SCALING

        scaling = data.get("scaling", {})

        if scaling:
            mode = scaling.get("mode")
            if mode:
                idx = self.controls.scaling_mode.findText(mode)
                if idx >= 0:
                    self.controls.scaling_mode.setCurrentIndex(
                        idx
                    )

        # BACKGROUND

        background = data.get("background", {})

        if background:
            bg_type = background.get("type", "solid")
            if bg_type == "Transparent":
                self.controls.background_type.setCurrentText(
                    "Transparent"
                )
            else:
                self.controls.background_type.setCurrentText(
                    "Solid Color"
                )

            color = background.get("color")
            if color and len(color) >= 3:
                from PySide6.QtGui import QColor
                self.controls.background_color = QColor(
                    color[0], color[1], color[2]
                )

        # CUT MARKS

        cutmarks = data.get("cutmarks", {})

        if cutmarks:
            enabled = cutmarks.get("enabled")
            if enabled is not None:
                self.controls.cutmark_enable.setChecked(enabled)

            length = cutmarks.get("length_mm")
            if length is not None:
                self.controls.cutmark_length.setValue(length)

            offset = cutmarks.get("offset_mm")
            if offset is not None:
                self.controls.cutmark_offset.setValue(offset)

        # EXPORT

        export = data.get("export", {})

        if export:
            fmt = export.get("format")
            if fmt:
                idx = self.controls.export_format.findText(
                    fmt.upper()
                )
                if idx >= 0:
                    self.controls.export_format.setCurrentIndex(
                        idx
                    )

            quality = export.get("jpg_quality")
            if quality is not None:
                self.controls.jpg_quality.setValue(quality)

    # =====================================================
    # ABOUT
    # =====================================================

    def show_about(self):

        dlg = AboutDialog(self)

        dlg.exec()

    # =====================================================
    # STYLES
    # =====================================================

    def _apply_styles(self):

        self.setStyleSheet("""

            QMainWindow {
                background: #202124;
                color: white;
            }

            QWidget {
                background: #202124;
                color: white;
                font-size: 12px;
            }

            QGroupBox {
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }

            QPushButton {
                background: #2d6cdf;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }

            QPushButton:hover {
                background: #3b7cff;
            }

            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QComboBox {

                background: #2b2b2b;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }

            QScrollArea {
                border: none;
            }

            QMenuBar {
                background: #202124;
            }

            QMenu {
                background: #2b2b2b;
            }

            QStatusBar {
                background: #2b2b2b;
            }

        """)


# =========================================================
# TEST
# =====================================================

if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    window = MainWindow()

    window.show()

    app.exec()
