from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from create_user import *
from DB import MySQL
app = Flask(__name__)
application = app

# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.from_pyfile('config.py')

db = MySQL(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно залогиниться'
login_manager.login_message_category = 'alert-warning'

login_manager.init_app(application)

class User(UserMixin):
    def __init__(self, login, user_id):
        self.login = login
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    user, flag = db.query("SELECT * FROM users where id = %s", (user_id,))
    if flag:

        return User(user[0].login, user_id)
    print("not success")

    return None


@app.route('/')
def index():
    table,flag = db.query("CALL GetUserWithRole();")

    return render_template('index.html', table=table)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form.get("login", False)
        password = request.form.get("password", False)
        remember_me = request.form.get('remember_me') == "on"

        res,flag = db.query("SELECT * FROM users where login = %s and password_hash=SHA2(%s,256)", (name,password))
        print(res)
        if res:

            user = User(res[0].login, res[0].id)
            login_user(user, remember=remember_me)
            flash("Успешно", "alert-success")

            return redirect(request.args.get("next") or url_for("index"))

        flash("Введены некорректные данные", "alert-danger")
    #
    return render_template('flask_login.html')


@app.route('/delete/<int:id>', methods=["POST","GET"])
@login_required
def delete(id):
    query,flag = db.query("DELETE FROM users where id = %s", (id,), True)
    if flag:
        flash("Пользователь успешно удален", "alert-success")
    else:
        flash("Ошибка на стороне серве", "alert-danger")
    return redirect(url_for('index'))




@app.route('/secret')
@login_required
def secret():
    # if not  current_user.is_authenticated:
    #     flash("Для доступа к этой странице нужно залогиниться", "alert-info")
    #     return redirect(url_for("login"))
    return render_template("secret.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/counter')
def counter():
    if "counter" in session:
        session["counter"] += 1
    else:
        session["counter"] = 1

    return render_template('counter.html')


@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    user,flag = db.query("SELECT * FROM users where id = %s", (id,))
    form = RegistrationForm(obj=user[0])  # Предзаполняем форму данными пользователя
    form.password.validators = []  # Убираем валидаторы пароля и его подтверждения
    form.confirm.validators = []

    if request.method == "POST" and form.validate():
        print("Информация пользователя успешно обновлена")
        query, flag = db.query("UPDATE users set login=%s, first_name=%s, middle_name=%s, last_name=%s, role_id=%s where id=%s",
                         (form.login.data,form.first_name.data, form.middle_name.data,
                          form.last_name.data,form.select_role.data, id), True)
        if flag:
            flash("Данные успешно отредактированы", "alert-success")
            return redirect(url_for("index"))
        flash("Изменения не вступили в силу", "alert-danger")
    return render_template('edit.html', form=form)


@app.route('/view/<int:id>', methods=["GET", "POST"])
def view(id):
    table, flag = db.query("SELECT a.*, b.description FROM users a join roles b on a.role_id=b.id having id=%s", (id,))
    print(table)
    return render_template('view.html', table=table)



@app.route('/updatepassword', methods=["GET", "POST"])
@login_required
def updatepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        id = current_user.id
        first_query, flag = db.query("SELECT * FROM users where id = %s and password_hash = SHA2(%s, 256)", (id, old_password))
        if first_query:
            last_query, flag2 = db.query("UPDATE users set password_hash = SHA2(%s, 256) where id = %s", (form.password.data, id))
            if flag2:
                flash("Пароль успешно обновлен", "alert-success")

                return redirect(url_for("index"))
        flash("Старый пароль неправильный", "alert-danger")
    return render_template('changepassword.html', form=form)





@app.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = RegistrationForm()
    if form.validate_on_submit():
        login_field = form.login.data
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        password = form.password.data
        role_id = form.select_role.data
        query, is_success = db.query(
            "INSERT INTO users (login, password_hash, first_name, middle_name, last_name,create_at, role_id) VALUES (%s, SHA2(%s,256), %s, %s, %s,NOW(), %s);",
            (login_field, password, first_name, middle_name, last_name, role_id), True)

        if is_success:
            flash("Пользователь успешно добавлен", "alert-success")
            return redirect(url_for("index"))
        flash("Отказано на стороне сервера", "alert-danger")


    else:
        print("Validation errors:", form.errors)
    return render_template('create.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)


# python3 -m venv ve
# . ve/bin/activate -- Linux
# ve\Scripts\activate -- Windows
# pip install flask python-dotenv