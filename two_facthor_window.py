from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TwoFactorWindow(QWidget):
  verification_success = pyqtSignal()

  def __init__(self, db_manager):
    super().__init__()
    self.db = db_manager
    self.setWindowTitle('Двухфакторная аутентификация')
    self.setFixedSize(320, 200)

    self.is_reader = self.db.current_role == 'Role_Reader'

    lay = QVBoxLayout()

    if self.is_reader:
      lay.addWidget(
          QLabel('Для роли Читатель требуется подтверждение через Google:')
      )

      self.btn_google = QPushButton('🌐 Войти через Google')
      self.btn_google.setStyleSheet(
          'background-color: #4285F4; color: white; font-weight: bold;'
          ' padding: 8px;'
      )
      self.btn_google.clicked.connect(self.verify_google)
      lay.addWidget(self.btn_google)
    else:
      lay.addWidget(QLabel('Введите 6-значный код из Telegram:'))
      self.code_input = QLineEdit()
      self.code_input.setPlaceholderText('Код из сообщения')
      lay.addWidget(self.code_input)

      self.btn_verify = QPushButton('Войти')
      self.btn_verify.clicked.connect(self.verify_telegram_code)
      lay.addWidget(self.btn_verify)

      self.btn_resend = QPushButton('Отправить код повторно')
      self.btn_resend.clicked.connect(self.resend_telegram_code)
      lay.addWidget(self.btn_resend)

    self.setLayout(lay)

  def verify_google(self):
    ok, msg = self.db.authenticate_reader_via_google()
    if ok:
      QMessageBox.information(self, 'Успех 2FA', msg)
      self.verification_success.emit()
      self.close()
    else:
      QMessageBox.critical(self, 'Ошибка Google 2FA', msg)

  def verify_telegram_code(self):
    code = self.code_input.text().strip()
    if not code:
      QMessageBox.warning(self, 'Внимание', 'Введите код подтверждения!')
      return

    ok, msg = self.db.verify_2fa_code(code)
    if ok:
      QMessageBox.information(self, 'Успех', msg)
      self.verification_success.emit()
      self.close()
    else:
      QMessageBox.critical(self, 'Ошибка 2FA', msg)

  def resend_telegram_code(self):
    ok, msg = self.db.send_2fa_code()
    if ok:
      QMessageBox.information(self, 'Успех', 'Новый код отправлен в Telegram!')
    else:
      QMessageBox.critical(self, 'Ошибка', msg)