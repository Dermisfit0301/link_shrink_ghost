#link shrink ghost
from flask import Flask,render_template, request ,flash, redirect,  url_for
from datetime import datetime
import random 
import re
import os 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import string



#CONFIGURATION
link_shink_ghost = Flask(__name__)



basedir = os.path.abspath(os.path.dirname(__file__))
link_shink_ghost.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
link_shink_ghost.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Building a database 
db = SQLAlchemy(link_shink_ghost)
Migrate(link_shink_ghost, db)





################################################
#creating the shrinker 



#valid URL function
def isValidURL(str):
        regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")
        p = re.compile(regex)
        if (str == None):
            return False
        if(re.search(p, str)):
            return True
        else:
            return False
        
@link_shink_ghost.before_first_request
def create_tables():
    db.create_all()

class URL_shrinker(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url_input=db.Column(db.String(1000),nullable=False)
    url_output=db.Column(db.String(100),nullable=False,unique=True)
    created_time=db.Column(db.DateTime(),default=datetime.now(),nullable=False)
    def __init__(self, url_input, url_output):
        self.url_input = url_input
        self.url_output = url_output  


   
    
def shrink_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while (isValidURL(str) == True):
        rand_letters = random.choice(letters, k=3)
        rand_letters = "".join(rand_letters)
        shrunk_url = URL_shrinker.query.filter_by(url_output=rand_letters).first()
    if not shrunk_url:
        return rand_letters



###############################################

#Building a route 

@link_shink_ghost.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        found_url = URL_shrinker.query.filter_by(url_input=url_received).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.url_output))
        else:
            short_url = shrink_url()
            print(short_url)
            new_url = URL_shrinker(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('home.html')

@link_shink_ghost.route('/<short_url>')
def redirection(short_url):
    long_url = URL_shrinker.query.filter_by(url_output=short_url).first()
    if long_url:
        return redirect(long_url.url_input)
    else:
        return f'<h1>Url not found by GHOSTS</h1>'

@link_shink_ghost.route('/display/<url>')
def display_short_url(url):
    return render_template('home.html', short_url_display=url)

@link_shink_ghost.route('/history')
def display_all():
    return render_template('history.html', vals=URL_shrinker.query.all())

###############################################
#Running stage
if __name__ == '__main__':
    link_shink_ghost.run(port=5000,debug=True)