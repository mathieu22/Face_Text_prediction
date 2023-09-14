from flask import Flask, render_template,request,redirect, session, url_for,send_from_directory
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
import numpy as np
import joblib
import os
from prediction.text_sentiment import preprocess_text, text_prediction 
from prediction.face_sentiment import face_prediction

app = Flask(__name__)

#directory of image uploaded
UPLOAD_FOLDER = "static/uploads"
#extension d'image accéptée
ALLOWED_EXTENSIONS = {"png"}
#define to the app the root of the uploaded image
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'User'
 
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/text",methods=['GET','POST'])
def text_analysis():
    msg = ''
    if request.method == 'POST':
        text = request.form["text"]
        print(text)
        # if user does not select file, browser also
        # submit an empty part without filename
        if text == '':
            msq = 'Text vide'
            return redirect(request.url)
        else:
            return redirect(url_for('text_predict',text=text))
    return f'''
        <!doctype html>
    <title>Upload new Image</title>
    <h1>Write Your Text</h1>
    <form method=post>
      <input type=text name=text>
      <input type=submit value=Upload>
    </form>
    '''
@app.route("/text_predict/<text>",methods=['GET','POST'])
def text_predict(text):
    texts = preprocess_text(text)
    prediction = text_prediction(texts)
    return render_template('classification.html',text=text, prediction=prediction)
@app.route("/homepage")
def home():
    msg =''
    return render_template('index.html', msg = msg)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',filename=filename))
    return '''
        <!doctype html>
    <title>Upload new Image</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@app.route("/upload/<filename>",methods=["GET","POST"])
def uploaded_file(filename):
    sentiment = face_prediction(filename)
    return render_template('upload.html',source=filename,prediction=sentiment)
    

#enregistrement de l'utilisateur dans la base de données
app.secret_key = 'your secret key'
@app.route("/")
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    return render_template('index.html', msg = msg)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE name = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            print("ici")
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['name']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


if __name__ == "__main__":
    app.run(debug=True)
