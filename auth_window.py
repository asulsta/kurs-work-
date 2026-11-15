from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AuthWindow(QWidget):
  login_success = pyqtSignal()

  def __init__(self, db_manager):
    super().__init__()
    self.db = db_manager
    self.setWindowTitle('Авторизация')
    self.setFixedSize(320, 260)

    lay = QVBoxLayout()

    lay.addWidget(QLabel('Логин SQL Server:'))
    self.u = QLineEdit()
    lay.addWidget(self.u)

    lay.addWidget(QLabel('Пароль:'))
    self.p = QLineEdit()
    self.p.setEchoMode(QLineEdit.EchoMode.Password)
    lay.addWidget(self.p)

    self.btn = QPushButton('Войти в систему')
    self.btn.clicked.connect(self.do_login)
    lay.addWidget(self.btn)

    self.setLayout(lay)

  def do_login(self):
    ok, msg = self.db.connect(self.u.text(), self.p.text())
    if ok:
      self.login_success.emit()
      self.close()
    else:
      QMessageBox.critical(self, 'Ошибка доступа', f'Вход не удался:\n{msg}')