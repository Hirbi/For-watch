from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from data import db_session, news, users, jobs
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


class JobsForm(FlaskForm):
    team_leader = StringField('Team leader', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    work_size = StringField('Work size', validators=[DataRequired()])
    collabarators = StringField('collabarators', validators=[DataRequired()])
    is_finished = BooleanField('Finished?')
    submit = SubmitField('Apply')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = StringField("Почта", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание')
    is_private = BooleanField('Личное')
    submit = SubmitField('Добавить')


@app.route('/news', methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        new = news.News()
        new.title = form.title.data
        new.content = form.content.data
        new.is_private = form.is_private.data
        current_user.news.append(new)
        sessions.merge(current_user)
        sessions.commit()
        return redirect('/')
    return render_template("news.html", title='Добавление новости', form=form)


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        job = jobs.Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collabarators=form.collabarators.data,
            is_finished=form.is_finished.data
        )
        # user.set_password(form.password.data)
        sessions.add(job)
        sessions.commit()
        return redirect("/")
    return render_template('add_job.html', title='add_job', form=form, message="")


@app.route('/list_jobs')
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        sessions = db_session.create_session()
        new = sessions.query(news.News).filter(
            news.News.id == id, news.News.user == current_user).first()
        if new:
            form.title.data = new.title
            form.content.data = new.content
            form.is_private.data = new.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        sessions = db_session.create_session()
        new = sessions.query(news.News).filter(
            news.News.id == id, news.News.user == current_user).first()
        if new:
            new.title = form.title.data
            new.content = form.content.data
            new.is_private = form.is_private.data
            sessions.commit()
            return redirect("/")
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobsForm()
    if request.method == "GET":
        sessions = db_session.create_session()
        job_old = sessions.query(jobs.Jobs).filter(
            jobs.Jobs.id == id, jobs.Jobs.user == current_user).first()
        if not job_old:
            job_old = sessions.query(jobs.Jobs).filter(
                jobs.Jobs.id == id, current_user.id == 1).first()
        if job_old:
            form.team_leader.data = job_old.team_leader
            form.job.data = job_old.job
            form.work_size.data = job_old.work_size
            form.collabarators.data = job_old.collabarators
            form.is_finished.data = job_old.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        sessions = db_session.create_session()
        job_old = sessions.query(jobs.Jobs).filter(
            jobs.Jobs.id == id, jobs.Jobs.user == current_user).first()
        if not job_old:
            job_old = sessions.query(jobs.Jobs).filter(
                jobs.Jobs.id == id, current_user.id == 1).first()
        if job_old:
            job_old.team_leader = form.team_leader.data
            job_old.job = form.job.data
            job_old.work_size = form.work_size.data
            job_old.collabarators = form.collabarators.data
            job_old.is_finished = form.is_finished.data
            sessions.commit()
            return redirect("/")
        else:
            abort(404)
    return render_template('add_job.html', title='Редактирование работы', form=form)


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    sessions = db_session.create_session()
    jobt = sessions.query(jobs.Jobs).filter(
        jobs.Jobs.id == id, jobs.Jobs.user == current_user).first()
    if not jobt:
        jobt = sessions.query(jobs.Jobs).filter(
            jobs.Jobs.id == id, current_user.id == 1).first()
    if jobt:
        sessions.delete(jobt)
        sessions.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def new_delete(id):
    sessions = db_session.create_session()
    new = sessions.query(news.News).filter(
        news.News.id == id, news.News.user == current_user).first()
    if new:
        sessions.delete(new)
        sessions.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        user = sessions.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        print(user)
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f'Вы пришли на эту страницу {visits_count + 1} раз')
        res.set_cookie("visits_count", str(visits_count + 1), max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response('Вы пришли на эту страницу в первый раз за 2 года')
        res.set_cookie("visits_count", "1", max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/session_test')
def session_test():
    session.permanent = True
    session['visits_count'] = session.get('visits_count', 0) + 1
    return f"Вы зашли на страницу {session['visits_count']} раз!"


@app.route("/")
def index():
    sessions = db_session.create_session()
    if current_user.is_authenticated:
        new = sessions.query(news.News).filter((news.News.user == current_user)
                                               | (news.News.is_private != True))
    else:
        new = sessions.query(news.News).filter(news.News.is_private != True)
    job = sessions.query(jobs.Jobs).filter(jobs.Jobs.is_finished != True).all()
    return render_template("index.html", news=new, jobs=job)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = users.User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            password=form.password.data
        )
        # user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/blogs.sqlite")
    sessions = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
