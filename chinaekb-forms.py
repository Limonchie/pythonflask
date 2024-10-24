import requests
from flask import Flask, render_template, request, redirect, url_for, current_app, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import flask
import json
import datetime
import os
import shutil

from werkzeug.utils import secure_filename

import db
import logging
from datetime import timedelta
from math import ceil
from flask import jsonify, request

VERSION = "0"
BASE_URL = os.environ["BASE_URL"] if "BASE_URL" in os.environ else ""
DOCS_PATH = os.environ["DOCS_PATH"] if "DOCS_PATH" in os.environ else "docs"
DOCS_PATH = DOCS_PATH[:-1] if DOCS_PATH[-1] == "/" else DOCS_PATH
CONTRACTS_PATH = os.environ["CONTRACTS_PATH"] if "CONTRACTS_PATH" in os.environ else "contracts_templates"
LOG_LEVEL = os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "DEBUG"
DOCS_TTL = int(os.environ["DOCS_TTL"]) if "DOCS_TTL" in os.environ else 3600

app = flask.Flask("chinaekb_form")
app.logger.setLevel(LOG_LEVEL)
app.secret_key = 'secret_123'

app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

pdfoptions = {}

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Класс пользователя
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.path.exists('chinaekb.db'):
    db.init_db()

if CONTRACTS_PATH != "contracts_templates":
    files = os.listdir("contracts_templates")
    for i in files:
        if not os.path.exists(CONTRACTS_PATH + "/" + i):
            shutil.copy2("contracts_templates/" + i, CONTRACTS_PATH + "/" + i)

def select_exam(examselection):
    if examselection == "1":
        examprise = 2000
        examlevel = 1
        examtype = "HSK"
    elif examselection == "2":
        examprise = 2000
        examlevel = 2
        examtype = "HSK"
    elif examselection == "3":
        examprise = 3000
        examlevel = 3
        examtype = "HSK"
    elif examselection == "4":
        examprise = 3000
        examlevel = 4
        examtype = "HSK"
    elif examselection == "5":
        examprise = 4000
        examlevel = 5
        examtype = "HSK"
    elif examselection == "6":
        examprise = 4000
        examlevel = 6
        examtype = "HSK"
    elif examselection == "7":
        examprise = 2000
        examlevel = "базовый"
        examtype = "HSKK"
    elif examselection == "8":
        examprise = 3000
        examlevel = "средний"
        examtype = "HSKK"
    elif examselection == "9":
        examprise = 4000
        examlevel = "высокий"
        examtype = "HSKK"
    elif examselection == "10":
        examprise = 2000
        examlevel = "A"
        examtype = "BCT"
    elif examselection == "11":
        examprise = 3000
        examlevel = "B"
        examtype = "BCT"
    elif examselection == "12":
        examprise = 1000
        examlevel = 1
        examtype = "YCT"
    elif examselection == "13":
        examprise = 1000
        examlevel = 2
        examtype = "YCT"
    elif examselection == "14":
        examprise = 1500
        examlevel = 3
        examtype = "YCT"
    elif examselection == "15":
        examprise = 1500
        examlevel = 4
        examtype = "YCT"
    else:
        examprise = 0
        examlevel = 0
        examtype = "_____________"

    return examprise, examlevel, examtype

def clear_docs() -> None:
    if DOCS_TTL == 0:
        return
    files = os.listdir(DOCS_PATH)
    for i in files:
        if datetime.datetime.now().timestamp() - os.path.getmtime(DOCS_PATH + "/" + i) > DOCS_TTL:
            os.remove(DOCS_PATH + "/" + i)

# Healthcheck uri
@app.route(BASE_URL + "/status")
def status():
    resp = {"success":True, "version":VERSION, "status":"ok"}
    return flask.Response(json.dumps(resp), 200, mimetype="application/json")

@app.errorhandler(500)
def error(error):
    if flask.request.method == "POST":
        return flask.Response(json.dumps({"success":False, "message":"Unknown server error"}), 500, mimetype="application/json")
    else:
        return flask.render_template("500.html", base_url=BASE_URL), 500

@app.errorhandler(404)
def not_found(error):
    if flask.request.method == "POST":
        return flask.Response(json.dumps({"success":False, "message":"Nothing was found"}), 404, mimetype="application/json")
    else:
        return flask.render_template("404.html", base_url=BASE_URL), 404

