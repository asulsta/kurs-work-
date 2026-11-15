import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from auth_window import AuthWindow
from database import DatabaseManager
from main_window import MainWindow
from two_facthor_window import TwoFactorWindow


class LibraryApp:

  def __init__(self):
    self.app = QApplication(sys.argv)
    self.db = DatabaseManager()
    self.auth_win = None
    self.tfa_win = None
    self.main_win = None

  def run(self):
    self.auth_win = AuthWindow(self.db)
    self.auth_win.login_success.connect(self.handle_login_success)
    self.auth_win.show()
    return self.app.exec()

  def handle_login_success(self):
    self.auth_win.hide()

    # Для библиотекарей отправляем код в Telegram.
    # Для читателей (Role_Reader) код не отправляется — будет вызов Google.
    if self.db.current_role != "Role_Reader":
      ok, msg = self.db.send_2fa_code()
      if not ok:
        QMessageBox.critical(
            None, "Ошибка 2FA", f"Не удалось отправить код в Telegram:\n{msg}"
        )
        self.auth_win.show()
        return

    # Открываем окно 2FA
    self.tfa_win = TwoFactorWindow(self.db)
    self.tfa_win.verification_success.connect(self.show_main)
    self.tfa_win.show()

  def show_main(self):
    """Переход в главное окно после успешной проверки 2FA"""
    try:
      self.main_win = MainWindow(self.db, self.auth_win)
      self.main_win.show()
    except Exception as e:
      QMessageBox.critical(
          None,
          "Ошибка запуска",
          f"Не удалось открыть главное окно:\n{str(e)}",
      )


if __name__ == "__main__":
  client_app = LibraryApp()
  sys.exit(client_app.run())