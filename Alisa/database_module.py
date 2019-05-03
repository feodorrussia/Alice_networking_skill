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
        cursor.execute('''CREATE TABLE IF NOT EXISTS friends
                            (user_name1 VARCHAR(128),
                            user_name2 VARCHAR(128))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                            (user_name1 VARCHAR(128),
                            message VARCHAR(128),
                            user_name2 VARCHAR(128),
                            status INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions
                                    (user_id TEXT,
                                    global_status VARCHAR(50),
                                    user_name VARCHAR(50),
                                    recipient_name VARCHAR(50),
                                    status_action VARCHAR(50))''')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def get_user(self, user_name):
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
                result = [True, user]
            else:
                result = [False, True]
        cursor.close()
        print(result)
        return result

    def get_registration(self, user_name: str = '', password: str = '') -> list:
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
                if password != user[0][1]:
                    result = [True, False]
                else:
                    result = [True, user]
            else:
                result = [False, True]
        cursor.close()
        print(result)
        return result

    def add_user(self, user_name: str = '', password: str = '') -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_registration(user_name, password)[0]:
                cursor.execute('''INSERT INTO users
                          (user_name, password, status)
                          VALUES (?,?,1)''',
                               (user_name, password))
                print('Регистрация пользователя {} прошла успешно.'.format(user_name))
            elif self.get_registration(user_name, password)[1]:
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

    def update_status(self, user_name: str, status: int) -> bool:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""UPDATE users
                                SET status = ?
                                WHERE user_name = ? """, (status, user_name))
        except sqlite3.DatabaseError as error:
            print('       !!!!!!!!!!!!!!!!!Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def get_friendship(self, user_name1):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT * FROM friends WHERE user_name1 = :user_name1""",
                           {'user_name1': user_name1})
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '2')
            result = [False, True]
        else:
            friendship = cursor.fetchall()
            if len(friendship) == 1:
                result = [True, friendship]
            else:
                result = [False, True]
        cursor.close()
        print(result)
        return result

    def add_friendship(self, user_name1, user_name2):
        cursor = self.connection.cursor()
        try:
            if not self.get_friendship(user_name1)[0]:
                cursor.execute('''INSERT INTO friends
                                  (user_name1, user_name2)
                                  VALUES (?,?)''',
                               (user_name1, user_name2))
                print('Пользователь {} добавил в друзья {}.'.format(user_name1, user_name2))
            else:
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '4')
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def add_message(self, user_name1, message, user_name2):
        cursor = self.connection.cursor()
        try:
            cursor.execute('''INSERT INTO messages
                                (user_name1, message, user_name2)
                                VALUES (?,?,?,1)''',
                           (user_name1, message, user_name2))
            print('Пользователь {} написал {}.'.format(user_name1, user_name2))
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '5')
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def get_dialog(self, user_name1, user_name2):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """SELECT * FROM messages WHERE user_name1 = :user_name1 AND user_name2 = :user_name2 OR user_name1 = :user_name2 AND user_name2 = :user_name1""",
                {'user_name1': user_name1, 'user_name2': user_name2})
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '5')
            cursor.close()
            return [False, []]
        else:
            dialog = cursor.fetchall()
            cursor.close()
            return [True, dialog]

    def get_session(self, user_id='', group='*', all=False) -> list:
        cursor = self.connection.cursor()
        try:
            if all:
                cursor.execute("""SELECT user_id FROM sessions""")
                dialog = [x[0] for x in cursor.fetchall()]
            else:
                cursor.execute(
                    f"""SELECT {group} FROM sessions WHERE user_id = :user_id""",
                    {'user_id': user_id})
                dialog = cursor.fetchall()[0]
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '5')
            cursor.close()
            return [False]
        else:
            cursor.close()
            return dialog

    def add_session(self, user_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                '''INSERT INTO sessions  VALUES(:user_id, :global_status, :user_name, :recipient_name, :status_action)''',
                {'user_id': ''.join([str(x) for x in user_id]), 'global_status': "out", 'user_name': "", 'recipient_name': "", 'status_action': "login"})
        except sqlite3.DatabaseError as error:
            print('Error: ', error, '6')
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def update_status_system(self, new, user_id, group='global_status'):
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"""UPDATE sessions
                            SET {group} = ?
                            WHERE user_id = ? """, (new, user_id))
        except sqlite3.DatabaseError as error:
            print('       !!!!!!!!!!!!!!!!!Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True
