"""
main.py

HG Tile Studio
Professional bulk image tiling and print layout software

Features:
- Bulk image tiling
- Auto-fit layouts
- PDF export
- DPI control
- Cut marks
- Template system
- Live preview
- Multi-page rendering

Framework:
PySide6

Author:
HARRY GRAPHICS
"""

import sys
import traceback

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from PySide6.QtGui import (
    QIcon,
)

from gui.main_window import MainWindow


# =========================================================
# GLOBAL EXCEPTION HANDLER
# =========================================================

def exception_hook(
    exc_type,
    exc_value,
    exc_traceback,
):

    error_message = "".join(

        traceback.format_exception(
            exc_type,
            exc_value,
            exc_traceback,
        )

    )

    print("\n========== ERROR ==========\n")

    print(error_message)

    try:

        QMessageBox.critical(

            None,

            "Application Error",

            f"Unexpected Error:\n\n"
            f"{str(exc_value)}\n\n"
            f"See console for details."

        )

    except:
        pass


# =========================================================
# APPLICATION
# =========================================================

def main():

    # ---------------------------------------------
    # EXCEPTION HOOK
    # ---------------------------------------------

    sys.excepthook = exception_hook

    # ---------------------------------------------
    # QT APP
    # ---------------------------------------------

    app = QApplication(sys.argv)

    app.setApplicationName(
        "HG Tile Studio"
    )

    app.setOrganizationName(
        "HARRY GRAPHICS"
    )

    app.setApplicationVersion(
        "1.0.0"
    )

    # ---------------------------------------------
    # OPTIONAL ICON
    # ---------------------------------------------

    try:

        app.setWindowIcon(
            QIcon("assets/icon.png")
        )

    except:
        pass

    # ---------------------------------------------
    # MAIN WINDOW
    # ---------------------------------------------

    window = MainWindow()

    window.show()

    # ---------------------------------------------
    # START
    # ---------------------------------------------

    sys.exit(app.exec())


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    main()