# coding: utf-8
import sqlite3


class DatabaseManager:
    def __init__(self):
        if 'data' not in __import__('os').listdir('.'):
            __import__('os').mkdir('data')

        self.connection = sqlite3.connect("data/alisa_users.db", isolation_level=None)
        cursor = self.connection.cursor()
        cursor.execute('PRAGMA foreign_key=1')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_id TEXT NOT NULL,
                             user_name TEXT,
                             password TEXT)''')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def get_users(self, user_id: str = '', get_all: bool = False)->list:
        cursor = self.connection.cursor()
        result = []
        try:
            if get_all:
                cursor.execute("""SELECT * FROM users""")
            else:
                cursor.execute("""SELECT * FROM users
                                        WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id,
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            result = cursor.fetchall()
        cursor.close()
        return result

    def get_individ(self, user_name: str = '', password: str = '')->bool:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT * FROM users
                                                    WHERE user_name = :user_name, password = :password""",
                           {
                               'user_name': user_name, 'password': password
                           })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def add_user(self, user_id: str, user_name: str = '', password: str = '') -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_individ(user_name, password):
                cursor.execute("""INSERT INTO users 
                                VALUES(:user_id, :user_name, :password)""", {
                    'user_id': user_id, 'user_name': user_name, 'password': password})
                print('Регистрация пользователя {}{}.'.format(user_id, user_name))
            else:
                print('Произведен вход пользователя {}{}.'.format(user_id, user_name))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True
