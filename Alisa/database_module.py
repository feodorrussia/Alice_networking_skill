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
                            (user_id VARCHAR(128) PRIMARY KEY ,
                             user_name VARCHAR(128),
                             password VARCHAR(128),
                             status INTEGER)''')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def get_users(self, user_id: str = '', get_all: bool = False) -> list:
        cursor = self.connection.cursor()
        result = []
        try:
            if get_all:
                cursor.execute("""SELECT * FROM users""")
            else:
                cursor.execute("""SELECT * FROM users
                                        WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '1')
        else:
            result = cursor.fetchall()
        cursor.close()
        return result

    def get_individ(self, user_id: str, user_name: str = '', password: str = '') -> list:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT * FROM users WHERE user_id = ?""", (user_id))
            user=cursor.fetchall()
            if user_name!=user[1] or password!=user[2]:
                result = [False, False]
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '2')
            result = [False, True]
        else:
            if len(cursor.fetchall())==1:
                result = [True]+[cursor.fetchall()]
            else:
                result = [False, True]
        cursor.close()
        return result

    def add_user(self, user_id: str, user_name: str = '', password: str = '') -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_individ(user_id, user_name, password)[0]:
                cursor.execute('''INSERT INTO users
                          (user_id, user_name, password, status)
                          VALUES (?,?,?,1)''',
                       (user_id, user_name, password))
                print('Регистрация пользователя {}{}.'.format(user_id, user_name))
            elif self.get_individ(user_id, user_name, password)[1]:
                print('Произведен вход пользователя {}{}.'.format(user_id, user_name))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '3')
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def uppdate_status(self, user_id: str, status: int) -> bool:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""UPDATE users
                                SET status = ?
                                WHERE user_id = ? """, (status, user_id))
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True
