from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QFrame
)
from PyQt5.QtCore import Qt


class PostresDialog(QDialog):
    def __init__(self, parent, edit_data=None, edit_row=None):
        super().__init__(parent)

        self.parent = parent

        self.setWindowTitle("Postres")
        self.setFixedSize(400, 350)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Postres")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        btn_style = """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 14px;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """

        btn_platanos = QPushButton("Plátanos fritos  $35")
        btn_pan = QPushButton("Pan dulce  $15")
        btn_arroz = QPushButton("Arroz con leche  $25")

        for btn in (btn_platanos, btn_pan, btn_arroz):
            btn.setStyleSheet(btn_style)
            btn.setFixedHeight(60)

        btn_platanos.clicked.connect(
            lambda: self.add_postre("Plátanos fritos", 35)
        )
        btn_pan.clicked.connect(
            lambda: self.add_postre("Pan dulce", 15)
        )
        btn_arroz.clicked.connect(
            lambda: self.add_postre("Arroz con leche", 25)
        )

        layout.addWidget(title)
        layout.addWidget(btn_platanos)
        layout.addWidget(btn_pan)
        layout.addWidget(btn_arroz)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

    def add_postre(self, tipo, price):
        data = {
            "categoria": "Postres",
            "tipo": tipo,
            "qty": 1,
            "price": price
        }

        self.parent.add_product(data)
        self.accept()
