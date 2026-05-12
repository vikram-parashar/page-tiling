"""
gui/main_window.py

Main application window for HG Tile Studio

Features:
- Splitter layout
- Controls panel
- Preview panel placeholder
- Status bar
- Toolbar
- Menu bar
- Template integration
- Export integration
- Modern scalable architecture

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
    QLabel,
    QStatusBar,
    QFileDialog,
    QMessageBox,
)

from gui.controls_panel import ControlsPanel

from gui.dialogs import (

    TemplateSaveDialog,
    TemplateLoadDialog,
    AboutDialog,

    show_error,
    show_success,
    show_info,
)

from core.template_manager import TemplateManager


# =========================================================
# PREVIEW PLACEHOLDER
# =========================================================

class PreviewPanel(QWidget):

    """
    Placeholder preview panel.

    Replace later with:
    - QGraphicsView
    - Zoom
    - Pan
    - Live rendering
    """

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        label = QLabel(
            "LIVE PREVIEW PANEL\n\n"
            "QGraphicsView will be added later."
        )

        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)


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
        # MANAGERS
        # ---------------------------------------------

        self.template_manager = TemplateManager()

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
    # PREVIEW
    # =====================================================

    def generate_preview(self):

        try:

            settings = (
                self.controls.get_settings()
            )

            print("\n========== PREVIEW ==========")

            for k, v in settings.items():

                print(k, ":", v)

            self.statusBar().showMessage(
                "Preview generated"
            )

            show_info(
                self,
                "Preview",
                "Preview generation placeholder.\n\n"
                "Live rendering engine will be added later.",
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

            settings = (
                self.controls.get_settings()
            )

            output_folder = settings.get(
                "output_folder",
                "",
            )

            if not output_folder:

                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select output folder.",
                )

                return

            self.statusBar().showMessage(
                "Generating output..."
            )

            # -----------------------------------------
            # PLACEHOLDER
            # -----------------------------------------

            print("\n========== EXPORT ==========")

            for k, v in settings.items():

                print(k, ":", v)

            self.statusBar().showMessage(
                "Export completed"
            )

            show_success(
                self,
                "Success",
                "Export placeholder completed.\n\n"
                "Export engine integration coming next.",
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
            # PLACEHOLDER
            # -----------------------------------------

            print("\n========== TEMPLATE ==========")

            print(data)

            show_success(
                self,
                "Template Loaded",
                f"Loaded template:\n{name}",
            )

            self.statusBar().showMessage(
                f"Template loaded: {name}"
            )

        except Exception as e:

            show_error(
                self,
                "Template Load Error",
                str(e),
                traceback.format_exc(),
            )

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