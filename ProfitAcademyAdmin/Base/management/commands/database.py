import datetime
import pytz
import sqlite3


uzbekistan_tz = pytz.timezone('Asia/Tashkent')


def get_current_time():
    return datetime.datetime.now(uzbekistan_tz).strftime('%Y-%m-%d %H:%M:%S')


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_user_table()
        self.create_course_table()
        self.create_promocode_table()
        self.create_groups_table()
        self.create_payments_table()
        self.create_channels_table()
        self.create_admins_table()

    def create_user_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                city TEXT,
                username TEXT,
                userid INTEGER NOT NULL,
                current_time TEXT
            );
        ''')
        self.connection.commit()


    def create_course_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            photo TEXT NOT NULL,
            description TEXT NOT NULL,
            price INTEGER NOT NULL,
            duration INTEGER NOT NULL
        );
        ''')


    def create_promocode_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                discount_percentage INTEGER NOT NULL,
                limit_count INTEGER NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );
        ''')
        self.connection.commit()

    def create_groups_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                chat_id INTEGER NOT NULL
            );
        ''')
        self.connection.commit()

    def create_payments_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo TEXT NOT NULL,
                course_id TEXT NOT NULL,
                payment INTEGER NOT NULL,
                promocode_id TEXT,
                comment TEXT,
                time TEXT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (promocode_id) REFERENCES promocodes(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        self.connection.commit()


    def create_channels_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );
        ''')
        self.connection.commit()

    def create_admins_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL
            );
        ''')
        self.connection.commit()


    def update_promocode(self, promocode_id, limit_count=None):
        self.cursor.execute("UPDATE promocodes SET limit_count = ? WHERE id = ?", (limit_count, promocode_id))
        self.connection.commit()


    def get_promocodes_by_course_id(self, course_id):
        self.cursor.execute('SELECT * FROM promocodes WHERE course_id = ?', (course_id, ))
        return dict_fetchall(self.cursor)


    def get_promocode_by_id(self, promocode_id):
        self.cursor.execute('SELECT * FROM promocodes WHERE id = ?', (promocode_id, ))
        return dict_fetchone(self.cursor)


    def insert_user(self, name, phone, city, username, userid):
        current_time = get_current_time()
        try:
            if self.get_user_by_id(userid):
                print(f"User with ID {userid} already exists in the database.")
                return False

            self.cursor.execute('''
                INSERT INTO users (name, phone, city, username, userid, current_time) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, city, username, userid, current_time))
            self.connection.commit()
            print(f"User {name} inserted successfully!")

        except sqlite3.IntegrityError as e:
            print(f"Error inserting user: {e}")

    def insert_payment(self, user, course, payment, photo=None, promocode=None, comment=None):
        current_time = get_current_time()
        try:
            self.cursor.execute('''
                INSERT INTO payments (user_id, photo, course_id, payment, promocode_id, comment, time) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user, photo, course, payment, promocode, comment, current_time))
            self.connection.commit()
            print(f"User {user} inserted successfully!")

        except sqlite3.IntegrityError as e:
            print(f"Error inserting user: {e}")


    def get_user_by_id(self, userid):
        self.cursor.execute('SELECT * FROM users WHERE userid = ?', (userid,))
        return dict_fetchone(self.cursor)


    def get_channel_by_course_id(self, course_id):
        self.cursor.execute('SELECT * FROM channels WHERE course_id = ?', (course_id,))
        return dict_fetchone(self.cursor)


    def get_all_courses(self):
        self.cursor.execute('SELECT * FROM courses')
        return dict_fetchall(self.cursor)


    def get_course_by_title(self, course_title):
        self.cursor.execute('SELECT * FROM courses WHERE title = ?', (course_title,))
        return dict_fetchone(self.cursor)


    def get_course_by_id(self, course_id):
        self.cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        return dict_fetchone(self.cursor)

    def get_groups(self):
        self.cursor.execute('SELECT * FROM groups')
        return dict_fetchall(self.cursor)

    def get_admin(self):
        self.cursor.execute('SELECT * FROM admins')
        return dict_fetchone(self.cursor)
