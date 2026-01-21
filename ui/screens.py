from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame
)

class HomeScreen(QWidget):
    cableSelected = pyqtSignal(str)

    def __init__(self, pinouts):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Cable Tester")
        title.setObjectName("Title")
        layout.addWidget(title)

        grid = QGridLayout()
        for i, p in enumerate(pinouts):
            btn = QPushButton(p.title)
            btn.clicked.connect(lambda _, k=p.key: self.cableSelected.emit(k))
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

        self.grid = QGridLayout()
        card = QFrame()
        card.setObjectName("Card")
        card.setLayout(self.grid)
        self.layout.addWidget(card, 1)

        btnTest = QPushButton("TEST")
        btnTest.clicked.connect(self.startTest.emit)
        self.layout.addWidget(btnTest)

        btnBack = QPushButton("TERUG")
        btnBack.clicked.connect(self.back.emit)
        self.layout.addWidget(btnBack)

    def set_pins(self, pins):
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()

        for i, p in enumerate(pins):
            lbl = QLabel(f"PIN {p}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(lbl, i // 4, i % 4)
