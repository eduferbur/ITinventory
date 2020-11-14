import sys
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from inventario import users  # inventario es la carpeta, users es el archivo.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/inventory.db'
db = SQLAlchemy(app)  # Cursor para la base de datos


@app.route('/login')
def home():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
