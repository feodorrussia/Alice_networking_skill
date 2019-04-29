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
                            (user_name VARCHAR(128) PRIMARY KEY,
                             password VARCHAR(128),
                             status INTEGER)''')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def get_individ(self, user_name: str = '', password: str = '') -> list:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT * FROM users WHERE user_name = :user_name""",
                           {'user_name': user_name})
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '2')
            result = [False, True]
        else:
            user = cursor.fetchall()
            print(user)
            if len(user) == 1:
                if password != user[0][2]:
                    result = [True, False]
                else:
                    result = [True, user]
            else:
                result = [False, True]
        cursor.close()
        print(result)
        return result

    def add_user(self, user_id: str, user_name: str = '', password: str = '') -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_individ(user_name, password)[0]:
                cursor.execute('''INSERT INTO users
                          (user_id, user_name, password, status)
                          VALUES (?,?,?,1)''',
                               (user_id, user_name, password))
                print('Регистрация пользователя {}.'.format(user_name))
            elif self.get_individ(user_name, password)[1]:
                print('Произведен вход пользователя {}.'.format(user_name))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '3')
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def update_status(self, user_id: str, status: int) -> bool:
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
