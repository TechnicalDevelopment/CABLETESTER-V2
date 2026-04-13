import subprocess

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from ui.theme import APP_QSS
from ui.screens import HomeScreen, TestScreen
from ui.settings_screen import SettingsScreen
from pinouts.catalog import CATALOG
from gpio.engine import GpioEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(APP_QSS)

        self.engine = GpioEngine(mock=True)
        self.pinouts = {p.key: p for p in CATALOG}
        self.active_key = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(CATALOG)
        self.test = TestScreen()
        self.settings = SettingsScreen()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.test)
        self.stack.addWidget(self.settings)

        self.home.cableSelected.connect(self.open_test)
        self.home.openSettings.connect(self.open_settings)

        self.test.back.connect(self.go_home)
        self.test.startTest.connect(self.run_test)

        self.settings.back.connect(self.go_home)
        self.settings.updateTriggered.connect(self.run_update)

    def open_test(self, key: str):
        self.active_key = key
        p = self.pinouts[key]
        self.test.lblTitle.setText(p.title)
        self.test.set_pins(p.pins)
        self.stack.setCurrentWidget(self.test)

    def open_settings(self):
        self.settings.lblUpdateStatus.setText("")
        self.settings.refresh_info()
        self.stack.setCurrentWidget(self.settings)

    def go_home(self):
        self.active_key = None
        self.stack.setCurrentWidget(self.home)

    def run_test(self):
        if not self.active_key:
            return

        p = self.pinouts[self.active_key]
        result = self.engine.run_test(p.pins)

        per_pin = {}
        for k, v in result.per_pin.items():
            per_pin[str(k)] = "ok" if v == "ok" else "bad"

        self.test.apply_result(per_pin, result.passed)

    def run_update(self):
        self.settings.lblUpdateStatus.setText("Update gestart...")

        try:
            subprocess.Popen(
                ["sudo", "/home/pi/cable-tester/update.sh"]
            )
            self.settings.lblUpdateStatus.setText("Update loopt, app wordt herstart...")

        except Exception as exc:
            self.settings.lblUpdateStatus.setText(f"Update fout: {str(exc)[:120]}")