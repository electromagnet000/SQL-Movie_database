import os

from sqlalchemy import create_engine, text, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, UserMixin, current_user, logout_user, login_required
from wtforms import StringField, SubmitField, IntegerField, FloatField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from API_JSON.API_functionality import API_add_movie

"""
os filepath defined
"""
# using os to dynamicaly create the path relative to the current scripts location address
current_directory = os.path.dirname(os.path.abspath(__file__))
relative_db_path = os.path.join(current_directory, 'data', 'Userdata.sqlite')

"""
Global variables
"""

engine = create_engine(f"sqlite:///{relative_db_path}", echo=True)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{relative_db_path}"
app.config['SECRET_KEY'] = "super_secret_key"
bcrypt = Bcrypt()
bcrypt.init_app(app)
db = SQLAlchemy()
db.init_app(app)

"""
Session - sqlalchem.orm
"""
Session = sessionmaker(bind=engine)
session = Session()

"""
flask login
"""

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


"""
Classes - Forms
"""


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], render_kw={"placeholder": "username"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "password"})
    submit = SubmitField("login")


class UpdateForm(FlaskForm):
    username = StringField("Username", default=current_user)
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    check_password = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Update")


"""
Data Models 
"""


class Movies(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    year = db.Column(db.Integer)
    poster = db.Column(db.String)
    imdb_rating = db.Column(db.String)
    notes = db.Column(db.String)

    # using lazy for query effiency
    data = relationship("Data", backref="movies", lazy=True)

    def __repr__(self):
        return f"{self.title}"


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

    # using lazy for query effiency
    data = relationship("Data", backref="users", lazy=True)

    def __repr__(self):
        return f"{self.username}"


class Data(db.Model):
    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.String, db.ForeignKey("movies.id"))
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    notes = db.Column(db.String)

    def __repr__(self):
        return f"{self.name}"


"""
SQLDATAMANAGER
"""


class sql_data_manager():

    def list_users():
        with engine.connect() as conn:
            results = conn.execute(text("Select * From Users"))
            users = [{"id": row[0], "username": row[1], "password": row[2]} for row in results]
            return users

    def get_user_movies():
        user_movies = Data.query.filter_by(user_id=current_user.id).all()
        movies = []

        for data in user_movies:
            movie_id = data.movie_id
            movie = Movies.query.get(movie_id)
            movie.notes = data.notes
            movies.append(movie)

        return movies


"""
Main application and APP ROUTES 
"""


# Home page
@app.route("/", methods=["GET", "POST"])
def Home():
    logout_user()
    users = sql_data_manager.list_users()
    return render_template("home.html", users=users)


# Login page
@app.route("/login", methods=["GET", "POST"])
def Login():
    # sets the form
    form = LoginForm()
    user_name = request.args.get("user")

    if request.method == "POST":

        # checks the validation on the forms
        if form.validate_on_submit():

            # form data
            username = form.username.data
            check_password = form.password.data

            # finds user
            user = Users.query.filter_by(username=username).first()
            if user:
                # validates password
                if bcrypt.check_password_hash(user.password_hash, check_password):
                    login_user(user)
                    flash("successful login!")
                    return redirect(url_for("dashboard"))
                else:
                    flash("Incorrect password")
            else:
                flash("user not found")
        else:
            flash("there seems to be an error with your input please regular characters and enter both fields")
    return render_template("login.html", form=form, user_name=user_name)


"""
The users_home page
"""


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if current_user.is_authenticated:
        movies = sql_data_manager.get_user_movies()
        return render_template("dashboard.html", user=current_user, movies=movies, )


@app.route("/accountSettings/<int:user_id>", methods=['GET', "POST"])
@login_required
def account_settings(user_id):
    if current_user.is_authenticated:
        return render_template("account_settings.html", user=current_user, user_id=user_id)


@app.route("/accessibility_settings/<int:user_id>", methods=['GET', "POST"])
@login_required
def accessibility_settings(user_id):
    if current_user.is_authenticated:
        return render_template("accessibility_settings.html", user=current_user, user_id=user_id)


