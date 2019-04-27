# coding: utf-8
import sqlite3


class DatabaseManager:
    def __init__(self):
        if 'data' not in __import__('os').listdir('.'):
            __import__('os').mkdir('data')

        self.connection = sqlite3.connect("data/alisa_users.db", isolation_level=None)
        cursor = self.connection.cursor()
        cursor.execute('PRAGMA foreign_key=1')
        cursor.execute('CREATE TABLE IF NOT EXISTS users'
                       '(user_id TEXT PRIMARY KEY NOT NULL, name TEXT, last_char TEXT,'
                       'current_score INT DEFAULT 0, max_score INT DEFAULT 0)')
        cursor.execute('CREATE TABLE IF NOT EXISTS words'
                       '(user_id TEXT NOT NULL, word TEXT,'
                       'FOREIGN KEY (user_id) REFERENCES users(user_id))')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def add_user(self, user_id: str, name: str = '', last_char: str = '',
                 current_score: int = 0, max_score: int = 0) -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_entry(user_id):
                cursor.execute("""INSERT INTO users 
                                VALUES(:user_id, :name, :last_char,
                                :current_score, :max_score)""", {
                    'user_id': user_id, 'name': name, 'last_char': last_char,
                    'current_score': current_score, 'max_score': max_score
                })
                print('Пользователь {} добавлен.'.format(user_id))
            else:
                print('Пользователь {} уже существует!'.format(user_id))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def update(self, user_id: str, new_last_char: str,
               current_score: int = 0, max_score: int = 0) -> bool:
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
                return False
            else:
                print(exist_entry, ' - exist entry;;;    branch else in update')
                cursor.execute("""UPDATE users
                                SET last_char = :last_char, 
                                current_score = :current_score,
                                max_score = :max_score 
                                WHERE user_id == :user_id""",
                               {
                                   'user_id': user_id, 'last_char': new_last_char,
                                   'current_score': current_score, 'max_score': max_score
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def add_word(self, user_id: str, new_word: str) -> bool:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""INSERT INTO words 
                            VALUES(:user_id, :word)""", {
                'user_id': user_id, 'word': new_word
            })
            print('Пользователю {} добавлено слово {}.'.format(user_id, new_word))
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def get_entry(self, user_id: str = '', get_all: bool = False) -> list:
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

    def get_words(self, user_id: str) -> list:
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute("""SELECT * FROM words
                            WHERE user_id = :user_id""",
                           {
                               'user_id': user_id,
                           })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            result = cursor.fetchall()
        cursor.close()
        return [elem[1] for elem in result]

    def delete_user(self, user_id: str) -> bool:
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
                return False
            else:
                cursor.execute("""DELETE FROM words
                                WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id
                               })
                cursor.execute("""DELETE FROM users
                                WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def make_leaderboard(self, size_of_table: int = 10) -> list:
        values_list = self.get_entry(get_all=True)  # [('1', 'Dima', 'a', 2, 3), ('2', 'Mila', 'т', 1, 5)]
        result = sorted(values_list, key=lambda inner_list: inner_list[4], reverse=True)
        size_of_board = len(result) if len(result) < size_of_table else size_of_table
        return [(i+1, result[i][1], result[i][4]) for i in range(size_of_board)]
