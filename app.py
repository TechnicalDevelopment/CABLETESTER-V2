import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from ui.main_window import MainWindow

# Forceer output naar SPI LCD (fb1)
os.environ.setdefault("QT_QPA_PLATFORM", "linuxfb:fb=/dev/fb1")
os.environ.setdefault("QT_QPA_FB", "/dev/fb1")

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeTouchForUnhandledMouseEvents, True)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cable Tester V2")

    w = MainWindow()
    w.showFullScreen()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
