"""
gui/controls_panel.py

Professional controls panel for HG Tile Studio

Features:
- Input/output folder selection
- Include subfolders
- Canvas presets
- Portrait/Landscape auto swap
- Custom sheet size
- Margin controls
- Gap controls
- Layout mode selection
- Scaling mode selection
- DPI control
- Background options
- Cut mark settings
- Export settings
- Template save/load hooks
- Collapsible sections
- Signal-ready architecture

Framework:
PySide6

Author: HARRY GRAPHICS
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (

    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QColorDialog,
    QScrollArea,
    QGroupBox,
    QSizePolicy,
)

from PySide6.QtGui import QColor


# =========================================================
# CONTROLS PANEL
# =========================================================

class ControlsPanel(QWidget):

    # -----------------------------------------------------
    # SIGNALS
    # -----------------------------------------------------

    preview_requested = Signal()
    generate_requested = Signal()

    template_save_requested = Signal()
    template_load_requested = Signal()

    settings_changed = Signal(dict)

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.background_color = QColor(255, 255, 255)

        self._build_ui()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self):

        root_layout = QVBoxLayout(self)

        # -------------------------------------------------
        # SCROLL AREA
        # -------------------------------------------------

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()

        self.layout = QVBoxLayout(content)

        self.layout.setSpacing(12)

        # -------------------------------------------------
        # BUILD SECTIONS
        # -------------------------------------------------

        self._build_folder_section()
        self._build_canvas_section()
        self._build_layout_section()
        self._build_margin_section()
        self._build_scaling_section()
        self._build_background_section()
        self._build_export_section()
        self._build_cutmark_section()
        self._build_template_section()
        self._build_action_buttons()

        self.layout.addStretch()

        scroll.setWidget(content)

        root_layout.addWidget(scroll)

    # =====================================================
    # FOLDER SECTION
    # =====================================================

    def _build_folder_section(self):

        box = self._create_group("Folders")

        layout = QVBoxLayout()

        # INPUT

        self.input_edit = QLineEdit()

        input_btn = QPushButton("Browse")

        input_btn.clicked.connect(
            self.select_input_folder
        )

        row = QHBoxLayout()

        row.addWidget(QLabel("Input"))
        row.addWidget(self.input_edit)
        row.addWidget(input_btn)

        layout.addLayout(row)

        # OUTPUT

        self.output_edit = QLineEdit()

        output_btn = QPushButton("Browse")

        output_btn.clicked.connect(
            self.select_output_folder
        )

        row2 = QHBoxLayout()

        row2.addWidget(QLabel("Output"))
        row2.addWidget(self.output_edit)
        row2.addWidget(output_btn)

        layout.addLayout(row2)

        # SUBFOLDER

        self.subfolder_check = QCheckBox(
            "Include Subfolders"
        )

        self.subfolder_check.setChecked(True)

        layout.addWidget(self.subfolder_check)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # CANVAS SECTION
    # =====================================================

    def _build_canvas_section(self):

        box = self._create_group("Canvas")

        layout = QVBoxLayout()

        # PRESET

        self.canvas_preset = QComboBox()

        self.canvas_preset.addItems([
            "A4",
            "A3",
            "A5",
            "Letter",
            "Legal",
            "Custom",
        ])

        self.canvas_preset.currentTextChanged.connect(
            self.on_canvas_changed
        )

        layout.addWidget(QLabel("Preset"))
        layout.addWidget(self.canvas_preset)

        # SIZE

        row = QHBoxLayout()

        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 5000)
        self.width_spin.setValue(210)

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 5000)
        self.height_spin.setValue(297)

        row.addWidget(QLabel("Width"))
        row.addWidget(self.width_spin)

        row.addWidget(QLabel("Height"))
        row.addWidget(self.height_spin)

        layout.addLayout(row)

        # ORIENTATION

        self.orientation_combo = QComboBox()

        self.orientation_combo.addItems([
            "Portrait",
            "Landscape",
        ])

        self.orientation_combo.currentTextChanged.connect(
            self.on_orientation_changed
        )

        layout.addWidget(QLabel("Orientation"))
        layout.addWidget(self.orientation_combo)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # LAYOUT SECTION
    # =====================================================

    def _build_layout_section(self):

        box = self._create_group("Layout")

        layout = QVBoxLayout()

        # MODE

        self.layout_mode = QComboBox()

        self.layout_mode.addItems([
            "grid",
            "space-between",
            "space-around",
            "space-evenly",
            "packed",
            "auto-fit",
        ])

        layout.addWidget(QLabel("Layout Mode"))
        layout.addWidget(self.layout_mode)

        # IMAGE SIZE

        row = QHBoxLayout()

        self.image_width = QDoubleSpinBox()
        self.image_width.setRange(1, 1000)
        self.image_width.setValue(35)

        self.image_height = QDoubleSpinBox()
        self.image_height.setRange(1, 1000)
        self.image_height.setValue(45)

        row.addWidget(QLabel("Image W"))
        row.addWidget(self.image_width)

        row.addWidget(QLabel("Image H"))
        row.addWidget(self.image_height)

        layout.addLayout(row)

        # GAP

        row2 = QHBoxLayout()

        self.h_gap = QDoubleSpinBox()
        self.h_gap.setValue(2)

        self.v_gap = QDoubleSpinBox()
        self.v_gap.setValue(2)

        row2.addWidget(QLabel("H Gap"))
        row2.addWidget(self.h_gap)

        row2.addWidget(QLabel("V Gap"))
        row2.addWidget(self.v_gap)

        layout.addLayout(row2)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # MARGINS
    # =====================================================

    def _build_margin_section(self):

        box = self._create_group("Margins")

        layout = QVBoxLayout()

        self.margin_left = self._margin_spin()
        self.margin_right = self._margin_spin()
        self.margin_top = self._margin_spin()
        self.margin_bottom = self._margin_spin()

        for label, widget in [

            ("Left", self.margin_left),
            ("Right", self.margin_right),
            ("Top", self.margin_top),
            ("Bottom", self.margin_bottom),

        ]:

            row = QHBoxLayout()

            row.addWidget(QLabel(label))
            row.addWidget(widget)

            layout.addLayout(row)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # SCALING
    # =====================================================

    def _build_scaling_section(self):

        box = self._create_group("Scaling")

        layout = QVBoxLayout()

        self.scaling_mode = QComboBox()

        self.scaling_mode.addItems([
            "fit",
            "fill",
            "stretch",
            "original",
            "contain",
            "cover",
            "smart-crop",
        ])

        layout.addWidget(QLabel("Scaling Mode"))
        layout.addWidget(self.scaling_mode)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # BACKGROUND
    # =====================================================

    def _build_background_section(self):

        box = self._create_group("Background")

        layout = QVBoxLayout()

        self.background_type = QComboBox()

        self.background_type.addItems([
            "Solid Color",
            "Transparent",
        ])

        layout.addWidget(QLabel("Background"))
        layout.addWidget(self.background_type)

        self.color_btn = QPushButton(
            "Choose Color"
        )

        self.color_btn.clicked.connect(
            self.choose_color
        )

        layout.addWidget(self.color_btn)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # EXPORT
    # =====================================================

    def _build_export_section(self):

        box = self._create_group("Export")

        layout = QVBoxLayout()

        self.export_format = QComboBox()

        self.export_format.addItems([
            "PNG",
            "JPG",
            "PDF",
        ])

        layout.addWidget(QLabel("Format"))
        layout.addWidget(self.export_format)

        # DPI

        self.dpi_spin = QSpinBox()

        self.dpi_spin.setRange(72, 2400)
        self.dpi_spin.setValue(300)

        layout.addWidget(QLabel("DPI"))
        layout.addWidget(self.dpi_spin)

        # JPG QUALITY

        self.jpg_quality = QSpinBox()

        self.jpg_quality.setRange(1, 100)
        self.jpg_quality.setValue(95)

        layout.addWidget(QLabel("JPG Quality"))
        layout.addWidget(self.jpg_quality)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # CUT MARKS
    # =====================================================

    def _build_cutmark_section(self):

        box = self._create_group("Cut Marks")

        layout = QVBoxLayout()

        self.cutmark_enable = QCheckBox(
            "Enable Cut Marks"
        )

        layout.addWidget(self.cutmark_enable)

        self.cutmark_length = QDoubleSpinBox()
        self.cutmark_length.setValue(3)

        self.cutmark_offset = QDoubleSpinBox()
        self.cutmark_offset.setValue(1)

        row = QHBoxLayout()

        row.addWidget(QLabel("Length"))
        row.addWidget(self.cutmark_length)

        row.addWidget(QLabel("Offset"))
        row.addWidget(self.cutmark_offset)

        layout.addLayout(row)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # TEMPLATE SECTION
    # =====================================================

    def _build_template_section(self):

        box = self._create_group("Templates")

        layout = QVBoxLayout()

        save_btn = QPushButton("Save Template")
        load_btn = QPushButton("Load Template")

        save_btn.clicked.connect(
            self.template_save_requested.emit
        )

        load_btn.clicked.connect(
            self.template_load_requested.emit
        )

        layout.addWidget(save_btn)
        layout.addWidget(load_btn)

        box.setLayout(layout)

        self.layout.addWidget(box)

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    def _build_action_buttons(self):

        row = QHBoxLayout()

        preview_btn = QPushButton("Preview")

        generate_btn = QPushButton("Generate")

        preview_btn.clicked.connect(
            self.preview_requested.emit
        )

        generate_btn.clicked.connect(
            self.generate_requested.emit
        )

        row.addWidget(preview_btn)
        row.addWidget(generate_btn)

        self.layout.addLayout(row)

    # =====================================================
    # HELPERS
    # =====================================================

    def _create_group(self, title):

        box = QGroupBox(title)

        box.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Maximum,
        )

        return box

    def _margin_spin(self):

        spin = QDoubleSpinBox()

        spin.setRange(0, 1000)
        spin.setValue(5)

        return spin

    # =====================================================
    # EVENTS
    # =====================================================

    def select_input_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
        )

        if folder:
            self.input_edit.setText(folder)

    def select_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
        )

        if folder:
            self.output_edit.setText(folder)

    def choose_color(self):

        color = QColorDialog.getColor(
            self.background_color,
            self,
        )

        if color.isValid():

            self.background_color = color

    def on_canvas_changed(self):

        preset = self.canvas_preset.currentText()

        sizes = {

            "A4": (210, 297),
            "A3": (297, 420),
            "A5": (148, 210),
            "Letter": (216, 279),
            "Legal": (216, 356),
        }

        if preset in sizes:

            w, h = sizes[preset]

            self.width_spin.setValue(w)
            self.height_spin.setValue(h)

    def on_orientation_changed(self):

        orientation = (
            self.orientation_combo.currentText()
        )

        w = self.width_spin.value()
        h = self.height_spin.value()

        if orientation == "Landscape":

            if h > w:
                self.width_spin.setValue(h)
                self.height_spin.setValue(w)

        else:

            if w > h:
                self.width_spin.setValue(h)
                self.height_spin.setValue(w)

    # =====================================================
    # GET SETTINGS
    # =====================================================

    def get_settings(self):

        return {

            # -----------------------------------------
            # FOLDERS
            # -----------------------------------------

            "input_folder":
                self.input_edit.text(),

            "output_folder":
                self.output_edit.text(),

            "include_subfolders":
                self.subfolder_check.isChecked(),

            # -----------------------------------------
            # CANVAS
            # -----------------------------------------

            "canvas_preset":
                self.canvas_preset.currentText(),

            "page_width_mm":
                self.width_spin.value(),

            "page_height_mm":
                self.height_spin.value(),

            "orientation":
                self.orientation_combo.currentText(),

            # -----------------------------------------
            # LAYOUT
            # -----------------------------------------

            "layout_mode":
                self.layout_mode.currentText(),

            "image_width_mm":
                self.image_width.value(),

            "image_height_mm":
                self.image_height.value(),

            "horizontal_gap_mm":
                self.h_gap.value(),

            "vertical_gap_mm":
                self.v_gap.value(),

            # -----------------------------------------
            # MARGINS
            # -----------------------------------------

            "margin_left_mm":
                self.margin_left.value(),

            "margin_right_mm":
                self.margin_right.value(),

            "margin_top_mm":
                self.margin_top.value(),

            "margin_bottom_mm":
                self.margin_bottom.value(),

            # -----------------------------------------
            # SCALING
            # -----------------------------------------

            "scaling_mode":
                self.scaling_mode.currentText(),

            # -----------------------------------------
            # BACKGROUND
            # -----------------------------------------

            "background_type":
                self.background_type.currentText(),

            "background_color":
                self.background_color.getRgb(),

            # -----------------------------------------
            # EXPORT
            # -----------------------------------------

            "export_format":
                self.export_format.currentText(),

            "dpi":
                self.dpi_spin.value(),

            "jpg_quality":
                self.jpg_quality.value(),

            # -----------------------------------------
            # CUT MARKS
            # -----------------------------------------

            "cutmarks_enabled":
                self.cutmark_enable.isChecked(),

            "cutmark_length_mm":
                self.cutmark_length.value(),

            "cutmark_offset_mm":
                self.cutmark_offset.value(),
        }