@app.errorhandler(405)
def not_allowed(error):
    return flask.Response(json.dumps({"success":False, "message":"Method not allowed"}), 405, mimetype="application/json")

@app.route("/favicon.ico")
def favicon():
    return flask.send_file("static/favicon.ico")

@app.route(BASE_URL + "/static/<path:path>")
def getstatic(path):
    return flask.send_from_directory("static", path)

@app.route(BASE_URL + "/docs/<path:path>")
def getdocs(path):
    clear_docs()
    return flask.send_from_directory(DOCS_PATH, path)

@app.route(BASE_URL + "/")
def index():
    return flask.redirect(BASE_URL + "/forms")

@app.route(BASE_URL + "/forms")
def forms():
    return flask.render_template("forms.html", base_url=BASE_URL)

@app.route(BASE_URL + "/education_adult", methods=["GET", "POST"])
def education_adult():
    if flask.request.method == 'GET':
        return flask.render_template("education_adult.html", base_url=BASE_URL, formtitle="Образование для взрослых")
    elif flask.request.method == 'POST':
        # Обработка данных формы
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        study_plan = "Практический курс китайского языка для взрослых"
        exam_selection = flask.request.form.get('examselection')
        exam_date = flask.request.form.get('examdate')
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO adult_students (last_name, first_name, middle_name, birth_date, address, gender, snils, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, submission_date, file_paths)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender, studentsnils, "passport", studentid_serial, studentid_number, studentid_by, studentid_issued, studentbank, studentphone, studentemail, study_plan, exam_selection, exam_date, submission_date, ','.join(file_paths)))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

@app.route(BASE_URL + "/exam_adult", methods=["GET", "POST"])
def exam_adult():
    if flask.request.method == 'GET':
        return flask.render_template("exam_adult.html", base_url=BASE_URL)
    elif flask.request.method == 'POST':
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        examselection = flask.request.form.get("examselection")
        examdate = flask.request.form.get("examdate")
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO adult_students (last_name, first_name, middle_name, birth_date, address, gender, snils, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender, studentsnils, "passport", studentid_serial, studentid_number, studentid_by, studentid_issued, studentbank, studentphone, studentemail, "Экзамен для взрослых", examselection, examdate, submission_date))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

