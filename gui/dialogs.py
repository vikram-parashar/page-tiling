"""
gui/dialogs.py

Professional dialog collection for HG Tile Studio

Features:
- Template save dialog
- Template load dialog
- Export progress dialog
- Image statistics dialog
- Error dialog
- Confirmation dialog
- About dialog

Framework:
PySide6

Author: HARRY GRAPHICS
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (

    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QProgressBar,
    QWidget,
    QFormLayout,
)


# =========================================================
# TEMPLATE SAVE DIALOG
# =========================================================

class TemplateSaveDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Save Template")

        self.setMinimumWidth(400)

        self.template_name = ""

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        label = QLabel("Template Name")

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "Enter template name..."
        )

        btn_row = QHBoxLayout()

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.accept_data)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)

        layout.addWidget(label)
        layout.addWidget(self.name_edit)
        layout.addLayout(btn_row)

    def accept_data(self):

        self.template_name = (
            self.name_edit.text().strip()
        )

        if not self.template_name:

            QMessageBox.warning(
                self,
                "Warning",
                "Template name cannot be empty."
            )

            return

        self.accept()

    def get_template_name(self):

        return self.template_name


# =========================================================
# TEMPLATE LOAD DIALOG
# =========================================================

class TemplateLoadDialog(QDialog):

    def __init__(
        self,
        templates=None,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle("Load Template")

        self.setMinimumSize(500, 400)

        self.selected_template = None

        self.templates = templates or []

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()

        for template in self.templates:

            item = QListWidgetItem(
                template.get("name", "Unknown")
            )

            item.setData(
                Qt.UserRole,
                template,
            )

            self.list_widget.addItem(item)

        layout.addWidget(
            QLabel("Available Templates")
        )

        layout.addWidget(self.list_widget)

        # BUTTONS

        row = QHBoxLayout()

        load_btn = QPushButton("Load")
        cancel_btn = QPushButton("Cancel")

        load_btn.clicked.connect(
            self.accept_selection
        )

        cancel_btn.clicked.connect(
            self.reject
        )

        row.addWidget(load_btn)
        row.addWidget(cancel_btn)

        layout.addLayout(row)

    def accept_selection(self):

        item = self.list_widget.currentItem()

        if not item:

            QMessageBox.warning(
                self,
                "Warning",
                "Please select a template."
            )

            return

        self.selected_template = item.data(
            Qt.UserRole
        )

        self.accept()

    def get_selected_template(self):

        return self.selected_template


# =========================================================
# EXPORT PROGRESS DIALOG
# =========================================================

class ExportProgressDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Exporting")

        self.setMinimumWidth(400)

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        self.status_label = QLabel(
            "Preparing export..."
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(0, 100)

        cancel_btn = QPushButton("Cancel")

        cancel_btn.clicked.connect(
            self.reject
        )

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(cancel_btn)

    def update_progress(
        self,
        value,
        text=None,
    ):

        self.progress_bar.setValue(value)

        if text:
            self.status_label.setText(text)


# =========================================================
# IMAGE STATISTICS DIALOG
# =========================================================

class ImageStatisticsDialog(QDialog):

    def __init__(
        self,
        stats,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle("Image Statistics")

        self.setMinimumWidth(400)

        self.stats = stats

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        form = QFormLayout()

        for key, value in self.stats.items():

            form.addRow(
                QLabel(str(key)),
                QLabel(str(value)),
            )

        close_btn = QPushButton("Close")

        close_btn.clicked.connect(
            self.accept
        )

        layout.addLayout(form)
        layout.addWidget(close_btn)


# =========================================================
# ERROR DIALOG
# =========================================================

class ErrorDialog(QMessageBox):

    def __init__(
        self,
        title="Error",
        message="Something went wrong.",
        details="",
        parent=None,
    ):

        super().__init__(parent)

        self.setIcon(QMessageBox.Critical)

        self.setWindowTitle(title)

        self.setText(message)

        if details:
            self.setDetailedText(details)

        self.setStandardButtons(
            QMessageBox.Ok
        )


# =========================================================
# CONFIRMATION DIALOG
# =========================================================

class ConfirmationDialog(QMessageBox):

    def __init__(
        self,
        title="Confirm",
        message="Are you sure?",
        parent=None,
    ):

        super().__init__(parent)

        self.setIcon(QMessageBox.Question)

        self.setWindowTitle(title)

        self.setText(message)

        self.setStandardButtons(
            QMessageBox.Yes |
            QMessageBox.No
        )

        self.setDefaultButton(
            QMessageBox.No
        )

    @staticmethod
    def ask(
        title,
        message,
        parent=None,
    ):

        dlg = ConfirmationDialog(
            title,
            message,
            parent,
        )

        return dlg.exec() == QMessageBox.Yes


# =========================================================
# ABOUT DIALOG
# =========================================================

class AboutDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("About")

        self.setMinimumSize(500, 350)

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "HG Tile Studio"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        description = QTextEdit()

        description.setReadOnly(True)

        description.setPlainText(
            """
HG Tile Studio

Professional bulk image tiling and print layout software.

Features:
- Auto image tiling
- PDF export
- Cut marks
- DPI control
- Template system
- Preview engine
- Multi-page layouts

Developed by:
HARRY GRAPHICS
            """
        )

        close_btn = QPushButton("Close")

        close_btn.clicked.connect(
            self.accept
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(close_btn)


# =========================================================
# SUCCESS MESSAGE
# =========================================================

def show_success(
    parent,
    title,
    message,
):

    QMessageBox.information(
        parent,
        title,
        message,
    )


# =========================================================
# ERROR MESSAGE
# =========================================================

def show_error(
    parent,
    title,
    message,
    details="",
):

    dlg = ErrorDialog(
        title=title,
        message=message,
        details=details,
        parent=parent,
    )

    dlg.exec()


# =========================================================
# INFO MESSAGE
# =========================================================

def show_info(
    parent,
    title,
    message,
):

    QMessageBox.information(
        parent,
        title,
        message,
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    # ---------------------------------------------
    # SAVE DIALOG TEST
    # ---------------------------------------------

    dlg = TemplateSaveDialog()

    if dlg.exec():

        print(
            dlg.get_template_name()
        )

    # ---------------------------------------------
    # LOAD DIALOG TEST
    # ---------------------------------------------

    templates = [

        {
            "name": "Passport Layout",
        },

        {
            "name": "Sticker Sheet",
        },

    ]

    load_dlg = TemplateLoadDialog(
        templates=templates
    )

    if load_dlg.exec():

        print(
            load_dlg.get_selected_template()
        )

    # ---------------------------------------------
    # ABOUT TEST
    # ---------------------------------------------

    about = AboutDialog()

    about.exec()