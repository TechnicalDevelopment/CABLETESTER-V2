from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame
)


def connect_safe_press(button: QPushButton, callback, delay_ms: int = 80):
    """
    Resistive touch (ADS7846): eerste contactpunt kan jitteren.
    We activeren pas na een korte delay én alleen als de pointer nog steeds
    binnen dezelfde knop zit. Dit voorkomt "verkeerde button" missers.
    """
    button.setAutoRepeat(False)

    def on_pressed():
        def confirm():
            # Cursorpositie opvragen en naar button-local coordinates mappen
            pos = button.mapFromGlobal(QCursor.pos())
            if button.rect().contains(pos):
                callback()

        QTimer.singleShot(delay_ms, confirm)

    button.pressed.connect(on_pressed)


class HomeScreen(QWidget):
    cableSelected = pyqtSignal(str)

    def __init__(self, pinouts):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Cable Tester V2")
        title.setObjectName("Title")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(16)

        for i, p in enumerate(pinouts):
            btn = QPushButton(p.title)

            # Touch-friendly sizing
            btn.setMinimumHeight(80)

            # Safe press (i.p.v. clicked/pressed direct)
            connect_safe_press(btn, lambda k=p.key: self.cableSelected.emit(k), delay_ms=80)

            grid.addWidget(btn, i // 2, i % 2)

        card = QFrame()
        card.setObjectName("Card")
        card.setLayout(grid)
        layout.addWidget(card, 1)

class TestScreen(QWidget):
    back = pyqtSignal()
    startTest = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.lblTitle = QLabel("")
        self.lblTitle.setObjectName("Title")
        self.layout.addWidget(self.lblTitle)

        self.lblStatus = QLabel("Klaar voor test")
        self.lblStatus.setObjectName("Hint")
        self.layout.addWidget(self.lblStatus)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)

        card = QFrame()
        card.setObjectName("Card")
        card.setLayout(self.grid)
        self.layout.addWidget(card, 1)

        btnTest = QPushButton("TEST")
        btnTest.setMinimumHeight(80)
        connect_safe_press(btnTest, self.startTest.emit, delay_ms=80)
        self.layout.addWidget(btnTest)

        btnBack = QPushButton("TERUG")
        btnBack.setMinimumHeight(80)
        connect_safe_press(btnBack, self.back.emit, delay_ms=80)
        self.layout.addWidget(btnBack)

        self._pin_labels = {}  # pin -> QLabel

    def set_pins(self, pins):
        # Clear grid safely
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._pin_labels.clear()
        self.lblStatus.setText("Klaar voor test")

        for i, p in enumerate(pins):
            lbl = QLabel(f"PIN {p}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("state", "idle")
            lbl.setStyleSheet("""
                QLabel {
                    border: 1px solid #2a3142;
                    border-radius: 10px;
                    padding: 14px;
                    font-size: 18px;
                    background: #0f1115;
                }
                QLabel[state="idle"] { color: #9aa3b2; }
                QLabel[state="ok"]   { color: #1ecf6a; border-color: #1ecf6a; }
                QLabel[state="bad"]  { color: #ff4d4d; border-color: #ff4d4d; }
            """)
            self._pin_labels[str(p)] = lbl
            self.grid.addWidget(lbl, i // 4, i % 4)

    def apply_result(self, per_pin: dict, passed: bool):
        for pin, state in per_pin.items():
            lbl = self._pin_labels.get(str(pin))
            if not lbl:
                continue
            lbl.setProperty("state", "ok" if state == "ok" else "bad")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

        self.lblStatus.setText("PASS ✅" if passed else "FAIL ❌")
