from flask import Flask, render_template, redirect, url_for, request, abort
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.music import Music
from data import db_session
from data.users import User
from data.news import News
from data.photo import Photo
from forms.userform import RegisterForm
from forms.loginform import LoginForm
from forms.newsform import NewsForm
from forms.artform import ImageForm
from forms.musicform import MusicForm


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'
UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def main():
    db_session.global_init("db/test.db")
    app.run(debug=True)


# логинимся или проверяем сто пользователь залогинен
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


# добавляем пользоваткля в бд
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# выходим из профиля
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# проверяем пользователся и добавляем данные из форм
@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


# изменем новости которые пишет пользователь
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


# отображаем новости с проверкой на приватность
@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


# Регистация + ништяки
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Функция для получения всех фотографий из базы данных
def get_all_photos():
    db_sess = db_session.create_session()
    return db_sess.query(Photo).all()


# Страница с галереей фотографий
@app.route('/gallery')
def gallery():
    photos = get_all_photos()  # Получаем все фотографии из базы данных
    return render_template('gallery.html', photos=photos)  # Передаем фотографии в шаблон


# Загрузка фото
@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    form = ImageForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        photo = Photo()
        file = form.photo.data
        filename_show = form.filename.data
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/files', filename))  # Предположим, что папка 'uploads' существует
        photo.filename_show = filename_show
        photo.filename = filename
        photo.user = current_user
        current_user.photos.append(photo)
        db_sess.merge(current_user)
        db_sess.commit()
        # После успешной загрузки, перенаправляем пользователя на страницу с галереей фотографий
        return redirect(url_for('gallery'))
    return render_template('arts.html', form=form)


@app.route('/music')
def music():
    musics = db_session.create_session().query(Music).all()
    return render_template('music.html', musics=musics)


@app.route('/music_upload', methods=['GET', 'POST'])
@login_required
def music_upload():
    form = MusicForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        music = Music()
        file = form.music_file.data
        filename = form.filename.data
        print(file.filename)
        print(secure_filename(file.filename))
        filepath = secure_filename(file.filename)
        file.save(os.path.join('static/files', filepath))
        music.filename = filename
        music.filepath = filepath
        music.user = current_user
        current_user.musics.append(music)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(url_for('music'))
    return render_template('music_upload.html', form=form)


if __name__ == '__main__':
    main()
