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
        # Mock run; GPIO komt later
        pass
