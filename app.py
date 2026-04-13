import os
import sys

from PyQt6.QtCore import Qt, QCoreApplication, QObject, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow

# Forceer output naar SPI LCD (fb1)
os.environ.setdefault("QT_QPA_PLATFORM", "linuxfb:fb=/dev/fb1")
os.environ.setdefault("QT_QPA_FB", "/dev/fb1")

# Qt: probeer automatisch touch->mouse
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeTouchForUnhandledMouseEvents, True)


class TouchToMouseFilter(QObject):
    """
    Forceert taps op resistive touch naar echte mouse press/release,
    zodat QPushButton.clicked betrouwbaar werkt (ook zonder swipe).
    """
    def __init__(self):
        super().__init__()
        self._pressed = False
        self._target = None

    def eventFilter(self, obj, event):
        et = event.type()

        if et in (QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd):
            points = event.points()
            if not points:
                return False

            posf = points[0].position()
            pos = QPoint(int(posf.x()), int(posf.y()))

            # Zoek widget onder touchpunt
            w = QApplication.widgetAt(pos)
            if w is None:
                return True  # consumeer; anders rare side effects

            if et == QEvent.Type.TouchBegin:
                self._target = w
                self._pressed = True
                me = QMouseEvent(QEvent.Type.MouseButtonPress, posf, Qt.MouseButton.LeftButton,
                                 Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(self._target, me)
                return True

            if et == QEvent.Type.TouchUpdate:
                # Sommige stacks sturen geen TouchBegin: dan maken we bij eerste update alsnog Press
                if not self._pressed:
                    self._target = w
                    self._pressed = True
                    me = QMouseEvent(QEvent.Type.MouseButtonPress, posf, Qt.MouseButton.LeftButton,
                                     Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
                    QApplication.sendEvent(self._target, me)
                else:
                    me = QMouseEvent(QEvent.Type.MouseMove, posf, Qt.MouseButton.LeftButton,
                                     Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
                    QApplication.sendEvent(self._target or w, me)
                return True

            if et == QEvent.Type.TouchEnd:
                if self._pressed:
                    me = QMouseEvent(QEvent.Type.MouseButtonRelease, posf, Qt.MouseButton.LeftButton,
                                     Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
                    QApplication.sendEvent(self._target or w, me)
                self._pressed = False
                self._target = None
                return True

        return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cable Tester V2")

    # Forceer touch->mouse
    app.installEventFilter(TouchToMouseFilter())

    w = MainWindow()
    w.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
