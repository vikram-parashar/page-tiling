"""
gui/preview_panel.py

Professional preview panel for HG Tile Studio

Features:
- QGraphicsView based preview
- Shows only first page with actual images
- Zoom in / zoom out
- Mouse wheel zoom
- Pan support
- Fit-to-screen
- Reset view
- Real image thumbnails rendered from disk
- DPI-safe preview rendering

Framework:
PySide6

Author: HARRY GRAPHICS
"""

from PySide6.QtCore import (
    Qt,
    QRectF,
    Signal,
)

from PySide6.QtGui import (
    QPixmap,
    QImage,
    QPainter,
    QColor,
    QPen,
    QBrush,
)

from PySide6.QtWidgets import (

    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,

    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
)

from PIL import Image


# =========================================================
# GRAPHICS VIEW
# =========================================================

class GraphicsView(QGraphicsView):

    zoom_changed = Signal(float)

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.zoom_level = 1.0

        self.panning = False
        self.pan_start = None

        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform
        )

        self.setDragMode(
            QGraphicsView.NoDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setBackgroundBrush(
            QColor(40, 40, 40)
        )

    # =====================================================
    # WHEEL ZOOM
    # =====================================================

    def wheelEvent(self, event):

        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:

            factor = zoom_in_factor

        else:

            factor = zoom_out_factor

        self.zoom_level *= factor

        self.scale(factor, factor)

        self.zoom_changed.emit(
            self.zoom_level
        )

    # =====================================================
    # PAN START
    # =====================================================

    def mousePressEvent(self, event):

        if event.button() == Qt.MiddleButton:

            self.panning = True

            self.pan_start = event.pos()

            self.setCursor(
                Qt.ClosedHandCursor
            )

            event.accept()

            return

        super().mousePressEvent(event)

    # =====================================================
    # PAN MOVE
    # =====================================================

    def mouseMoveEvent(self, event):

        if self.panning:

            delta = (
                event.pos()
                - self.pan_start
            )

            self.pan_start = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - delta.x()
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - delta.y()
            )

            event.accept()

            return

        super().mouseMoveEvent(event)

    # =====================================================
    # PAN END
    # =====================================================

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:

            self.panning = False

            self.setCursor(
                Qt.ArrowCursor
            )

            event.accept()

            return

        super().mouseReleaseEvent(event)

    # =====================================================
    # RESET ZOOM
    # =====================================================

    def reset_zoom(self):

        self.resetTransform()

        self.zoom_level = 1.0

        self.zoom_changed.emit(
            self.zoom_level
        )

    # =====================================================
    # FIT VIEW
    # =====================================================

    def fit_scene(self):

        rect = self.sceneRect()

        if rect.isNull():
            return

        self.fitInView(
            rect,
            Qt.KeepAspectRatio,
        )

        self.zoom_level = 1.0

        self.zoom_changed.emit(
            self.zoom_level
        )


# =========================================================
# PREVIEW PANEL
# =========================================================

