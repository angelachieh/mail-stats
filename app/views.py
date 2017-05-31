from flask import render_template, redirect, url_for, request
from app import app
from stats.mailStatistics import *
from form import LoginForm

# index view function suppressed for brevity

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def index():
  form = LoginForm()
  if form.validate_on_submit():
    username = request.form.get('username')
    password = request.form.get('password')
    folder = request.form.get('folder')
    isCaseSensitive = False
    gmail = Mail(username, password, service=GMAIL)
    nbMails = 10
    nbWords = 10
    words, counts = mostUsedWordsInFolder(gmail, folder, isCaseSensitive, nbMails, nbWords)
    return render_template("stats.html", values=counts, keys=words, nbWords=nbWords)

  return render_template('login.html', form=form)