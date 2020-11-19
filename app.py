from flask import (Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

# -------  BASE DE DATOS ---------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'  # NOS CONECTAMOS A LA BASE DE DATOS
db_usuarios = SQLAlchemy(app)  # Cursor para la base de datos

class Usuarios(db_usuarios.Model):
    __tablename__ = "Usuarios"  # Creamos la estructura, la tabla
    id = db_usuarios.Column(db_usuarios.Integer, primary_key=True)  # Columna ID con una clave única
    username = db_usuarios.Column(db_usuarios.String(200))
    password = db_usuarios.Column(db_usuarios.String(200))
    access_Level = db_usuarios.Column(db_usuarios.String(10))

    def __repr__(self): # Sacado de la web de Alchemy, para que me dé el nombre
        return '<User %r>' % self.username

db_usuarios.create_all()
db_usuarios.session.commit()

usernames = []
usuario = Usuarios.query.all()
for user in usuario:
    usernames.append(user.password)

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in usuario if x.id == session['user_id']][0]
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in usuario if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