@app.route(BASE_URL + "/education_children_under14", methods=["GET", "POST"])
def education_children_under14():
    if flask.request.method == 'GET':
        return flask.render_template("education_children_under14.html", base_url=BASE_URL, formtitle="Образование для несовершеннолетних (до 14 лет)")
    elif flask.request.method == 'POST':
        # Обработка данных формы
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        id_type = "birth certificate"
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        study_plan = "Практический базовый курс китайского языка для детей"
        exam_selection = flask.request.form.get('examselection')
        exam_date = flask.request.form.get('examdate')
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        clientname_lastname = flask.request.form.get('clientname-lastname').strip().lower().capitalize()
        clientname_name = flask.request.form.get('clientname-name').strip().lower().capitalize()
        clientname_surname = flask.request.form.get('clientname-surname').strip().lower().capitalize()
        clientbirth = str(flask.request.form.get('clientbirth'))
        clientaddress = flask.request.form.get('clientaddress')
        clientgender = flask.request.form.get('clientgender')
        clientsnils = flask.request.form.get('clientsnils')
        clientid_serial = flask.request.form.get('clientid-serial')
        clientid_number = flask.request.form.get('clientid-number')
        clientid_by = flask.request.form.get('clientid-by')
        clientid_issued = str(flask.request.form.get('clientid-issued'))
        clientbank = flask.request.form.get('clientbank')
        clientphone = flask.request.form.get('clientphone')
        clientemail = flask.request.form.get('clientemail')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO students (last_name, first_name, middle_name, birth_date, address, gender, snils, age_group, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, status, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender,
            studentsnils, "under14", id_type, studentid_serial, studentid_number, studentid_by, studentid_issued,
            studentbank, studentphone, studentemail, study_plan, exam_selection, exam_date, "на проверке", submission_date
        ))

        student_id = c.lastrowid

        c.execute('''
            INSERT INTO representatives (student_id, last_name, first_name, middle_name, birth_date, address, gender, snils, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, clientname_lastname, clientname_name, clientname_surname, clientbirth, clientaddress, clientgender,
            clientsnils, clientid_serial, clientid_number, clientid_by, clientid_issued, clientbank, clientphone,
            clientemail
        ))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

@app.route(BASE_URL + "/education_children_over14", methods=["GET", "POST"])
def education_children_over14():
    if flask.request.method == 'GET':
        return flask.render_template("education_children_over14.html", base_url=BASE_URL, formtitle="Образование для несовершеннолетних (от 14 до 18 лет)")
    elif flask.request.method == 'POST':
        # Обработка данных формы
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        id_type = "passport"
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        study_plan = "Практический базовый курс китайского языка для детей"
        exam_selection = flask.request.form.get('examselection')
        exam_date = flask.request.form.get('examdate')
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        clientname_lastname = flask.request.form.get('clientname-lastname').strip().lower().capitalize()
        clientname_name = flask.request.form.get('clientname-name').strip().lower().capitalize()
        clientname_surname = flask.request.form.get('clientname-surname').strip().lower().capitalize()
        clientbirth = str(flask.request.form.get('clientbirth'))
        clientaddress = flask.request.form.get('clientaddress')
        clientgender = flask.request.form.get('clientgender')
        clientsnils = flask.request.form.get('clientsnils')
        clientid_serial = flask.request.form.get('clientid-serial')
        clientid_number = flask.request.form.get('clientid-number')
        clientid_by = flask.request.form.get('clientid-by')
        clientid_issued = str(flask.request.form.get('clientid-issued'))
        clientbank = flask.request.form.get('clientbank')
        clientphone = flask.request.form.get('clientphone')
        clientemail = flask.request.form.get('clientemail')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO students (last_name, first_name, middle_name, birth_date, address, gender, snils, age_group, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, status, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender,
            studentsnils, "over14", id_type, studentid_serial, studentid_number, studentid_by, studentid_issued,
            studentbank, studentphone, studentemail, study_plan, exam_selection, exam_date, "на проверке", submission_date))

        student_id = c.lastrowid

        c.execute('''
            INSERT INTO representatives (student_id, last_name, first_name, middle_name, birth_date, address, gender, snils, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, clientname_lastname, clientname_name, clientname_surname, clientbirth, clientaddress, clientgender,
            clientsnils, clientid_serial, clientid_number, clientid_by, clientid_issued, clientbank, clientphone,
            clientemail))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

