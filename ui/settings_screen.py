import socket
import subprocess

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from ui.screens import connect_safe_press


class SettingsScreen(QWidget):
    back = pyqtSignal()
    updateTriggered = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Settings")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.lblIp = QLabel("IP: ophalen...")
        self.lblIp.setObjectName("Hint")
        layout.addWidget(self.lblIp)

        self.lblVersion = QLabel("Versie: onbekend")
        self.lblVersion.setObjectName("Hint")
        layout.addWidget(self.lblVersion)

        self.lblUpdateStatus = QLabel("")
        self.lblUpdateStatus.setObjectName("Hint")
        layout.addWidget(self.lblUpdateStatus)

        btn_update = QPushButton("UPDATE SOFTWARE")
        btn_update.setMinimumHeight(50)
        connect_safe_press(btn_update, self.updateTriggered.emit, delay_ms=80)
        layout.addWidget(btn_update)

        btn_back = QPushButton("TERUG")
        btn_back.setMinimumHeight(45)
        connect_safe_press(btn_back, self.back.emit, delay_ms=80)
        layout.addWidget(btn_back)

        layout.addStretch(1)

        self.refresh_info()

    def refresh_info(self):
        self.lblIp.setText(f"IP: {self.get_ip_address()}")
        self.lblVersion.setText(f"Versie: {self.get_git_version()}")

    @staticmethod
    def get_ip_address() -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return "Geen netwerk"

    @staticmethod
    def get_git_version() -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd="/home/pi/cable-tester",
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception:
            return "Onbekend"