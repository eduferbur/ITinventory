from flask import (Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_sqlalchemy import SQLAlchemy
from inventario.tablas_usuarios import Usuarios  # Recibo las clases con las tablas usuarios, admin, clientes y proveedores

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

# -------  CONFIGURAMOS LA BASE DE DATOS ------------------------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'  # NOS CONECTAMOS A LA BASE DE DATOS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # ESTO LO RECOMIENTA LA WEB DE SQLALCHEMY
db_usuarios = SQLAlchemy(app)  # Cursor para la base de datos





db_usuarios.create_all()
db_usuarios.session.commit()
# Lecturas de la tabla all_usuarios
all_usuarios = Usuarios.query.all()

# Extrayendo la lista total de usernames
all_Usernames = []
for names in all_usuarios:
    all_Usernames.append(names.username)

En_lista = Usuarios.query.filter(~Usuarios.rol_id.in_([1, 2])).first()
print(En_lista)



# print(all_Usernames)  # Lista con todos los usernames de la tabla
# -------  CONFIGURAMOS LA BASE DE DATOS. FIN ------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------


# -------  CREAMOS PROVEEDORES ------------------------------------------------------
nombres_proveedores = []
all_proveedores = Usuarios.query.filter(Usuarios.rol_id == 3)
# for names in all_usuarios if names.access_Level=="proveedor":
for names in all_proveedores:
    nombres_proveedores.append(names.username)
# print(nombres_proveedores)

'''class proveedor():
    def __init__(self, username, nombre_empresa=None, cif=None, direccion=None, IVA=None):
        self.__username = username
        self.__nombre = nombre_empresa
        self.__cif = cif
        self.__direccion = direccion
        self.__IVA = IVA

    def facturacion(self):
        """Calculamos el total de los pedidos realizados"""
        pass

    def descuento(self):
        """El proveedor podrá modificar el descuento de sus producto VOLVER A PEDIR CONTRASEÑA"""
        pass'''



@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in all_usuarios if x.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        if username in all_Usernames:  #Si nos llega un usuario de la tabla, lo guardamos, si no, falso.
            user = [x for x in all_usuarios if x.username == username][0]
        else:
            user = False

        # COMPROBAMOS QUE TIPO DE ACCESO TIENE EL USUARIO
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_rol_id'] = user.rol_id
            if session['user_rol_id'] == 1:
                return redirect(url_for('profile_admin'))
            elif session['user_rol_id'] == 2:
                return redirect(url_for('profile_client'))
            elif session['user_rol_id'] == 3:
                return redirect(url_for('profile_supplier'))
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

@app.route('/profile_supplier')
def profile_supplier():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile_supplier.html')

if __name__ == '__main__':
    app.run(debug=True)