@app.route(BASE_URL + "/exam_children_under14", methods=["GET", "POST"])
def exam_children_under14():
    if flask.request.method == 'GET':
        return flask.render_template("exam_children_under14.html", base_url=BASE_URL, formtitle="Экзамен для несовершеннолетних(до 14 лет)")
    elif flask.request.method == 'POST':
        # Обработка данных формы
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        id_type = "birth certificate"
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        study_plan = "Экзамен для детей (до 14 лет)"
        exam_selection = flask.request.form.get('examselection')
        exam_date = flask.request.form.get('examdate')
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        clientname_lastname = flask.request.form.get('clientname-lastname').strip().lower().capitalize()
        clientname_name = flask.request.form.get('clientname-name').strip().lower().capitalize()
        clientname_surname = flask.request.form.get('clientname-surname').strip().lower().capitalize()
        clientbirth = str(flask.request.form.get('clientbirth'))
        clientaddress = flask.request.form.get('clientaddress')
        clientgender = flask.request.form.get('clientgender')
        clientsnils = flask.request.form.get('clientsnils')
        clientid_serial = flask.request.form.get('clientid-serial')
        clientid_number = flask.request.form.get('clientid-number')
        clientid_by = flask.request.form.get('clientid-by')
        clientid_issued = str(flask.request.form.get('clientid-issued'))
        clientbank = flask.request.form.get('clientbank')
        clientphone = flask.request.form.get('clientphone')
        clientemail = flask.request.form.get('clientemail')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO students (last_name, first_name, middle_name, birth_date, address, gender, snils, age_group, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, status, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender, studentsnils, "under14", id_type, studentid_serial, studentid_number, studentid_by, studentid_issued, studentbank, studentphone, studentemail, study_plan, exam_selection, exam_date, "на проверке", submission_date))

        student_id = c.lastrowid

        c.execute('''
            INSERT INTO representatives (student_id, last_name, first_name, middle_name, birth_date, address, gender, snils, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, clientname_lastname, clientname_name, clientname_surname, clientbirth, clientaddress, clientgender, clientsnils, clientid_serial, clientid_number, clientid_by, clientid_issued, clientbank, clientphone, clientemail))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

@app.route(BASE_URL + "/exam_children_over14", methods=["GET", "POST"])
def exam_children_over14():
    if flask.request.method == 'GET':
        return flask.render_template("exam_children_over14.html", base_url=BASE_URL, formtitle="Экзамен для несовершеннолетних (от 14 до 18 лет)")
    elif flask.request.method == 'POST':
        # Обработка данных формы
        studentname_lastname = flask.request.form.get('studentname-lastname').strip().lower().capitalize()
        studentname_name = flask.request.form.get('studentname-name').strip().lower().capitalize()
        studentname_surname = flask.request.form.get('studentname-surname').strip().lower().capitalize()
        studentbirth = str(flask.request.form.get('studentbirth'))
        studentaddress = flask.request.form.get('studentaddress')
        studentgender = flask.request.form.get('studentgender')
        studentsnils = flask.request.form.get('studentsnils')
        studentid_serial = flask.request.form.get('studentid-serial')
        studentid_number = flask.request.form.get('studentid-number')
        studentid_by = flask.request.form.get('studentid-by')
        studentid_issued = str(flask.request.form.get('studentid-issued'))
        id_type = "passport"
        studentbank = flask.request.form.get('studentbank')
        studentphone = flask.request.form.get('studentphone')
        studentemail = flask.request.form.get('studentemail')
        study_plan = "Экзамен для детей (от 14 до 18 лет)"
        exam_selection = flask.request.form.get('examselection')
        exam_date = flask.request.form.get('examdate')
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        clientname_lastname = flask.request.form.get('clientname-lastname').strip().lower().capitalize()
        clientname_name = flask.request.form.get('clientname-name').strip().lower().capitalize()
        clientname_surname = flask.request.form.get('clientname-surname').strip().lower().capitalize()
        clientbirth = str(flask.request.form.get('clientbirth'))
        clientaddress = flask.request.form.get('clientaddress')
        clientgender = flask.request.form.get('clientgender')
        clientsnils = flask.request.form.get('clientsnils')
        clientid_serial = flask.request.form.get('clientid-serial')
        clientid_number = flask.request.form.get('clientid-number')
        clientid_by = flask.request.form.get('clientid-by')
        clientid_issued = str(flask.request.form.get('clientid-issued'))
        clientbank = flask.request.form.get('clientbank')
        clientphone = flask.request.form.get('clientphone')
        clientemail = flask.request.form.get('clientemail')

        # Проверка наличия загруженных файлов
        studentfiles = flask.request.files.getlist('studentfiles')
        if not studentfiles:
            return "No files uploaded", 400

        # Обработка загруженных файлов
        file_paths = []
        for studentfile in studentfiles:
            if studentfile and studentfile.filename:
                filename = secure_filename(studentfile.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                studentfile.save(file_path)
                file_paths.append(filename)

        # Сохранение данных в базу данных
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO students (last_name, first_name, middle_name, birth_date, address, gender, snils, age_group, id_type, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email, study_plan, exam_selection, exam_date, status, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (studentname_lastname, studentname_name, studentname_surname, studentbirth, studentaddress, studentgender, studentsnils, "under14", id_type, studentid_serial, studentid_number, studentid_by, studentid_issued, studentbank, studentphone, studentemail, study_plan, exam_selection, exam_date, "на проверке", submission_date))

        student_id = c.lastrowid

        c.execute('''
            INSERT INTO representatives (student_id, last_name, first_name, middle_name, birth_date, address, gender, snils, id_serial, id_number, id_issued_by, id_issued_date, bank_details, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, clientname_lastname, clientname_name, clientname_surname, clientbirth, clientaddress, clientgender, clientsnils, clientid_serial, clientid_number, clientid_by, clientid_issued, clientbank, clientphone, clientemail))

        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return redirect(url_for('success'))

# Устанавливаем время жизни "запомнить меня" куки (например, 7 дней)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

