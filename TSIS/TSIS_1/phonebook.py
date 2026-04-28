# phonebook.py
# TSIS 1: Extended PhoneBook Application
# This module contains the main application logic.

import csv
import json
import os
from datetime import datetime
from connect import get_connection

# =========================================================================
# Database Initialization Helpers
# =========================================================================
def _run_sql_file(conn, filepath):
    """Executes an SQL script file on the given connection."""
    if not os.path.exists(filepath):
        print(f"  [!] File not found: {filepath}")
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()
        print(f"  [✓] Successfully executed: {os.path.basename(filepath)}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [✗] Error executing {os.path.basename(filepath)}: {e}")
        return False

def init_db(conn):
    """Initializes the database by creating tables and procedures."""
    print("\n--- Initializing Database ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not _run_sql_file(conn, os.path.join(script_dir, "schema.sql")):
        return False
    if not _run_sql_file(conn, os.path.join(script_dir, "procedures.sql")):
        return False
    print("--- Database Initialization Complete ---\n")
    return True

# =========================================================================
# Import / Export Functionality
# =========================================================================
def import_from_csv(conn, filepath="contacts.csv"):
    """Imports contacts from a CSV file, handling all new fields."""
    if not os.path.exists(filepath):
        print(f"  [!] File not found: {filepath}")
        return

    added = 0
    updated = 0
    errors = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip() or None
                    phone = row.get('phone', '').strip()
                    if not first_name or not phone:
                        errors += 1
                        continue

                    email = row.get('email', '').strip() or None
                    birthday_str = row.get('birthday', '').strip()
                    birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date() if birthday_str else None
                    group_name = row.get('group', '').strip() or None
                    phone_type = row.get('phone_type', 'mobile').strip().lower()
                    if phone_type not in ('home', 'work', 'mobile'):
                        phone_type = 'mobile'

                    # Get or create group
                    group_id = None
                    if group_name:
                        with conn.cursor() as cur:
                            cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
                            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                            group_row = cur.fetchone()
                            group_id = group_row[0] if group_row else None

                    # Check if contact already exists
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT id FROM contacts 
                            WHERE first_name = %s AND (last_name IS NOT DISTINCT FROM %s)
                        """, (first_name, last_name))
                        existing = cur.fetchone()

                        if existing:
                            # Update existing contact
                            cur.execute("""
                                UPDATE contacts 
                                SET email = %s, birthday = %s, group_id = %s, updated_at = CURRENT_TIMESTAMP
                                WHERE id = %s
                            """, (email, birthday, group_id, existing[0]))
                            contact_id = existing[0]
                            updated += 1
                        else:
                            # Insert new contact
                            cur.execute("""
                                INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING id
                            """, (first_name, last_name, email, birthday, group_id))
                            contact_id = cur.fetchone()[0]
                            added += 1

                        # Add phone (skip if duplicate)
                        cur.execute("""
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (contact_id, phone) DO NOTHING
                        """, (contact_id, phone, phone_type))

                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"  [!] Error processing row: {row}. Error: {e}")
                    errors += 1
    except Exception as e:
        print(f"  [!] Failed to read CSV file: {e}")
        return
    print(f"  [+] CSV Import finished. Added: {added}, Updated: {updated}, Errors: {errors}")
def export_to_json(conn, filepath="contacts.json"):
    """Exports all contacts (with phones and groups) to a JSON file."""
    query = """
        SELECT
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.birthday,
            g.name as group_name,
            json_agg(json_build_object('phone', p.phone, 'type', p.type)) as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        ORDER BY c.first_name, c.last_name;
    """
    data = []
    with conn.cursor() as cur:
        cur.execute(query)
        for row in cur.fetchall():
            contact = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "birthday": row[4].isoformat() if row[4] else None,
                "group": row[5],
                "phones": row[6] if row[6] else []
            }
            data.append(contact)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [+] Exported {len(data)} contacts to {filepath}")

def import_from_json(conn, filepath="contacts.json"):
    """Imports contacts from a JSON file with duplicate handling."""
    if not os.path.exists(filepath):
        print(f"  [!] File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        contacts_data = json.load(f)

    added = 0
    skipped = 0
    for contact in contacts_data:
        first_name = contact.get('first_name')
        last_name = contact.get('last_name')
        if not first_name:
            skipped += 1
            continue

        # Check for duplicate by first and last name
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE first_name = %s AND last_name IS NOT DISTINCT FROM %s", (first_name, last_name))
            existing = cur.fetchone()

        if existing:
            choice = input(f"  Contact '{first_name} {last_name or ''}' already exists. Overwrite? (y/n): ").lower()
            if choice != 'y':
                skipped += 1
                continue
            # If overwriting, we delete the old contact and all its phones (CASCADE will handle phones)
            with conn.cursor() as cur:
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                conn.commit()

        # Prepare group
        group_id = None
        group_name = contact.get('group')
        if group_name:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                grp_row = cur.fetchone()
                group_id = grp_row[0] if grp_row else None

        # Insert contact and phones
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (
                    first_name,
                    contact.get('last_name'),
                    contact.get('email'),
                    contact.get('birthday'),
                    group_id
                ))
                contact_id = cur.fetchone()[0]

                for phone in contact.get('phones', []):
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
                    """, (contact_id, phone.get('phone'), phone.get('type', 'mobile')))
            conn.commit()
            added += 1
        except Exception as e:
            conn.rollback()
            print(f"  [!] Failed to insert {first_name}: {e}")

    print(f"  [+] JSON Import finished. Added: {added}, Skipped: {skipped}")