class PreviewPanel(QWidget):

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.scene = QGraphicsScene()

        self._build_ui()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self):

        root = QVBoxLayout(self)

        # -------------------------------------------------
        # TOOLBAR
        # -------------------------------------------------

        toolbar = QHBoxLayout()

        self.zoom_label = QLabel(
            "100%"
        )

        zoom_in_btn = QPushButton("+")
        zoom_out_btn = QPushButton("-")

        fit_btn = QPushButton("Fit")
        reset_btn = QPushButton("Reset")
        clear_btn = QPushButton("Clear")

        zoom_in_btn.clicked.connect(
            self.zoom_in
        )

        zoom_out_btn.clicked.connect(
            self.zoom_out
        )

        fit_btn.clicked.connect(
            self.fit_view
        )

        reset_btn.clicked.connect(
            self.reset_view
        )

        clear_btn.clicked.connect(
            self.clear_preview
        )

        toolbar.addWidget(zoom_in_btn)
        toolbar.addWidget(zoom_out_btn)

        toolbar.addWidget(fit_btn)
        toolbar.addWidget(reset_btn)

        toolbar.addWidget(clear_btn)

        toolbar.addStretch()

        toolbar.addWidget(
            QLabel("Zoom:")
        )

        toolbar.addWidget(
            self.zoom_label
        )

        # -------------------------------------------------
        # VIEW
        # -------------------------------------------------

        self.view = GraphicsView()

        self.view.setScene(self.scene)

        self.view.zoom_changed.connect(
            self.on_zoom_changed
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label = QLabel(
            "Ready"
        )

        # -------------------------------------------------
        # ADD
        # -------------------------------------------------

        root.addLayout(toolbar)

        root.addWidget(self.view)

        root.addWidget(self.status_label)

    # =====================================================
    # ZOOM
    # =====================================================

    def zoom_in(self):

        factor = 1.15

        self.view.scale(
            factor,
            factor,
        )

        self.view.zoom_level *= factor

        self.on_zoom_changed(
            self.view.zoom_level
        )

    def zoom_out(self):

        factor = 1 / 1.15

        self.view.scale(
            factor,
            factor,
        )

        self.view.zoom_level *= factor

        self.on_zoom_changed(
            self.view.zoom_level
        )

    def reset_view(self):

        self.view.reset_zoom()

    def fit_view(self):

        self.view.fit_scene()

    def on_zoom_changed(self, value):

        percent = int(value * 100)

        self.zoom_label.setText(
            f"{percent}%"
        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_preview(self):

        self.scene.clear()

        self.status_label.setText(
            "Preview cleared"
        )

    # =====================================================
    # DISPLAY FIRST PAGE WITH ACTUAL IMAGES
    # =====================================================

    def draw_first_page_preview(
        self,
        page,
        dpi=300,
    ):
        """
        Draw only the first page of the layout using
        actual image thumbnails loaded from disk.

        Parameters:
            page  : LayoutPage object (from layout_engine)
            dpi   : DPI for rendering calculations
        """

        self.scene.clear()

        width_px = page.width_px
        height_px = page.height_px

        # -------------------------------------------------
        # PAGE BACKGROUND
        # -------------------------------------------------

        page_rect = QGraphicsRectItem(
            0,
            0,
            width_px,
            height_px,
        )

        page_rect.setBrush(
            QBrush(
                QColor(255, 255, 255)
            )
        )

        page_rect.setPen(
            QPen(
                QColor(180, 180, 180),
                2,
            )
        )

        self.scene.addItem(page_rect)

        # -------------------------------------------------
        # PLACE ACTUAL IMAGES
        # -------------------------------------------------

        for item in page.items:

            pixmap = self._load_thumbnail(
                item.path,
                item.w,
                item.h,
            )

            if pixmap and not pixmap.isNull():

                # Scale the loaded pixmap to the exact
                # layout cell size for crisp rendering

                scaled = pixmap.scaled(
                    item.w,
                    item.h,
                    Qt.IgnoreAspectRatio,
                    Qt.SmoothTransformation,
                )

                gfx_item = QGraphicsPixmapItem(
                    scaled
                )

                gfx_item.setPos(
                    item.x,
                    item.y,
                )

                self.scene.addItem(gfx_item)

            else:

                # Fallback: placeholder rectangle
                rect = QGraphicsRectItem(
                    item.x,
                    item.y,
                    item.w,
                    item.h,
                )

                rect.setBrush(
                    QBrush(
                        QColor(200, 220, 255)
                    )
                )

                rect.setPen(
                    QPen(
                        QColor(100, 140, 255),
                        1,
                    )
                )

                self.scene.addItem(rect)

        # -------------------------------------------------
        # SCENE RECT
        # -------------------------------------------------

        self.scene.setSceneRect(
            QRectF(
                0,
                0,
                width_px,
                height_px,
            )
        )

        self.fit_view()

        self.status_label.setText(
            f"Page 1 Preview: "
            f"{width_px} x {height_px} px | "
            f"{len(page.items)} image(s)"
        )

    # =====================================================
    # LOAD THUMBNAIL FOR PREVIEW
    # =====================================================

    def _load_thumbnail(
        self,
        path,
        target_w,
        target_h,
    ):
        """
        Load an image from disk and create a QPixmap
        at the target layout cell size.
        Uses PIL for robust loading with format support.
        """

        try:

            img = Image.open(path)

            # Convert to RGB if necessary
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")

            # Resize to target cell size
            img = img.resize(
                (target_w, target_h),
                Image.LANCZOS,
            )

            # PIL -> QImage -> QPixmap
            if img.mode == "RGBA":

                data = img.tobytes(
                    "raw", "RGBA"
                )

                qimg = QImage(
                    data,
                    img.width,
                    img.height,
                    QImage.Format_RGBA8888,
                )

            else:

                data = img.tobytes(
                    "raw", "RGB"
                )

                qimg = QImage(
                    data,
                    img.width,
                    img.height,
                    img.width * 3,
                    QImage.Format_RGB888,
                )

            pixmap = QPixmap.fromImage(qimg)

            img.close()

            return pixmap

        except Exception as e:

            print(f"Preview load error: {e}")

            return None

    # =====================================================
    # DISPLAY PIXMAP (legacy)
    # =====================================================

    def display_pixmap(
        self,
        pixmap: QPixmap,
    ):

        self.scene.clear()

        item = QGraphicsPixmapItem(
            pixmap
        )

        self.scene.addItem(item)

        self.scene.setSceneRect(
            QRectF(
                pixmap.rect()
            )
        )

        self.fit_view()

        self.status_label.setText(
            f"Preview Size: "
            f"{pixmap.width()} x "
            f"{pixmap.height()}"
        )

    # =====================================================
    # DISPLAY IMAGE FILE (legacy)
    # =====================================================

    def display_image_file(
        self,
        image_path,
    ):

        pixmap = QPixmap(image_path)

        if pixmap.isNull():

            self.status_label.setText(
                "Failed loading image"
            )

            return

        self.display_pixmap(pixmap)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication

    class DummyItem:

        def __init__(self, x, y, w, h, path=""):

            self.x = x
            self.y = y
            self.w = w
            self.h = h
            self.path = path

    class DummyPage:

        def __init__(self):

            self.width_px = 2480
            self.height_px = 3508

            self.items = []

    app = QApplication([])

    panel = PreviewPanel()

    # ---------------------------------------------
    # TEST PAGE
    # ---------------------------------------------

    page = DummyPage()

    for row in range(5):

        for col in range(4):

            item = DummyItem(
                100 + col * 500,
                100 + row * 600,
                350,
                450,
            )

            page.items.append(item)

    panel.draw_first_page_preview(page)

    panel.resize(1200, 800)

    panel.show()

    app.exec()
