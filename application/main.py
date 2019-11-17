# coding=utf-8
from flask import Flask, request, make_response
from flask_mail import Mail, Message
from hashlib import md5
import time
import requests
from threading import Thread

from db.interface import DBInterface


app = Flask('MD5_light')
app.config.update({
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": '<your mail>',
    "MAIL_PASSWORD": '<your password>'
})
mail = Mail(app)
db_obj = DBInterface()


def email_sender(email: str, file_hash: str, url: str):
    msg = Message('File Hash from MD5_light', sender='olegsvetovidov@gmail.com', recipients=[email])
    msg.body = f"FILE HASH: {file_hash}\nURL: {url}"
    with app.app_context():
        mail.send(msg)

def worker(url: str, task_id: str, email: str):
    try:
        response = requests.get(url)
    except requests.exceptions.BaseHTTPError:
        print('Something went wrong')
    else:
        if response.status_code == 200:
            file_hash = md5(requests.get(url).content).hexdigest()
            db_obj.execute("UPDATE files SET status=%s, file_hash=%s WHERE task_id=%s", ('completed', file_hash, task_id))
            if email:  # Не очень мне нравится, что письмо отправляется здесь, но зато работает
                Thread(target=email_sender, args=(email, file_hash, url)).start()
            return
    db_obj.execute("UPDATE files SET status=%s WHERE task_id=%s", ('fail', task_id))


@app.route('/submit', methods=['POST'])
def submit():
    email, url = request.form.get('email'), request.form.get('url')
    if url:
        task_id = md5(str(time.time()).encode()).hexdigest()
        db_obj.execute("INSERT INTO files (task_id, email, url) VALUES (%s, %s, %s)", (task_id, email, url))
        Thread(target=worker, args=(url, task_id, email)).start()
        return make_response({'id': task_id}, 200)
    return make_response({'error': 'incorrect data'}, 422)


@app.route('/check', methods=['GET'])
def check():
    task_id = request.args.get('id')
    if task_id:
        task_from_db = db_obj.execute("SELECT * FROM files WHERE task_id=%s", (task_id,))
        if task_from_db:
            task_from_db = task_from_db[0]
            if task_from_db[3] in ['in_work', 'fail']:
                return make_response({'status': task_from_db[3]}, 200)
            return make_response({'md5': task_from_db[-1], 'status': task_from_db[3], 'url': task_from_db[2]}, 200)
        return make_response({'status': 'does_not_exit'}, 404)
    return make_response({'error': 'incorrect data'}, 422)


if __name__ == '__main__':
    app.run('0.0.0.0', 9000, debug=True)