@app.route(BASE_URL + "/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'  # Проверяем, отмечен ли флажок

        # Проверка логина и пароля (замените на реальную проверку)
        if username == 'moder1' and password == 'password1':
            user = User('moderator1')
            login_user(user, remember=remember)  # Передаем параметр remember
            return redirect(BASE_URL + "/moderation")
        elif username == 'moder2' and password == 'password2':
            user = User('moderator2')
            login_user(user, remember=remember)  # Передаем параметр remember
            return redirect(BASE_URL + "/moderation")
        else:
            return render_template("login.html", base_url=BASE_URL, error="Неверный логин или пароль")

    return render_template("login.html", base_url=BASE_URL)

# Маршрут для выхода
@app.route(BASE_URL + "/logout")
@login_required
def logout():
    logout_user()
    return redirect(BASE_URL + "/forms")

@app.route(BASE_URL + "/moderation", methods=["GET", "POST"])
@login_required
def moderation():
    if request.method == 'GET':
        # Получаем параметры фильтрации
        table_name = request.args.get('table_name', default='students')
        status = request.args.get('status', default='all')
        limit = int(request.args.get('limit', default='20'))
        page = int(request.args.get('page', default='1'))

        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()

        # Извлекаем данные из выбранной таблицы
        query = f'SELECT * FROM {table_name}'
        if status != 'all':
            query += f' WHERE status = ?'
            c.execute(query, (status,))
        else:
            c.execute(query)

        total_records = len(c.fetchall())
        total_pages = ceil(total_records / limit)

        offset = (page - 1) * limit
        query += f' LIMIT ? OFFSET ?'
        c.execute(query, (limit, offset) if status == 'all' else (status, limit, offset))

        if table_name == 'students':
            students = c.fetchall()
            minor_students_with_representatives = []
            adult_students = []
        elif table_name == 'adult_students':
            adult_students = c.fetchall()
            students = []
            minor_students_with_representatives = []

        conn.close()

        # Логирование данных, передаваемых в шаблон
        current_app.logger.info(f"Rendering template with table_name={table_name}, status={status}, limit={limit}, page={page}, total_pages={total_pages}")
        current_app.logger.info(f"Students: {students}")
        current_app.logger.info(f"Adult Students: {adult_students}")

        # Получаем сообщение из сессии и удаляем его
        success_message = session.pop('success_message', None)

        return render_template("moderation.html", base_url=BASE_URL, students=students, adult_students=adult_students, minor_students_with_representatives=minor_students_with_representatives, table_name=table_name, status=status, limit=limit, page=page, total_pages=total_pages, success_message=success_message)

@app.route(BASE_URL + "/moderation/<table_name>/student/<int:student_id>", methods=["GET", "POST"])
@login_required
def student_details(table_name, student_id):
    if request.method == 'GET':
        conn = sqlite3.connect('chinaekb.db')
        c = conn.cursor()
        c.execute(f'SELECT * FROM {table_name} WHERE id = ?', (student_id,))
        student = c.fetchone()
        representative = None
        if student and table_name == 'students':
            c.execute('SELECT * FROM representatives WHERE student_id = ?', (student_id,))
            representative = c.fetchone()
        conn.close()

        if student:
            return render_template("student_details.html", base_url=BASE_URL, student=student, representative=representative, table_name=table_name)
        else:
            return "Студент не найден", 404

    elif request.method == 'POST':
        action = request.form.get('action')

        # Логирование значения table_name
        logger.info(f"table_name: {table_name}")

        if action == 'approve':
            conn = sqlite3.connect('chinaekb.db')
            c = conn.cursor()

            try:
                # Обновляем статус заявки на "проверено"
                c.execute(f'UPDATE {table_name} SET status = ? WHERE id = ?', ('проверено', student_id))
                conn.commit()

                # Получаем данные заявки для отправки в 1С
                c.execute(f'SELECT * FROM {table_name} WHERE id = ?', (student_id,))
                student = c.fetchone()

                # Получаем данные ответственного, если это несовершеннолетний студент
                representative = None
                if table_name == 'students':
                    c.execute('SELECT * FROM representatives WHERE student_id = ?', (student_id,))
                    representative = c.fetchone()

                # Проверка на None
                if student is None:
                    logger.error(f"Студент с ID {student_id} не найден в таблице {table_name}")
                    return json.dumps({"success": False, "message": "Студент не найден"}), 404, {'Content-Type': 'application/json'}

                # Выводим количество столбцов и сами данные студента
                logger.info(f"Количество столбцов в данных студента с ID {student_id} в таблице {table_name}: {len(student)}")
                logger.info(f"Данные студента с ID {student_id} в таблице {table_name}: {student}")

                # Формируем JSON и отправляем данные в 1С
                if table_name == 'students':
                    student_data = {
                        'id': student[0],
                        'last_name': student[1],
                        'first_name': student[2],
                        'middle_name': student[3],
                        'birth_date': student[4],
                        'address': student[5],
                        'gender': student[6],
                        'snils': student[7],
                        'age_group': student[8],
                        'id_type': student[9],
                        'id_serial': student[10],
                        'id_number': student[11],
                        'id_issued_by': student[12],
                        'id_issued_date': student[13],
                        'bank_details': student[14],
                        'phone': student[15],
                        'email': student[16],
                        'study_plan': student[17],
                        'exam_selection': student[18],
                        'exam_date': student[19],
                        'status': student[20],
                        'submission_date': student[21],
                        'representative': {
                            'last_name': representative[2],
                            'first_name': representative[3],
                            'middle_name': representative[4],
                            'birth_date': representative[5],
                            'address': representative[6],
                            'gender': representative[7],
                            'snils': representative[8],
                            'id_serial': representative[9],
                            'id_number': representative[10],
                            'id_issued_by': representative[11],
                            'id_issued_date': representative[12],
                            'bank_details': representative[13],
                            'phone': representative[14],
                            'email': representative[15]
                        } if representative else None
                    }
                elif table_name == 'adult_students':
                    # Формируем JSON и отправляем данные в 1С
                    student_data = {
                        'id': student[0],
                        'last_name': student[1],
                        'first_name': student[2],
                        'middle_name': student[3],
                        'birth_date': student[4],
                        'address': student[5],
                        'gender': student[6],
                        'snils': student[7],
                        'id_type': student[8],
                        'id_serial': student[9],
                        'id_number': student[10],
                        'id_issued_by': student[11],
                        'id_issued_date': student[12],
                        'bank_details': student[13],
                        'phone': student[14],
                        'email': student[15],
                        'study_plan': student[16],
                        'exam_selection': student[17],
                        'exam_date': student[18],
                        'status': student[19],
                        'submission_date': student[20]
                    }

                # Сохраняем данные JSON в файл
                filename = f"student_{student_id}_{table_name}.json"
                save_json_to_file(student_data, filename)

                # Отправка данных в 1С (!!!закомментировано)
                # try:
                #     response = requests.post('https://your-1c-service.com/api/endpoint', json=student_data)
                #     response.raise_for_status()  # Проверка на ошибки HTTP
                #     logger.info(f"Заявка {student_id} одобрена и отправлена в 1С")
                #     return json.dumps({"success": True, "message": "Заявка одобрена и отправлена в 1С"}), 200, {'Content-Type': 'application/json'}
                # except requests.exceptions.RequestException as e:
                #     logger.error(f"Ошибка при отправке данных в 1С: {e}")
                #     return json.dumps({"success": False, "message": "Ошибка при отправке данных в 1С"}), 500, {'Content-Type': 'application/json'}

                # Добавляем сообщение в сессию
                session['success_message'] = "Заявка успешно отправлена в 1С"

                # Перенаправляем пользователя на страницу модерации
                return redirect(url_for('moderation'))

            except Exception as e:
                # Откат транзакции в случае ошибки
                conn.rollback()
                logger.error(f"Ошибка при обработке заявки {student_id} в таблице {table_name}: {e}")
                return json.dumps({"success": False, "message": "Ошибка при обработке заявки"}), 500, {'Content-Type': 'application/json'}

            finally:
                conn.close()

        elif action == 'reject':
            # Обновляем статус заявки на "отклонено"
            conn = sqlite3.connect('chinaekb.db')
            c = conn.cursor()
            c.execute(f'UPDATE {table_name} SET status = ? WHERE id = ?', ('отклонено', student_id))
            conn.commit()
            conn.close()

            logger.info(f"Заявка {student_id} отклонена")
            return json.dumps({"success": True, "message": "Заявка отклонена"}), 200, {'Content-Type': 'application/json'}

        return json.dumps({"success": False, "message": "Неизвестное действие"}), 400, {'Content-Type': 'application/json'}

def save_json_to_file(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные успешно сохранены в файл {filename}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в файл {filename}: {e}")

@app.route(BASE_URL + "/success")
def success():
    return flask.render_template("success.html", base_url=BASE_URL)

@app.route(BASE_URL + "/<path:file_path>", methods=['GET', 'POST'])
def get_file(file_path):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], file_path)

# Debug only
if __name__ == "__main__":
    app.run("0.0.0.0", port=3000)