# update page
@app.route("/update/<int:user_id>", methods=["GET", "POST"])
@login_required
def update(user_id):
    form = UpdateForm()

    if current_user.is_authenticated:
        # gets the chosen user
        name_to_update = Users.query.get_or_404(user_id)

        if request.method == "POST":
            if form.validate_on_submit():
                # form data
                new_username = form.username.data
                new_password = form.password.data
                check_password = form.check_password.data

                # if the user wants to change username checks if username is taken
                if new_username != name_to_update.username:
                    already_user = Users.query.filter_by(username=new_username).first()
                    if already_user is None:
                        try:
                            name_to_update.username = new_username
                        except Exception as e:
                            flash(f"there seems to be a problem {e}")
                    else:
                        flash("username already taken")
                        return redirect(url_for("update", user_id=user_id))

                # if the user did not want to change username
                if new_password == check_password:
                    # changes to the desired username and hashes new chosen password
                    name_to_update.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    try:
                        db.session.commit()
                        flash("User Updated Successfully!")
                        return redirect(url_for("dashboard"))

                    except Exception as e:
                        flash(f"There seems to be an error {e}")
                        return render_template("update.html", name_to_update=name_to_update)
                else:
                    flash("passwords did not match")

        return render_template("update.html", form=form, user_id=user_id)


# delete page
@app.route("/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete(user_id):
    if current_user.is_authenticated:
        # sets a variable to the current user
        name_to_delete = current_user
        # gets the user data
        if request.method == "POST":
            confirm_username = request.form.get("confirm_username")

            # confirms that user entered correct username to delete account
            if name_to_delete.username == confirm_username:
                try:
                    # deletes the account from database by filtering for the confirmed username
                    Users.query.filter_by(username=confirm_username).delete()
                    flash("user deleted Successfully!!!")
                    db.session.commit()
                    return redirect(url_for("Home"))
                except Exception as e:
                    flash(f"there was an error : {e}")
            else:
                flash("username did not match")

        return render_template("delete_user.html", user=name_to_delete, user_id=name_to_delete.id)


# adds a movie
@app.route("/dashboard/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    movies = sql_data_manager.get_user_movies()

    if request.method == "POST":

        movie_title = request.form.get("movie_chosen")
        user_notes = request.form.get("notes")
        try:
            movie = API_add_movie(movie_title)
            new_movie = Movies(id=movie["imdbID"], title=movie["Title"], year=movie["Year"], poster=movie["Poster"],
                               imdb_rating=movie["imdbRating"])
            user_has_movie = Data.query.filter_by(movie_id=new_movie.id, user_id=user_id).first()

            # checks if user already has the movie in their database
            if user_has_movie:
                flash("Movie already in database")
                return redirect("add_movie")

            # check if movie is in the movies table using the unique imdbID
            check_movie = Movies.query.filter_by(id=new_movie.id).first()
            # if movie is in the database
            if check_movie:
                # skip adding the movie to the movie table, and links the imdbID to the user_id
                new_data = Data(movie_id=new_movie.id, user_id=user_id, notes=user_notes)
                db.session.add(new_data)

            # if movie is not in the movie database
            else:
                # add it to the movie table database
                db.session.add(new_movie)
                new_data = Data(movie_id=new_movie.id, user_id=user_id, notes=user_notes)
                db.session.add(new_data)

            # commit the session
            db.session.commit()
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"There seems to be a problem : {e}")
            session.rollback()

    return render_template("add_movie.html", user=current_user, user_id=user_id, movies=movies)


# update movie
@app.route("/dashboard/<int:user_id>/update_movie/<string:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    # search data table for the user and movie corrolation
    data_record = Data.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if request.method == "POST":
        new_notes = request.form.get("notes")
        try:
            # assings the new value to the notes column
            data_record.notes = new_notes
            flash("Successfully updated the movie")
            db.session.commit()
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"There was a problem : {e}")

    return render_template("update_movie.html", user=current_user, user_id=user_id, movie_id=movie_id)


# deletes a users movie
@app.route("/dashboard/<int:user_id>/delete_movie/<string:movie_id>", methods=["GET"])
def delete_movie(user_id, movie_id):
    chosen_movie = Data.query.filter_by(movie_id=movie_id, user_id=user_id).first()
    db.session.delete(chosen_movie)
    db.session.commit()
    return redirect(url_for("dashboard"))


# add user page
@app.route("/add_users", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":

        # form data
        new_username = request.form.get("username")
        password = request.form.get("password")
        check_password = request.form.get("check_password")

        # confirms password
        if password == check_password:
            # checks username
            already_user = Users.query.filter_by(username=new_username).first()
            if already_user is None:
                # adds user to the session and commits the new user to the database
                try:
                    new_user = Users(username=new_username,
                                     password_hash=bcrypt.generate_password_hash(password).decode('utf-8'))
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect(url_for("Home"))
                except Exception as e:
                    flash(f"there was an error {e}")
                    session.rollback()

            # flashes message if user has username
            else:
                flash("User already Exists please chose another username")
        # flashes message if passwords did not match
        else:
            flash("passwords did not match")

    return render_template("add_user.html")


"""
Error Handling
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/something")
def something():
    return render_template("something.html")


if __name__ in "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    # with app.app_context():
    #      db.create_all()
