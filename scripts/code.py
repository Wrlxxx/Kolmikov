import os
import sqlite3
from tabulate import tabulate

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()
    
    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()

def register_user(db, username, password, role):
    """Регистрирует нового пользователя с заданным именем, паролем и ролью."""
    try:
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))
        print("Пользователь успешно зарегистрирован.")
    except sqlite3.IntegrityError:
        print("Пользователь с таким именем уже существует.")

def authenticate_user(db, username, password):
    """Аутентифицирует пользователя по имени и паролю."""
    db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return db.fetchone()

def display_welcome_message(username):
    """Выводит приветственное сообщение для пользователя."""
    print(f"Добро пожаловать в функциональный режим, {username}!")

def user_info(username, role):
    """Выводит информацию о пользователе."""
    print(f"Имя пользователя: {username}")
    print(f"Роль: {role}")

def main_menu(db, user_db):
    """Основное меню для выбора действия."""
    while True:
        print("\n1. Вход")
        print("2. Регистрация")
        print("3. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            user = authenticate_user(user_db, username, password)
            if user:
                display_welcome_message(user[1])
                if user[3] == 'user':
                    user_menu(db, user[1], user[3])
                else:
                    admin_menu(db, user[1], user[3])    
            else:
                print("Неверное имя пользователя или пароль.")
        elif choice == '2':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            role = input("Введите роль: ")
            register_user(user_db, username, password, role)
        elif choice == '3':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

def user_menu(db, username, user_role):
    """Меню для пользователя с ролью 'user'."""
    while True:
        print("\nМеню пользователя:")
        print("1. Информация о пользователе")
        print("2. Просмотр таблиц")
        print("3. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            user_info(username, user_role)  
        elif choice == '2':
            show_tables(db)
            sql_command = input("Введите команду SELECT * FROM <таблица>: ")
            if sql_command.strip().upper().startswith("SELECT * FROM"):
                if "users" in sql_command.lower():
                    print("У вас нет разрешения на просмотр таблицы 'users'.")
                else:
                    execute_sql_command(db, sql_command)
            else:
                print("Неверная команда. Используйте формат 'SELECT * FROM <таблица>'.")
        elif choice == '3':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

def admin_menu(db, username, user_role):
    """Меню для пользователя с ролью 'admin'."""
    while True:
        print("\nМеню администратора:")
        print("1. Информация о пользователе")
        print("2. Выполнить SQL команду")
        print("3. Помощь")
        print("4. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            user_info(username, user_role)  
        elif choice == '2':
            sql_command = input("\nВведите SQL команду (или 'выход' для выхода): ")
            
            if sql_command.lower() == 'выход':
                break
            elif sql_command.lower() == 'help':
                print_help(user_role)  
                continue
            
            execute_sql_command(db, sql_command)
        elif choice == '3':
            print_help(user_role)  
        elif choice == '4':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

def execute_sql_command(db, command):
    """Выполняет SQL-команду и обрабатывает результаты."""
    try:
        db.execute(command)
        if command.strip().upper().startswith("SELECT"):
            results = db.fetchall()
            headers = [description[0] for description in db.cursor.description]
            print(tabulate(results, headers=headers, tablefmt="grid"))
        else:
            print("Команда выполнена успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка выполнения команды: {e}")

def show_tables(db):
    """Отображает все существующие таблицы в базе данных."""
    db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = db.fetchall()
    if tables:
        print("\nСуществующие таблицы:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("Нет существующих таблиц.")

def print_help(user_role):
    """Выводит список доступных SQL-команд в зависимости от роли пользователя."""
    if user_role == 'user':
        help_text = """
Доступные команды для вас:
1. SELECT * FROM <таблица> - Просмотр всех записей из указанной таблицы.
"""
    else:
        help_text = """
Доступные команды:
1. SELECT * FROM <таблица> - Просмотр всех записей из указанной таблицы.
2. INSERT INTO <таблица> (...) VALUES (...) - Добавление новой записи.
3. UPDATE <таблица> SET <поля> WHERE <условие> - Обновление записи.
4. DELETE FROM <таблица> WHERE <условие> - Удаление записи.
5. CREATE TABLE <имя таблицы> (...) - Создание новой таблицы.
6. DROP TABLE <имя таблицы> - Удаление таблицы.
7. HELP - Показать список доступных команд.
8. EXIT - Выход из интерфейса SQL.
"""
    print(help_text)

def list_databases(directory):
    """Возвращает список файлов баз данных в указанной директории."""
    return [f for f in os.listdir(directory) if f.endswith('.db')]

def select_database(directory):
    """Позволяет пользователю выбрать базу данных из списка."""
    databases = list_databases(directory)
    if not databases:
        print("В указанной директории нет баз данных.")
        return None

    print("Доступные базы данных:")
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db}")

    choice = input("Выберите базу данных (введите номер): ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(databases):
            return os.path.join(directory, databases[choice - 1])
        else:
            print("Неверный выбор.")
            return None
    except ValueError:
        print("Пожалуйста, введите число.")
        return None

def main():
    while True:
        base_dir = os.path.dirname(__file__)
        directory = os.path.join(base_dir, '..', 'alldb')
        user_db_path = os.path.join(base_dir, '..', 'user', 'users.db')

        db_path = select_database(directory)
        if db_path:
            db = Database(db_path)
            user_db = Database(user_db_path)
            try:
                main_menu(db, user_db)
            finally:
                db.close()
                user_db.close()
        
        choice = input("Хотите выбрать другую базу данных? (да/нет): ").strip().lower()
        if choice != 'да':
            break

if __name__ == "__main__":
    main()