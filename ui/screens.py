from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QScrollArea,
)


def connect_safe_press(button: QPushButton, callback, delay_ms: int = 80):
    """
    Resistive touch kan op het eerste contactpunt jitteren.
    We bevestigen de press pas na korte delay en alleen
    als de pointer nog steeds binnen dezelfde knop zit.
    """
    button.setAutoRepeat(False)

    def on_pressed():
        def confirm():
            pos = button.mapFromGlobal(QCursor.pos())
            if button.rect().contains(pos):
                callback()

        QTimer.singleShot(delay_ms, confirm)

    button.pressed.connect(on_pressed)


class HomeScreen(QWidget):
    cableSelected = pyqtSignal(str)
    openSettings = pyqtSignal()

    def __init__(self, pinouts):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Cable Tester V2.2")
        title.setObjectName("Title")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        for i, p in enumerate(pinouts):
            btn = QPushButton(p.title)
            btn.setMinimumHeight(60)
            connect_safe_press(
                btn,
                lambda k=p.key: self.cableSelected.emit(k),
                delay_ms=80,
            )
            grid.addWidget(btn, i // 2, i % 2)

        card = QFrame()
        card.setObjectName("Card")
        card.setLayout(grid)
        layout.addWidget(card, 1)

        btn_settings = QPushButton("SETTINGS")
        btn_settings.setMinimumHeight(45)
        connect_safe_press(btn_settings, self.openSettings.emit, delay_ms=80)
        layout.addWidget(btn_settings)


class TestScreen(QWidget):
    back = pyqtSignal()
    startTest = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.lblTitle = QLabel("")
        self.lblTitle.setObjectName("Title")
        layout.addWidget(self.lblTitle)

        self.lblStatus = QLabel("Klaar voor test")
        self.lblStatus.setObjectName("Hint")
        layout.addWidget(self.lblStatus)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setLayout(self.grid)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self.card)

        layout.addWidget(scroll, 1)

        btn_test = QPushButton("TEST")
        btn_test.setMinimumHeight(45)
        connect_safe_press(btn_test, self.startTest.emit, delay_ms=80)
        layout.addWidget(btn_test)

        btn_back = QPushButton("TERUG")
        btn_back.setMinimumHeight(45)
        connect_safe_press(btn_back, self.back.emit, delay_ms=80)
        layout.addWidget(btn_back)

        self._pin_labels: dict[str, QLabel] = {}

    def set_pins(self, pins: list[str]):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._pin_labels.clear()
        self.lblStatus.setText("Klaar voor test")

        for i, pin in enumerate(pins):
            pin_str = str(pin)

            lbl = QLabel(f"PIN {pin_str}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("state", "idle")
            lbl.setStyleSheet("""
                QLabel {
                    border: 1px solid #2a3142;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 17px;
                    background: #0f1115;
                }
                QLabel[state="idle"] { color: #9aa3b2; }
                QLabel[state="ok"]   { color: #1ecf6a; border-color: #1ecf6a; }
                QLabel[state="bad"]  { color: #ff4d4d; border-color: #ff4d4d; }
            """)

            self._pin_labels[pin_str] = lbl
            self.grid.addWidget(lbl, i // 4, i % 4)

    def apply_result(self, per_pin: dict[str, str], passed: bool):
        for pin, state in per_pin.items():
            lbl = self._pin_labels.get(str(pin))
            if not lbl:
                continue

            lbl.setProperty("state", "ok" if state == "ok" else "bad")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

        self.lblStatus.setText("PASS ✅" if passed else "FAIL ❌")