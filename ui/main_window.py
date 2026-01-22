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

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(CATALOG)
        self.test = TestScreen()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.test)

        self.home.cableSelected.connect(self.open_test)
        self.test.back.connect(self.go_home)
        self.test.startTest.connect(self.run_test)

    def open_test(self, key):
        p = self.pinouts[key]
        self.test.lblTitle.setText(p.title)
        self.test.set_pins(p.pins)
        self.stack.setCurrentWidget(self.test)

    def go_home(self):
        self.stack.setCurrentWidget(self.home)

   def run_test(self):
    # Bepaal welke pinout actief is op basis van titel
    title = self.test.lblTitle.text()
    selected = None
    for p in self.pinouts.values():
        if p.title == title:
            selected = p
            break
    if not selected:
        return

    result = self.engine.run_test(selected.pins)

    # result.per_pin geeft "ok"/"fail" -> we mappen fail naar "bad"
    per_pin = {str(k): ("ok" if v == "ok" else "bad") for k, v in result.per_pin.items()}
    self.test.apply_result(per_pin, result.passed)
