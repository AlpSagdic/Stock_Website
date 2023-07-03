from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap
from data import stocks_dict
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "http://api.marketstack.com/v1/intraday"

app = Flask(__name__)
app.config["SECRET_KEY"] = "YOU_CAN_WRITE_WHATEVER_YOU_WANT"
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Database
class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=False, nullable=False)
    user_email = db.Column(db.String(100), unique=False, nullable=False)
    message_subject = db.Column(db.String(100), unique=False, nullable=False)
    message = db.Column(db.String(5000), unique=False, nullable=False)


#We used it to create the database.
#with app.app_context():
#   db.create_all()


#Forms
class ShareForm(FlaskForm):
    share_name = SelectField("Which stock do you want to research?",
                             choices=["MSFT",
                                      "AAPL",
                                      "AMZN",
                                      "GOOG",
                                      "GOOGL",
                                      "BABA",
                                      "FB",
                                      "NVDA",
                                      "ORCL",
                                      "C"],
                             validators=[DataRequired()])
    submit = SubmitField("Search")


class ContactForm(FlaskForm):
    user_name = StringField("What's Your Name?", validators=[DataRequired()])
    user_email = EmailField("What's Your Email Address?", validators=[Email()])
    message_subject = StringField("What's Your Subject?", validators=[DataRequired()])
    message = StringField("What's Your Message?", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def home():
    stock_info = {}
    form = ShareForm()
    if form.validate_on_submit():
        SYMBOLS = form.share_name.data
        parameters = {
            "access_key": API_KEY,
            "symbols": SYMBOLS,
        }

        response = requests.get(url=BASE_URL, params=parameters).json()
        stock_info = {"name": response["data"][0]["symbol"],
                      "open_price": response["data"][0]["open"],
                      "last_price": response["data"][0]["last"],
                      "high_price": response["data"][0]["high"]}
    return render_template("index.html", form=form, stock_info=stock_info)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        user_info = UserInfo(
            user_name=form.user_name.data,
            user_email=form.user_email.data,
            message_subject=form.message_subject.data,
            message=form.message.data
        )
        db.session.add(user_info)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("contact.html", form=form)


@app.route("/stocks")
def stocks():
    stocks_list = stocks_dict
    return render_template("stocks.html", stocks_list=stocks_list)


if __name__ == "__main__":
    app.run(debug=True)
