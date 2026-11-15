from datetime import datetime, timedelta
import random
import string
import pyodbc
import requests
from google_auth_oauthlib.flow import InstalledAppFlow


class DatabaseManager:

  def __init__(self):
    self.server = "alans"
    self.database = "Stud_SultanovAlan"
    self.connection = None
    self.cursor = None
    self.current_role = None
    self.user_login = None

    self.bot_token = "8760268173:AAGvorCwfWRihyXOghMXFfexwkYT2vCtj58"
    self.chat_id = "846607263"

    self.temp_2fa_code = None
    self.temp_2fa_expires = None

  def connect(self, username, password):
    try:
      conn_str = (
          f"DRIVER={{ODBC Driver 17 for SQL Server}};"
          f"SERVER={self.server};"
          f"DATABASE={self.database};"
          f"UID={username};"
          f"PWD={password};"
          "Encrypt=yes;"
          "TrustServerCertificate=yes;"
      )

      self.connection = pyodbc.connect(conn_str)
      self.cursor = self.connection.cursor()
      self.user_login = username

      self._determine_role()

      return True, "Успешный вход"

    except pyodbc.Error as e:
      error_text = str(e)
      print(error_text)

      if "Login failed for user" in error_text:
        try:
          temp_conn = pyodbc.connect(
              f"DRIVER={{ODBC Driver 17 for SQL Server}};"
              f"SERVER={self.server};"
              f"DATABASE={self.database};"
              "Trusted_Connection=yes;"
              "Encrypt=yes;"
              "TrustServerCertificate=yes;"
          )
          temp_cursor = temp_conn.cursor()
          temp_cursor.execute(
              "SELECT name FROM sys.sql_logins WHERE name = ?", (username,)
          )
          user_exists = temp_cursor.fetchone()
          temp_conn.close()

          if user_exists:
            return False, "Неверный пароль"
          else:
            return False, "Пользователь не зарегистрирован"
        except Exception as check_error:
          return False, f"Ошибка проверки пользователя: {check_error}"

      return False, f"Ошибка подключения: {error_text}"

    except Exception as e:
      return False, f"Неизвестная ошибка: {str(e)}"

  def _determine_role(self):
    roles = ["Role_Reader", "Role_Librarian", "Role_Head", "Role_DBA"]
    for role in roles:
      try:
        self.cursor.execute(f"SELECT IS_ROLEMEMBER('{role}')")
        row = self.cursor.fetchone()
        if row and row[0] == 1:
          self.current_role = role
          break
      except:
        continue

  def send_2fa_code(self):
    """Отправка кода в Telegram (для Библиотекарей)"""
    if not self.user_login:
      return False, "Пользователь не авторизован"

    code = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.now() + timedelta(minutes=2)

    self.temp_2fa_code = code
    self.temp_2fa_expires = expires_at

    try:
      url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
      payload = {
          "chat_id": self.chat_id,
          "text": (
              f"🔑 Код для входа пользователя *{self.user_login}*:"
              f" *{code}*.\n⏱ Действителен ровно 2 минуты."
          ),
          "parse_mode": "Markdown",
      }

      response = requests.post(url, json=payload)
      if response.status_code == 200:
        return True, "Код отправлен в Telegram!"
      else:
        return False, f"Ошибка отправки в Telegram: {response.text}"

    except Exception as e:
      return False, f"Ошибка отправки 2FA: {e}"

  def verify_2fa_code(self, entered_code):
    """Проверка Telegram-кода"""
    if not self.user_login:
      return False, "Пользователь не авторизован"

    if not self.temp_2fa_code or not self.temp_2fa_expires:
      return False, "Код подтверждения не запрашивался"

    if datetime.now() > self.temp_2fa_expires:
      return False, "Время действия кода истекло (2 минуты)!"

    if self.temp_2fa_code == entered_code:
      self.temp_2fa_code = None
      self.temp_2fa_expires = None
      return True, "Вход разрешен!"
    else:
      return False, "Неверный код!"

  def authenticate_reader_via_google(self):
    """Запуск официального окна авторизации Google (без проверки почты)"""
    if self.current_role != "Role_Reader":
      return (
        False,
        "Google-аутентификация предназначена только для роли Читатель!",
      )

    try:
      SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
      ]
      flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_448555809630-6moj40g326clnsbmp7u900155cgtjrsh.apps.googleusercontent.com.json", SCOPES
      )

      # Открывает браузерное окно Google для входа
      credentials = flow.run_local_server(port=0, prompt="select_account")

      # Если окно успешно пройдено и токен получен — вход разрешен
      return True, "Успешный вход через Google!"

    except FileNotFoundError:
      return (
        False,
        "Файл client_secret.json не найден! Положите его рядом со скриптом.",
      )
    except Exception as e:
      return False, f"Ошибка входа через Google: {str(e)}"

  def get_data(self, query, params=None):
    try:
      if params:
        self.cursor.execute(query, params)
      else:
        self.cursor.execute(query)

      cols = [column[0] for column in self.cursor.description]
      rows = self.cursor.fetchall()
      return cols, rows
    except Exception as e:
      return [f"Ошибка: {e}"], []

  def get_next_id(self, table_name, id_column):
    try:
      self.cursor.execute(
          f"SELECT ISNULL(MAX({id_column}), 0) + 1 FROM {table_name}"
      )
      res = self.cursor.fetchone()
      return int(res[0])
    except:
      return 1

  def get_list(self, query):
    try:
      self.cursor.execute(query)
      return self.cursor.fetchall()
    except:
      return []

  def execute_query(self, query, params=None):
    try:
      if params:
        self.cursor.execute(query, tuple(params))
      else:
        self.cursor.execute(query)
      self.connection.commit()
      return True, "Успешно"
    except Exception as e:
      if self.connection:
        self.connection.rollback()
      return False, str(e)