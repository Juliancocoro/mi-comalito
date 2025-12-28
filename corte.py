from PyQt5.QtWidgets import (
    QDialog, QTextEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from datetime import datetime
from guardar_corte import guardar_corte


class CorteDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)

        self.ticket = ticket

        self.setWindowTitle("Corte del Día")
        self.setFixedSize(400, 420)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas;
                font-size: 14px;
                background: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        self.text.setText(self.generate_ticket())

        btn_close = QPushButton("GUARDAR Y CERRAR")
        btn_close.setFixedHeight(45)
        btn_close.clicked.connect(self.save_and_close)

        layout.addWidget(self.text)
        layout.addWidget(btn_close)

    def save_and_close(self):
        try:
            guardar_corte(
                self.ticket.total_vendido,
                self.ticket.tickets_pagados
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar el corte:\n{e}"
            )

    def generate_ticket(self):
        now = datetime.now()

        return f"""
MICHEL - CORTE DEL DÍA
-----------------------------
Fecha: {now.strftime('%d/%m/%Y')}
Hora:  {now.strftime('%H:%M:%S')}

-----------------------------
Tickets cobrados: {self.ticket.tickets_pagados}
Total vendido:    ${self.ticket.total_vendido:.2f}

-----------------------------
FIN DEL CORTE
""".strip()
