from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class PaymentDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)

        self.ticket = ticket

        self.setWindowTitle("Pago")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("TOTAL A PAGAR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        total = QLabel(f"${self.ticket.total:.2f}")
        total.setAlignment(Qt.AlignCenter)
        total.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #1a73e8;"
        )

        btn_pay = QPushButton("CONFIRMAR PAGO")
        btn_pay.setFixedHeight(60)
        btn_pay.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 16px;
            }
        """)

        btn_pay.clicked.connect(self.confirm_payment)

        layout.addWidget(title)
        layout.addWidget(total)
        layout.addStretch()
        layout.addWidget(btn_pay)

    def confirm_payment(self):
        self.ticket.total_vendido += self.ticket.total
        self.ticket.tickets_pagados += 1

        QMessageBox.information(self, "Pago", "Pago realizado con éxito")
        self.ticket.clear()
        self.accept()
