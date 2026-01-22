from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from ui.theme import APP_QSS
from ui.screens import HomeScreen, TestScreen
from pinouts.catalog import CATALOG
from gpio.engine import GpioEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(APP_QSS)

        self.engine = GpioEngine(mock=True)
        self.pinouts = {p.key: p for p in CATALOG}
        self.active_key = None  # <- onthoud selectie

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(CATALOG)
        self.test = TestScreen()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.test)

        self.home.cableSelected.connect(self.open_test)
        self.test.back.connect(self.go_home)
        self.test.startTest.connect(self.run_test)

    def open_test(self, key: str):
        self.active_key = key
        p = self.pinouts[key]
        self.test.lblTitle.setText(p.title)
        self.test.set_pins(p.pins)
        self.stack.setCurrentWidget(self.test)

    def go_home(self):
        self.active_key = None
        self.stack.setCurrentWidget(self.home)

    def run_test(self):
        if not self.active_key:
            return

        p = self.pinouts[self.active_key]
        result = self.engine.run_test(p.pins)

        # result.per_pin: "ok" of "fail" -> map naar ok/bad
        per_pin = {}
        for k, v in result.per_pin.items():
            per_pin[str(k)] = "ok" if v == "ok" else "bad"

        self.test.apply_result(per_pin, result.passed)
