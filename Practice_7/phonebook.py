import csv
from connect import get_connection


def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) UNIQUE NOT NULL
                );
            """)


def insert_from_csv(filepath):
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                        INSERT INTO phonebook (first_name, phone)
                        VALUES (%s, %s)
                        ON CONFLICT (phone) DO NOTHING;
                    """, (row["first_name"].strip(), row["phone"].strip()))
    print("CSV импортирован.")


def insert_from_console():
    name = input("Имя: ").strip()
    phone = input("Телефон: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO phonebook (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING;
            """, (name, phone))
    print(f"Контакт {name} добавлен.")


def update_contact():
    print("Что обновить?")
    print("1 - Имя  2 - Телефон")
    choice = input("Выбор: ").strip()

    old_phone = input("Введите текущий телефон контакта: ").strip()

    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                new_name = input("Новое имя: ").strip()
                cur.execute("""
                    UPDATE phonebook SET first_name = %s WHERE phone = %s;
                """, (new_name, old_phone))
            elif choice == "2":
                new_phone = input("Новый телефон: ").strip()
                cur.execute("""
                    UPDATE phonebook SET phone = %s WHERE phone = %s;
                """, (new_phone, old_phone))
            else:
                print("Неверный выбор.")
                return
    print("Контакт обновлён.")


def query_contacts():
    print("Фильтр поиска:")
    print("1 - По имени  2 - По префиксу телефона  3 - Все контакты")
    choice = input("Выбор: ").strip()

    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Имя (или часть): ").strip()
                cur.execute("""
                    SELECT id, first_name, phone FROM phonebook
                    WHERE first_name ILIKE %s
                    ORDER BY first_name;
                """, (f"%{name}%",))
            elif choice == "2":
                prefix = input("Префикс телефона (например +7701): ").strip()
                cur.execute("""
                    SELECT id, first_name, phone FROM phonebook
                    WHERE phone LIKE %s
                    ORDER BY phone;
                """, (f"{prefix}%",))
            else:
                cur.execute("SELECT id, first_name, phone FROM phonebook ORDER BY first_name;")

            rows = cur.fetchall()

    if rows:
        print(f"\n{'ID':<5} {'Имя':<20} {'Телефон'}")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]}")
    else:
        print("Контакты не найдены.")


def delete_contact():
    print("Удалить по:")
    print("1 - Имени  2 - Телефону")
    choice = input("Выбор: ").strip()

    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Имя: ").strip()
                cur.execute("DELETE FROM phonebook WHERE first_name = %s;", (name,))
            elif choice == "2":
                phone = input("Телефон: ").strip()
                cur.execute("DELETE FROM phonebook WHERE phone = %s;", (phone,))
            else:
                print("Неверный выбор.")
                return
    print("Контакт удалён.")


def main():
    create_table()

    while True:
        print("\n=== PhoneBook ===")
        print("1 - Импорт из CSV")
        print("2 - Добавить вручную")
        print("3 - Обновить контакт")
        print("4 - Поиск контактов")
        print("5 - Удалить контакт")
        print("0 - Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            path = input("Путь к CSV файлу (Enter = contacts.csv): ").strip() or "contacts.csv"
            insert_from_csv(path)
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
