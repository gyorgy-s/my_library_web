"""Main for the My library website."""
from flask import Flask, render_template, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Integer, Float, VARCHAR, exc
from sqlalchemy.orm import Mapped, mapped_column

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"

app.secret_key = "aslk234!@#asdGRS?242DOmoiasdN"

db = SQLAlchemy()
db.init_app(app)


class Books(db.Model):
    """Class to represent the table in the SQLite DB. PRIMARY KEY = id, UNIQUE = name"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[VARCHAR(250)] = mapped_column(VARCHAR(250), unique=True, nullable=False)
    author: Mapped[VARCHAR(250)] = mapped_column(VARCHAR(250), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<[Books] {self.name} - {self.author}>"


class BookForm(FlaskForm):
    """Form class to represent the input fields."""

    name = StringField(label="Book name", validators=[DataRequired()])
    author = StringField(label="Book author", validators=[DataRequired()])
    score = FloatField(label="Score")


def create_db():
    """Create DB using SQLAlchemy."""
    with app.app_context():
        db.create_all()


def create_book(name: str, author: str, score: float):
    """Create record using SQLAlchemy."""
    with app.app_context():
        db.session.add(Books(name=name, author=author, score=score))
        db.session.commit()


def update_book(book, name: str, author: str, score: float):
    """Update the whole record, selected by ID."""
    with app.app_context():
        book_to_update = db.session.execute(db.select(Books).where(Books.id == book.id)).scalar()
        book_to_update.name = name
        book_to_update.author = author
        book_to_update.score = score
        db.session.commit()


def get_all_books():
    """Using SQLALchemmy returns the whole table as a list of Scalars()."""
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.id), execution_options={"prebuffer_rows": True}).scalars()
    return result


def get_book(id: int):
    """Using SQLALchemy returns a Scalar for the record based on ID."""
    with app.app_context():
        result = db.get_or_404(Books, id)
    return result


def delete_book(id: int):
    """Using SQLAlchemy deletes teh record with thte given ID."""
    book_to_delete = get_book(id)
    db.session.delete(book_to_delete)
    db.session.commit()


@app.route("/", methods=["GET", "POST"])
def home():
    """Home screen, displaying the conents of the dm table if any."""
    result = get_all_books()
    if request.method == "POST":
        if request.form["button"][:6] == "delete":
            delete_book(int(request.form["button"][6:]))
            result = get_all_books()
        return render_template("index.html", books=result)
    if request.method == "GET":
        return render_template("index.html", books=result)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Adds a new record to the DB. Checks for valid fields,
    displays the error message if the insertion fails
    (ex.: existing unique field in the table)"""
    form = BookForm()
    if request.method == "POST":
        if request.form["button"] == "insert":
            if form.validate_on_submit():
                try:
                    create_book(
                        name=form.name.data,
                        author=form.author.data,
                        score=form.score.data,
                    )
                except exc.IntegrityError as err:
                    return render_template("add.html", form=form, msg=err.orig)
                return redirect(url_for("home"))
        elif request.form["button"] == "back":
            return redirect(url_for("home"))

    return render_template("add.html", form=form)


@app.route("/edit-book", methods=["GET", "POST"])
def edit_book():
    """Edit the selected record in the DB. Checks for valid fields."""
    form = BookForm()
    book_to_edit = get_book(id=request.values["id"])
    if request.method == "POST":
        if request.form["button"] == "update":
            if form.validate_on_submit():
                try:
                    update_book(
                        book_to_edit,
                        name=form.name.data,
                        author=form.author.data,
                        score=form.score.data,
                    )
                except exc.IntegrityError as err:
                    return render_template("edit_book.html", book=book_to_edit, form=form, msg=err.orig)
                return redirect(url_for("home"))
            return render_template("edit_book.html", book=book_to_edit, form=form)
        elif request.form["button"] == "back":
            return redirect(url_for("home"))
    else:
        return render_template("edit_book.html", book=book_to_edit, form=form)


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
