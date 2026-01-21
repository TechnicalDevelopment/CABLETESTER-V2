from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from api import run_test

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cable Tester")

        btn = QPushButton("Test uitvoeren")
        btn.clicked.connect(self.on_test)

        layout = QVBoxLayout()
        layout.addWidget(btn)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def on_test(self):
        result = run_test()
        print(result)
