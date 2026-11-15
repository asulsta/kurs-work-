import pandas as pd
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ReportExporter:
    @staticmethod
    def to_excel(table, filename):
        try:
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            data = [[table.item(r, c).text() if table.item(r, c) else "" for c in range(table.columnCount())] for r in range(table.rowCount())]
            df = pd.DataFrame(data, columns=headers)
            path, _ = QFileDialog.getSaveFileName(None, "Сохранить Excel", f"{filename}.xlsx", "Excel (*.xlsx)")
            if path:
                df.to_excel(path, index=False)
                QMessageBox.information(None, "Успех", "Excel-отчет создан!")
        except Exception as e: QMessageBox.critical(None, "Ошибка", str(e))

    @staticmethod
    def to_pdf(table, filename):
        try:
            path, _ = QFileDialog.getSaveFileName(None, "Сохранить PDF", f"{filename}.pdf", "PDF (*.pdf)")
            if not path: return
            c = canvas.Canvas(path)
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                c.setFont('Arial', 10)
            except: c.setFont('Helvetica', 8)
            y = 800
            c.drawString(50, y, f"ОТЧЕТ БИБЛИОТЕКИ: {filename.upper()}"); y -= 30
            for r in range(table.rowCount()):
                line = " | ".join([table.item(r, c).text()[:15] if table.item(r, c) else "" for c in range(table.columnCount())])
                c.drawString(30, y, line); y -= 15
                if y < 50: c.showPage(); y = 800
            c.save()
            QMessageBox.information(None, "Успех", "PDF-отчет создан!")
        except Exception as e: QMessageBox.critical(None, "Ошибка PDF", str(e))
