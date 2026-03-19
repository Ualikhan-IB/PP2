import psycopg2
import csv
import sys

def connect():
    """Возвращает соединение с PostgreSQL."""
    return psycopg2.connect(
        host="localhost",
        database="phonebook_db",
        user="postgres",
        password="PP2_Ualikhan"   
    )

def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id       SERIAL PRIMARY KEY,
        first_name VARCHAR(50)  NOT NULL,
        last_name  VARCHAR(50),
        phone      VARCHAR(20)  NOT NULL UNIQUE
    );
    """
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print("[OK] Таблица phonebook создана (или уже существует).")
    finally:
        conn.close()

def insert_from_csv(filepath: str):
    conn = connect()
    try:
        cur = conn.cursor()
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cur.execute(
                    """INSERT INTO phonebook (first_name, last_name, phone)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (phone) DO NOTHING""",
                    (row["first_name"], row.get("last_name", ""), row["phone"])
                )
                count += 1
        conn.commit()
        print(f"[OK] Загружено {count} записей из {filepath}.")
    except FileNotFoundError:
        print(f"[ERR] Файл не найден: {filepath}")
    finally:
        conn.close()

def insert_from_console():
    first_name = input("Имя      : ").strip()
    last_name  = input("Фамилия  : ").strip()
    phone      = input("Телефон  : ").strip()

    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO phonebook (first_name, last_name, phone)
               VALUES (%s, %s, %s)
               ON CONFLICT (phone) DO NOTHING""",
            (first_name, last_name, phone)
        )
        conn.commit()
        print(f"[OK] Контакт '{first_name} {last_name}' добавлен.")
    finally:
        conn.close()

def update_contact():
    print("Что обновить?  1 — имя   2 — телефон")
    choice = input("Выбор: ").strip()

    phone = input("Текущий телефон контакта: ").strip()

    conn = connect()
    try:
        cur = conn.cursor()
        if choice == "1":
            new_name = input("Новое имя: ").strip()
            cur.execute(
                "UPDATE phonebook SET first_name = %s WHERE phone = %s",
                (new_name, phone)
            )
        elif choice == "2":
            new_phone = input("Новый телефон: ").strip()
            cur.execute(
                "UPDATE phonebook SET phone = %s WHERE phone = %s",
                (new_phone, phone)
            )
        else:
            print("[ERR] Неверный выбор.")
            return
        conn.commit()
        print("[OK] Данные обновлены.")
    finally:
        conn.close()

def query_contacts():
    print("Фильтр:  1 — все   2 — по имени   3 — по телефону")
    choice = input("Выбор: ").strip()

    conn = connect()
    try:
        cur = conn.cursor()
        if choice == "1":
            cur.execute("SELECT id, first_name, last_name, phone FROM phonebook ORDER BY last_name, first_name")
        elif choice == "2":
            name = input("Имя (частично): ").strip()
            cur.execute(
                "SELECT id, first_name, last_name, phone FROM phonebook "
                "WHERE first_name ILIKE %s OR last_name ILIKE %s "
                "ORDER BY last_name",
                (f"%{name}%", f"%{name}%")
            )
        elif choice == "3":
            phone = input("Телефон (частично): ").strip()
            cur.execute(
                "SELECT id, first_name, last_name, phone FROM phonebook "
                "WHERE phone LIKE %s",
                (f"%{phone}%",)
            )
        else:
            print("[ERR] Неверный выбор.")
            return

        rows = cur.fetchall()
        if rows:
            print(f"\n{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Телефон'}")
            print("-" * 50)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<15} {row[2] or '':<15} {row[3]}")
        else:
            print("[INFO] Записи не найдены.")
    finally:
        conn.close()

def delete_contact():
    print("Удалить по:  1 — имени   2 — телефону")
    choice = input("Выбор: ").strip()

    conn = connect()
    try:
        cur = conn.cursor()
        if choice == "1":
            name = input("Имя: ").strip()
            cur.execute("DELETE FROM phonebook WHERE first_name = %s", (name,))
        elif choice == "2":
            phone = input("Телефон: ").strip()
            cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
        else:
            print("[ERR] Неверный выбор.")
            return
        deleted = cur.rowcount
        conn.commit()
        print(f"[OK] Удалено записей: {deleted}.")
    finally:
        conn.close()

def menu():
    create_table()
    while True:
        print("\n===== PhoneBook =====")
        print("1. Добавить из CSV")
        print("2. Добавить вручную")
        print("3. Обновить контакт")
        print("4. Поиск / просмотр")
        print("5. Удалить контакт")
        print("0. Выход")
        choice = input("Выбор: ").strip()

        if   choice == "1": insert_from_csv(input("Путь к CSV: ").strip())
        elif choice == "2": insert_from_console()
        elif choice == "3": update_contact()
        elif choice == "4": query_contacts()
        elif choice == "5": delete_contact()
        elif choice == "0": sys.exit(0)
        else: print("[ERR] Неверный ввод.")

if __name__ == "__main__":
    menu()
