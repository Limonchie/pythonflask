import sqlite3

def init_db():
    conn = sqlite3.connect('chinaekb.db')
    c = conn.cursor()

    # Создание таблицы для хранения данных о студентах
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            birth_date TEXT NOT NULL,
            address TEXT NOT NULL,
            gender TEXT NOT NULL,
            snils TEXT,
            age_group TEXT NOT NULL,
            id_type TEXT NOT NULL,
            id_serial TEXT,
            id_number TEXT NOT NULL,
            id_issued_by TEXT,
            id_issued_date TEXT,
            bank_details TEXT,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            study_plan TEXT NOT NULL,
            exam_selection TEXT,
            exam_date TEXT,
            status TEXT NOT NULL DEFAULT 'на проверке',
            submission_date TEXT NOT NULL,
            file_paths TEXT
        )
    ''')

    # Создание таблицы для хранения данных о представителях
    c.execute('''
        CREATE TABLE IF NOT EXISTS representatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            birth_date TEXT NOT NULL,
            address TEXT NOT NULL,
            gender TEXT NOT NULL,
            snils TEXT,
            id_serial TEXT NOT NULL,
            id_number TEXT NOT NULL,
            id_issued_by TEXT NOT NULL,
            id_issued_date TEXT NOT NULL,
            bank_details TEXT,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    # Создание таблицы для хранения данных о взрослых студентах без представителей
    c.execute('''
        CREATE TABLE IF NOT EXISTS adult_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            birth_date TEXT NOT NULL,
            address TEXT NOT NULL,
            gender TEXT NOT NULL,
            snils TEXT,
            id_type TEXT NOT NULL,
            id_serial TEXT,
            id_number TEXT NOT NULL,
            id_issued_by TEXT,
            id_issued_date TEXT,
            bank_details TEXT,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            study_plan TEXT NOT NULL,
            exam_selection TEXT,
            exam_date TEXT,
            status TEXT NOT NULL DEFAULT 'на проверке',
            submission_date TEXT NOT NULL,
            file_paths TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            data BLOB NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

init_db()