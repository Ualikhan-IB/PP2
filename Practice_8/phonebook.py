import os
from connect import get_connection


def load_sql_functions():
    base = os.path.dirname(os.path.abspath(__file__))
    with get_connection() as conn:
        with conn.cursor() as cur:
            for filename in ("functions.sql", "procedures.sql"):
                path = os.path.join(base, filename)
                with open(path, encoding="utf-8") as f:
                    cur.execute(f.read())
    print("SQL функции и процедуры загружены.")


def search_contacts():
    pattern = input("Введите паттерн поиска (имя или часть телефона): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5} {'Имя':<20} {'Телефон'}")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]}")
    else:
        print("Контакты не найдены.")


def upsert_contact():
    name = input("Имя: ").strip()
    phone = input("Телефон: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
    print(f"Контакт '{name}' добавлен или обновлён.")


def insert_many():
    print("Введите контакты (имя и телефон через запятую), пустая строка = конец:")
    names = []
    phones = []
    while True:
        line = input("  имя,телефон: ").strip()
        if not line:
            break
        parts = line.split(",", 1)
        if len(parts) != 2:
            print("  Неверный формат, пропускаю.")
            continue
        names.append(parts[0].strip())
        phones.append(parts[1].strip())

    if not names:
        print("Нет данных для вставки.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_many_contacts(%s, %s);", (names, phones))
            # Получаем некорректные записи
            cur.execute("SELECT first_name, phone, reason FROM invalid_contacts;")
            invalid = cur.fetchall()

    print(f"Вставка завершена. Добавлено: {len(names) - len(invalid)}")
    if invalid:
        print("\nНекорректные записи (не добавлены):")
        print(f"{'Имя':<20} {'Телефон':<20} {'Причина'}")
        print("-" * 60)
        for row in invalid:
            print(f"{row[0]:<20} {row[1]:<20} {row[2]}")


def paginated_query():
    try:
        limit = int(input("Записей на страницу: ").strip())
        page = int(input("Номер страницы (с 1): ").strip())
    except ValueError:
        print("Введите числа.")
        return
    offset = (page - 1) * limit
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
            rows = cur.fetchall()
    if rows:
        print(f"\nСтраница {page} (по {limit} записей):")
        print(f"{'ID':<5} {'Имя':<20} {'Телефон'}")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]}")
    else:
        print("Записей нет на этой странице.")


def delete_contact():
    print("Удалить по:")
    print("1 - Имени  2 - Телефону")
    choice = input("Выбор: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Имя: ").strip()
                cur.execute("CALL delete_contact(p_name => %s);", (name,))
            elif choice == "2":
                phone = input("Телефон: ").strip()
                cur.execute("CALL delete_contact(p_phone => %s);", (phone,))
            else:
                print("Неверный выбор.")
                return
    print("Контакт удалён.")


def main():
    load_sql_functions()

    while True:
        print("\n=== PhoneBook — Practice 8 ===")
        print("1 - Поиск по паттерну")
        print("2 - Добавить / обновить контакт (upsert)")
        print("3 - Массовая вставка с валидацией")
        print("4 - Просмотр с пагинацией")
        print("5 - Удалить контакт")
        print("0 - Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            search_contacts()
        elif choice == "2":
            upsert_contact()
        elif choice == "3":
            insert_many()
        elif choice == "4":
            paginated_query()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
