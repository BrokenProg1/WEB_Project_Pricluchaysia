from flask import *

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем


@app.route('/', methods=["GET"])
def main_page():
    return render_template('base.html', title='Main Page')


if __name__ == '__main__':
    db_session.global_init("db/databaseFile.db")
    app.run(debug=True)