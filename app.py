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

# -------  CONFIGURAMOS LA BASE DE DATOS ------------------------------------------------------
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

usuario = Usuarios.query.all()

all_Usernames = []
for names in usuario:
    all_Usernames.append(names.username)
# print(all_Usernames)  # Lista con todos los usernames de la tabla
# -------  CONFIGURAMOS LA BASE DE DATOS. FIN ------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------


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

        if username in all_Usernames:  #Si nos llega un usuario de la tabla, lo guardamos, si no, falso.
            user = [x for x in usuario if x.username == username][0]
        else:
            user = False

        # COMPROBAMOS QUE TIPO DE ACCESO TIENE EL USUARIO
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_access_Level'] = user.access_Level
            if session['user_access_Level'] == 'admin':
                return redirect(url_for('profile_admin'))
            elif session['user_access_Level'] == 'cliente':
                return redirect(url_for('profile_client'))
            elif session['user_access_Level'] == 'proveedor':
                return redirect(url_for('profile_dealer'))
            else:
                return redirect(url_for('login'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')

@app.route('/profile_admin')
def profile_admin():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile_admin.html')

@app.route('/profile_client')
def profile_client():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile_client.html')

@app.route('/profile_dealer')
def profile_dealer():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile_dealer.html')

if __name__ == '__main__':
    app.run(debug=True)
