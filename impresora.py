"""
Módulo de impresión para tickets térmicos ESC/POS
Soporta impresoras USB, de red y Windows
Si no hay impresora, no genera errores
"""

import os
import sys
from datetime import datetime


class PrinterManager:
    """Administra la conexión y configuración de impresoras térmicas"""

    def __init__(self):
        self.printer = None
        self.printer_type = None
        self.config = self.load_config()

    def load_config(self):
        """Carga configuración de impresora desde archivo"""
        try:
            import json
            from pathlib import Path

            config_file = Path("printer_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self, config):
        """Guarda configuración de impresora"""
        try:
            import json

            with open("printer_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.config = config
        except Exception as e:
            print(f"Error guardando config: {e}")

    def detect_usb_printers(self):
        """Detecta impresoras USB conectadas"""
        printers = []

        try:
            import usb.core
            import usb.util

            devices = usb.core.find(find_all=True)
            if devices is None:
                return printers

            for device in devices:
                try:
                    vendor_id = device.idVendor
                    product_id = device.idProduct

                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) or "Desconocido"
                    except:
                        manufacturer = "Desconocido"

                    try:
                        product = usb.util.get_string(device, device.iProduct) or "Dispositivo USB"
                    except:
                        product = "Dispositivo USB"

                    is_printer = False

                    if device.bDeviceClass == 7:
                        is_printer = True

                    try:
                        for cfg in device:
                            for intf in cfg:
                                if intf.bInterfaceClass == 7:
                                    is_printer = True
                                    break
                    except:
                        pass

                    known_printer_vendors = [
                        0x04b8, 0x0519, 0x0dd4, 0x0fe6, 0x1504,
                        0x0416, 0x0483, 0x1fc9, 0x0525, 0x28e9,
                        0x6868, 0x0456, 0x067b, 0x1a86, 0x10c4
                    ]

                    if vendor_id in known_printer_vendors:
                        is_printer = True

                    product_lower = product.lower() if product else ""
                    if any(kw in product_lower for kw in ['printer', 'pos', 'receipt', 'thermal', 'escpos']):
                        is_printer = True

                    if is_printer:
                        printers.append({
                            "type": "usb",
                            "vendor_id": vendor_id,
                            "product_id": product_id,
                            "manufacturer": manufacturer,
                            "product": product,
                            "name": f"{manufacturer} - {product}",
                            "id": f"0x{vendor_id:04x}:0x{product_id:04x}"
                        })

                except:
                    continue

        except ImportError:
            pass
        except:
            pass

        return printers

    def detect_windows_printers(self):
        """Detecta impresoras instaladas en Windows"""
        printers = []

        if sys.platform != 'win32':
            return printers

        try:
            import win32print

            printer_list = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )

            for printer in printer_list:
                printers.append({
                    "type": "windows",
                    "name": printer[2],
                    "id": printer[2]
                })

        except ImportError:
            pass
        except:
            pass

        return printers

    def get_all_printers(self):
        """Obtiene todas las impresoras disponibles"""
        all_printers = []

        usb_printers = self.detect_usb_printers()
        all_printers.extend(usb_printers)

        if sys.platform == 'win32':
            win_printers = self.detect_windows_printers()
            all_printers.extend(win_printers)

        return all_printers

    def connect_usb(self, vendor_id, product_id):
        """Conecta a una impresora USB"""
        try:
            from escpos.printer import Usb
            self.printer = Usb(vendor_id, product_id, 0)
            self.printer_type = "usb"
            return True
        except:
            return False

    def connect_network(self, ip, port=9100):
        """Conecta a una impresora de red"""
        try:
            from escpos.printer import Network
            self.printer = Network(ip, port)
            self.printer_type = "network"
            return True
        except:
            return False

    def connect_windows(self, printer_name):
        """Conecta a una impresora de Windows"""
        try:
            from escpos.printer import Win32Raw
            self.printer = Win32Raw(printer_name)
            self.printer_type = "windows"
            return True
        except:
            return False

    def connect_from_config(self):
        """Conecta usando la configuración guardada"""
        if not self.config:
            return False

        printer_type = self.config.get("type")

        try:
            if printer_type == "usb":
                return self.connect_usb(
                    self.config.get("vendor_id"),
                    self.config.get("product_id")
                )
            elif printer_type == "network":
                return self.connect_network(
                    self.config.get("ip"),
                    self.config.get("port", 9100)
                )
            elif printer_type == "windows":
                return self.connect_windows(
                    self.config.get("name")
                )
        except:
            pass

        return False

    def is_connected(self):
        """Verifica si hay una impresora conectada"""
        return self.printer is not None

    def print_ticket(self, items, total, ticket_num=None):
        """Imprime un ticket de venta"""
        if not self.printer:
            return False

        try:
            p = self.printer
            now = datetime.now()

            p.set(align='center')
            p.text("================================\n")
            p.set(align='center', text_type='B', width=2, height=2)
            p.text("MICHEL\n")
            p.set(align='center', text_type='normal', width=1, height=1)
            p.text("Gorditas y Antojitos\n")
            p.text("================================\n")

            p.text(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
            p.text(f"Hora:  {now.strftime('%H:%M:%S')}\n")

            if ticket_num:
                p.text(f"Ticket: #{ticket_num}\n")

            p.text("--------------------------------\n")

            p.set(align='left')

            for item in items:
                qty = item.get("qty", 1)
                categoria = item.get("categoria", "")
                tipo = item.get("tipo", "")
                subtotal = item.get("subtotal", 0)

                producto = f"{categoria}"
                if tipo:
                    producto += f" - {tipo}"

                p.text(f"{qty} x {producto}\n")
                p.set(align='right')
                p.text(f"${subtotal:.2f}\n")
                p.set(align='left')

            p.text("--------------------------------\n")

            p.set(align='right', text_type='B', width=2, height=2)
            p.text(f"TOTAL: ${total:.2f}\n")

            p.set(align='center', text_type='normal', width=1, height=1)
            p.text("================================\n")
            p.text("GRACIAS POR SU COMPRA!\n")
            p.text("================================\n")

            p.text("\n\n\n")
            p.cut()

            return True

        except:
            return False

    def print_test(self):
        """Imprime una página de prueba"""
        if not self.printer:
            return False

        try:
            p = self.printer
            now = datetime.now()

            p.set(align='center')
            p.text("================================\n")
            p.set(align='center', text_type='B', width=2, height=2)
            p.text("PRUEBA\n")
            p.set(align='center', text_type='normal', width=1, height=1)
            p.text("================================\n")
            p.text(f"Fecha: {now.strftime('%d/%m/%Y %H:%M')}\n")
            p.text("\n")
            p.text("Si puedes leer esto,\n")
            p.text("la impresora funciona\n")
            p.text("correctamente!\n")
            p.text("\n")
            p.text("================================\n")
            p.text("\n\n\n")
            p.cut()

            return True

        except:
            return False

    def print_corte(self, total_vendido, tickets_pagados):
        """Imprime el corte del día"""
        if not self.printer:
            return False

        try:
            p = self.printer
            now = datetime.now()

            p.set(align='center')
            p.text("================================\n")
            p.set(align='center', text_type='B', width=2, height=2)
            p.text("CORTE DEL DIA\n")
            p.set(align='center', text_type='normal', width=1, height=1)
            p.text("MICHEL\n")
            p.text("================================\n")

            p.text(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
            p.text(f"Hora:  {now.strftime('%H:%M:%S')}\n")

            p.text("--------------------------------\n")

            p.set(align='left')
            p.text(f"Tickets cobrados: {tickets_pagados}\n")

            p.set(align='right', text_type='B', width=2, height=1)
            p.text(f"TOTAL: ${total_vendido:.2f}\n")

            p.set(align='center', text_type='normal', width=1, height=1)
            p.text("--------------------------------\n")
            p.text("FIN DEL CORTE\n")
            p.text("================================\n")
            p.text("\n\n\n")
            p.cut()

            return True

        except:
            return False