# =========================================================================
# Console UI and Search Features
# =========================================================================
def _print_contacts(contacts):
    """Helper function to pretty-print a list of contact tuples."""
    if not contacts:
        print("  No contacts found.")
        return
    print("\n" + "-" * 120)
    print(f"{'ID':<4} {'Name':<25} {'Email':<30} {'Birthday':<12} {'Group':<15} {'Phones'}")
    print("-" * 120)
    for contact in contacts:
        print(f"{contact[0]:<4} {contact[1]:<25} {str(contact[2]):<30} {str(contact[3]):<12} {str(contact[4]):<15} {contact[5]}")
    print("-" * 120)

def filter_by_group(conn):
    """Console: Filter and show contacts by group."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()
    if not groups:
        print("  No groups found.")
        return
    print("\n  Available groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    try:
        choice = int(input("  Enter group ID: "))
    except ValueError:
        print("  Invalid input.")
        return

    query = """
        SELECT c.id, CONCAT(c.first_name, ' ', COALESCE(c.last_name, '')) as name,
               c.email, c.birthday, g.name as group_name,
               STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.group_id = %s
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        ORDER BY name;
    """
    with conn.cursor() as cur:
        cur.execute(query, (choice,))
        _print_contacts(cur.fetchall())

def search_by_email(conn):
    """Console: Search contacts by email pattern."""
    pattern = input("  Enter email pattern to search: ")
    if not pattern:
        return
    query = """
        SELECT c.id, CONCAT(c.first_name, ' ', COALESCE(c.last_name, '')) as name,
               c.email, c.birthday, g.name as group_name,
               STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.email ILIKE %s
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        ORDER BY name;
    """
    with conn.cursor() as cur:
        cur.execute(query, (f"%{pattern}%",))
        _print_contacts(cur.fetchall())

def sort_and_show_all(conn):
    """Console: Show all contacts sorted by a chosen field."""
    print("  Sort by:")
    print("    1. Name")
    print("    2. Birthday")
    print("    3. Date added")
    choice = input("  Choose: ")
    sort_map = {'1': 'c.first_name, c.last_name', '2': 'c.birthday NULLS LAST', '3': 'c.created_at'}
    order_by = sort_map.get(choice, 'c.first_name, c.last_name')

    query = f"""
        SELECT c.id, CONCAT(c.first_name, ' ', COALESCE(c.last_name, '')) as name,
               c.email, c.birthday, g.name as group_name,
               STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order_by};
    """
    with conn.cursor() as cur:
        cur.execute(query)
        _print_contacts(cur.fetchall())

def paginated_browse(conn):
    """Console: Browse contacts page by page using the pagination function from Practice 8."""
    limit = 5
    page = 0
    while True:
        offset = page * limit
        # Using the paginated_contacts function from Practice 8
        query = "SELECT * FROM paginated_contacts(%s, %s);"
        with conn.cursor() as cur:
            cur.execute(query, (limit, offset))
            contacts = cur.fetchall()
        if not contacts:
            print("  No more contacts.")
            break
        print(f"\n--- Page {page + 1} ---")
        _print_contacts(contacts)
        cmd = input("  [n]ext, [p]rev, [q]uit: ").lower()
        if cmd == 'n':
            page += 1
        elif cmd == 'p' and page > 0:
            page -= 1
        elif cmd == 'q':
            break

def full_search(conn):
    """Console: Use the search_contacts DB function for a global search."""
    term = input("  Enter search term (name, email, phone): ")
    if not term:
        return
    query = "SELECT * FROM search_contacts(%s);"
    with conn.cursor() as cur:
        cur.execute(query, (term,))
        results = cur.fetchall()
    _print_contacts(results)

def add_phone_ui(conn):
    """UI for adding a phone to an existing contact via the stored procedure."""
    name = input("  Contact name: ")
    phone = input("  Phone number: ")
    ptype = input("  Type (home/work/mobile) [mobile]: ").strip().lower() or 'mobile'
    try:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print(f"  [+] Phone {phone} added to {name}.")
    except Exception as e:
        conn.rollback()
        print(f"  [✗] Failed to add phone: {e}")

def move_to_group_ui(conn):
    """UI for moving a contact to a group via the stored procedure."""
    name = input("  Contact name: ")
    group = input("  Group name: ")
    try:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"  [+] Contact {name} moved to group {group}.")
    except Exception as e:
        conn.rollback()
        print(f"  [✗] Failed to move contact: {e}")

# =========================================================================
# Main Menu and Application Entry Point
# =========================================================================
def main_menu(conn):
    """Displays the main menu and handles user input."""
    while True:
        print("\n" + "="*50)
        print("      TSIS 1: PHONEBOOK APPLICATION")
        print("="*50)
        print(" 1. Filter contacts by group")
        print(" 2. Search contacts by email")
        print(" 3. Show all contacts (sorted)")
        print(" 4. Browse contacts (paginated)")
        print(" 5. Full-text search (name, email, phone)")
        print(" 6. Add phone to existing contact (PROCEDURE)")
        print(" 7. Move contact to group (PROCEDURE)")
        print(" 8. Import from CSV")
        print(" 9. Import from JSON")
        print("10. Export to JSON")
        print(" 0. Exit")
        print("="*50)

        choice = input("  Enter your choice: ")

        if choice == '1':
            filter_by_group(conn)
        elif choice == '2':
            search_by_email(conn)
        elif choice == '3':
            sort_and_show_all(conn)
        elif choice == '4':
            paginated_browse(conn)
        elif choice == '5':
            full_search(conn)
        elif choice == '6':
            add_phone_ui(conn)
        elif choice == '7':
            move_to_group_ui(conn)
        elif choice == '8':
            path = input("  Path to CSV file [contacts.csv]: ").strip() or "contacts.csv"
            import_from_csv(conn, path)
        elif choice == '9':
            path = input("  Path to JSON file [contacts.json]: ").strip() or "contacts.json"
            import_from_json(conn, path)
        elif choice == '10':
            path = input("  Output JSON file path [export.json]: ").strip() or "export.json"
            export_to_json(conn, path)
        elif choice == '0':
            print("  Exiting application. Goodbye!")
            break
        else:
            print("  [!] Invalid choice. Please try again.")
        input("\n  Press Enter to continue...")

if __name__ == "__main__":
    conn = get_connection()
    if conn is None:
        exit(1)

    # Initialize the database schema and procedures
    if not init_db(conn):
        print("  [✗] Database initialization failed. Exiting.")
        conn.close()
        exit(1)

    # Auto-import contacts.csv if it exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auto_csv_path = os.path.join(script_dir, "contacts.csv")
    if os.path.exists(auto_csv_path):
        print("\n--- Auto-importing contacts.csv ---")
        import_from_csv(conn, auto_csv_path)

    # Start the main menu
    main_menu(conn)
    conn.close()