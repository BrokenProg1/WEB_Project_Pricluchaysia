from flask import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем


@app.route('/', methods=[])
def main_page():
    return render_template('base.html', title='Main Page')


if __name__ == '__main__':
    app.run(debug=True)