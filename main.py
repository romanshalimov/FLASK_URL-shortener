import sqlite3
import datetime
import random
import hashlib

host = 'http://localhost:5000/'

def md5_encoder(url):
    """
    Сгенерируем укороченную ссылку (кодировка md5 экономит место в базе данных)
    """
    # сгененрируем хэш-код на основе введённой ссылки
    hash_code = hashlib.md5(url.encode())

    # выбор последних 6 цифр хэш-кода
    # 1,073,741,824 вариантов
    target_url = hash_code.hexdigest()[-6:]

    return target_url


def random_string(length: int = 6):
    """
    Сгенерируем случайную буквенно-цифровую строку
    """
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # выберем случайную строку из 6 цифр из base
    # 56,800,235,584 вариантов
    code = ''.join([random.choice(base) for i in range(length)])

    return code


class URL_DB(object):
    """
    Класс для управления базой данных
    """

    def __init__(self, shortcode=""):
        """
        Вставленный код является уникальным идентификатором в базе данных по умолчанию, помимо id
        """
        self.shortcode = shortcode

    def create_table(self, db_address="./urls.db"):
        """
        Создадим одноразовую таблицу
        """
        create_table = """CREATE TABLE WEB_URL(id, 
                                            URL_original, 
                                            shortcode, 
                                            create_datetime, 
                                            last_redirect,    
                                            redirect_count)"""
        # вставим запись
        first_entry = """INSERT INTO WEB_URL VALUES(
                                        1, "URL","shortcode",
                                        "create_datetime","last_redirect",0) """

        # подключимся к обновлённой базе данных
        conn = sqlite3.connect(db_address)
        cursor = conn.cursor()
        # создадим таблицу
        cursor.execute(create_table)

        cursor.execute(first_entry)
        conn.commit()
        return "NEW TABLE!!"

    def fetch_data_from_db(self, db_address="./urls.db"):
        """
        Извлечём  данные из базы с заданным коротким кодом.
        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()

        data = [str(self.shortcode)]

        res = cur.execute("SELECT * FROM WEB_URL WHERE shortcode=?", data)
        val = res.fetchall()
        return val

    def add_data_to_db(self, url, db_address="./urls.db"):
        """
        Добавим данные в базу.
        """
        # подключимся к базе
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()

        # прочитаем список id
        res = cur.execute("SELECT * FROM WEB_URL")

        # добавим единицу к длине получившейся базы данных
        index = len(res.fetchall()) + 1

        creation_datetime = datetime.datetime.utcnow().isoformat()
        last_redirect = ""
        redirect_count = 0

        # введём данные
        data = [(index, str(url), str(self.shortcode), creation_datetime,
                 last_redirect, redirect_count)]

        cur.executemany("INSERT INTO WEB_URL VALUES(?, ?, ?, ?, ?, ?)", data)
        conn.commit()
        return "New entry added"

    def delete_data_from_db(self, db_address="./urls.db"):
        """
        Удаление всех записей с коротким кодом
        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()

        cur.execute("DELETE FROM WEB_URL WHERE shortcode=?",
                    [str(self.shortcode)])
        conn.commit()

        return "Deleted!"

    def update_redirect_record(self, db_address="./urls.db"):
        """
        Обновим запись перенаправления в базе данных.
        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()

        old_fetch_count = cur.execute("SELECT redirect_count FROM WEB_URL \
                                      WHERE shortcode=?",
                                      [str(self.shortcode)]).fetchall()

        # время выполнения
        fetch_time = datetime.datetime.utcnow().isoformat()
        fetch_count = old_fetch_count[0][0] + 1

        # обновление данных
        data = [fetch_time, fetch_count, self.shortcode]

        statement = """UPDATE WEB_URL 
                          SET last_redirect="{}" , 
                              redirect_count ={} 
                          WHERE shortcode ="{}"
                          """.format(str(data[0]), str(data[1]), data[2])

        cur.execute(statement)
        conn.commit()

        return "Updated!"