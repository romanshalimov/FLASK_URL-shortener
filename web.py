from flask import Flask, render_template, redirect, request, \
    abort, jsonify, make_response
import sqlite3
import main

host = 'http://localhost:5000/'

db_address = './urls.db'

app = Flask(__name__, template_folder='template')

base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ввод URL
        url = request.form['url']

        # заменим пробелы
        shortcode = request.form['shortcode'].replace(" ", "")

        # проверка правильности ввода в формы
        validity = URL_valid(url, shortcode)

        #
        if validity == True:
            ## ведёт ли URL на "http://"
            if "http" in url[0:7]:
                pass
            else:
                url = "https://" + url  # добавляем к URL
            # else:
            #    pass

            if shortcode == "":
                # сгенерируем строку для верхнего поля
                shortcode = main.md5_encoder(url)

                # проверка наличия кода в базе
                shortcode_list = main.URL_DB(shortcode).fetch_data_from_db(db_address=db_address)

                # случай отсутствия кода
                if len(shortcode_list) == 0:
                    # добавление короткого кода в базу
                    main.URL_DB(shortcode).add_data_to_db(url, db_address=db_address)

                # случай, если короткий код уже есть в базе
                elif len(shortcode_list) > 0:
                    pass
            else:
                main.URL_DB(shortcode).add_data_to_db(url)

            # создание укороченной ссылки
            short_url = host + shortcode

            # страница статистики
            stats_page = host + shortcode + "/stats"
        else:
            pass

        # ответ по умолчанию
        response = render_template('index2.html', short_url=short_url,
                                   stats_page=stats_page)

        pack = jsonify(shortcode=shortcode)

        # вернём статус 201
        response2 = make_response(pack)
        return response
    return render_template('index2.html')


def URL_valid(url, shortcode, db_address=db_address):
    """
    Функция для проверки правильности введённого URL и короткого кода
    """
    # подключение к базе данных
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()
    res = cur.execute("SELECT shortcode FROM WEB_URL")

    shortcode_list = res.fetchall()
    # проверка ошибочности входных данных

    # возвращает страницу с ошибкой 400, если URL нет
    if url == "":
        message = "Status 400. Empty input is not acceptable."
        return abort(400, message)
        # ответ abort(make_response(jsonify(message=message)),400)

    # ответ 409
    elif (shortcode,) in shortcode_list:
        message = 'Status 409. Shortcode is already in use. Please choose another one.'
        return abort(409, message)
        # ответ abort(make_response(jsonify(message=message)),409)
    else:
        pass
    # ответ 412
    # проверка на наличие недопустимых символов
    for i in range(len(shortcode)):
        if shortcode[i] not in base:
            message = """Status 412. Illegal characters detected in the shortcode. 
                         Only 0-9,a-z, and A-Z are allowed."""
            return abort(412, message)
            # ответ abort(make_response(jsonify(message=message)),412)
    # else:
    #     pass
    return True


@app.route('/<shortcode>', methods=['GET'])
def redirect_URL(shortcode, db_address=db_address):
    """
    Перенаправление по новой ссылке.
    Функция выполняет поиск в базе данных, чтобы получить исходный URL,
    используя заданный короткий код. Он перенаправляет веб-страницу на этот URL.
    """
    # соединение с базой данных
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()

    res = cur.execute("SELECT shortcode FROM WEB_URL")

    # сохранение списка коротких кодов
    bag = res.fetchall()

    # проверка наличия короткого кода
    if (shortcode,) in bag:
        # извлечение и перенаправление длинного URL
        res = cur.execute("SELECT URL_original FROM WEB_URL WHERE shortcode=?",
                          (shortcode,))
        url = res.fetchall()[0][0]

        # обновление статистики
        main.URL_DB(shortcode).update_redirect_record()

        response = make_response(redirect(url, code=302))

        return response

    else:
        return abort(404)


@app.route('/<shortcode>/stats', methods=['GET'])
def check_shortcode_stats(shortcode, db_address=db_address):
    """
    Для просмотра статистики по данному короткому коду

    Аналитические сведения:
    { "{ "created": дата и время создания записи,
     ""last Redirect": дата и время последнего перенаправления,
    ""redirectCount": количество раз, когда использовалась эта сокращенная ссылка."}
    """

    # подключимся к базе данных
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()

    res = cur.execute("SELECT shortcode FROM WEB_URL")

    # сохраним список коротких кодов
    bag = res.fetchall()

    if (shortcode,) not in bag:
        return abort(404, "Shortcode not found in the database.")
    else:
        # извлечение введённых данных и заданного короткого кода
        val = main.URL_DB(shortcode).fetch_data_from_db()

        # создание файла Json
        pack = jsonify(created=val[0][-3],
                       lastRedirect=val[0][-2],
                       redirectCount=val[0][-1])
        response = make_response(pack)
        return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)