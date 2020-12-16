from flask import (Flask,
                   g, # Variables globales entre app.py y html
                   redirect,
                   render_template,
                   request,
                   session,  # gestion de usuarios frontend-backend
                   url_for
                   )

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

# -------  CONFIGURAMOS LA BASE DE DATOS ------------------------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'  # NOS CONECTAMOS A LA BASE DE DATOS
# app.config['SQLALCHEMY_BINDS'] = {'inventary': 'sqlite:///database/inventary.db'}  # NOS CONECTAMOS A OTRA DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ESTO LO RECOMIENTA LA WEB DE SQLALCHEMY
db = SQLAlchemy(app)  # Cursor para la base de datos

class Usuarios(db.Model):
    __tablename__ = "USERS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)  # Columna ID con una clave única
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    rol_id = db.Column(db.Integer)

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return '<User %r>' % self.username


class Admins(db.Model):
    __tablename__ = "ADMINS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(200))
    nombre = db.Column(db.String(200))
    username = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Administrador {self.nombre}'


class Clients(db.Model):
    __tablename__ = "CLIENTS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    cif = db.Column(db.String(200))
    nombreFiscal = db.Column(db.String(200))
    descuento = db.Column(db.Float)
    username = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Cliente {self.nombreFiscal} con CIF {self.cif}'


class Suppliers(db.Model):
    __tablename__ = "SUPPLIERS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    cif = db.Column(db.String(200))
    nombreFiscal = db.Column(db.String(200))
    Telefono = db.Column(db.Integer)
    direccion = db.Column(db.String(200))
    descuento = db.Column(db.Float)
    facturacion = db.Column(db.Float)
    username = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Proveedor {self.nombreFiscal} con CIF {self.cif}'

    def facturacion(self):
        """Calculamos el total de los pedidos realizados"""
        pass


class Inventario(db.Model):
    __tablename__ = "INVENTARIO"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    objeto = db.Column(db.String(200))
    caracteristicas = db.Column(db.String(200))
    fabricante = db.Column(db.String(200))
    ref = db.Column(db.String(200))
    stock = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Artículo: {self.caracteristicas}: {self.objeto}'

class Pedidos(db.Model):
    __tablename__ = "PEDIDOS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    comprador = db.Column(db.String(200))
    proveedor = db.Column(db.String(200))
    total = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Pedido del: {self.fecha}, de {self.comprador} a {self.proveedor}. Total: {self.total} €'

db.create_all()
db.session.commit()
# Lecturas de las tablas y almacenado de sus registros
all_users = Usuarios.query.all()
all_admins = Admins.query.all()
all_clients = Clients.query.all()
all_suppliers = Suppliers.query.all()
all_devices = Inventario.query.all()
all_Orders = Pedidos.query.all()

# Extrayendo la lista total de usernames
all_Usernames = []
for names in all_users:
    all_Usernames.append(names.username)

En_lista = Usuarios.query.filter(~Usuarios.rol_id.in_([1, 2])).first()  # Prueba de filtrado directamente en la tabla
# print(En_lista)


# -------  CONFIGURAMOS LA BASE DE DATOS. FIN ------------------------------------------------------
# --------------------------------------------------------------------------------------------------


# -------  CREAMOS PROVEEDORES ------------------------------------------------------
nombres_proveedores = []
all_proveedores = Usuarios.query.filter(Usuarios.rol_id == 3)
# for names in all_usuarios if names.access_Level=="proveedor":
for names in all_proveedores:
    nombres_proveedores.append(names.username)


@app.before_request  # Aun no sé para qué hace esto
def before_request():
    print(session, "loginbefore")
    g.user = None

    if 'user_id' in session:
        user = [x for x in all_users if x.id == session['user_id']][0]
        g.user = user
        pedidos = [x for x in all_Orders if x.comprador == g.user.username]
        print(pedidos)

@app.route('/')
def home():
    return render_template("index.html")  # Vincula el HTML

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # session.pop('user_id', None)

        session['username'] = request.form['username']  # Recogemos el username introducido.
        password = request.form['password']  # Recogemos la contraseña introducida

        if session['username'] in all_Usernames:  # Si nos llega un usuario de la tabla, lo guardamos, si no, falso.
            # Almacenamos todos los datos del usuario actual
            user = [x for x in all_users if x.username == session['username']][0]
            # User será un registro de la tabla "Users"

            # COMPROBAMOS QUE COINCIDE USUARIO Y CONTRASEÑA Y EL TIPO DE ACCESO
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
                    print(f"Error, user_rol_id={session['user_id']}  no válido")
                    session['user_id'] = None
            else:
                user = False  # Si no coincide usuario y contraseña, borro el usuario de sesion
        else:
            user = False

    # Si llego aquí, el login no ha ido bien y calgo login de nuevo
    session.pop("user", None)
    session.pop('username', None)
    return render_template('login.html')


@app.route('/logout')  # Cerrar session.
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')


@app.route('/profile_admin')
def profile_admin():
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del admin actual.
    g.user = [x for x in all_admins if x.username == session['username']][0]
    return render_template('profile_admin.html')


@app.route('/profile_client')
def profile_client():
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del cliente actual.
    g.user = [x for x in all_clients if x.username == session['username']][0]
    return render_template('profile_client.html')


@app.route('/profile_supplier')
def profile_supplier():
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del proveedor actual.
    g.user = [x for x in all_suppliers if x.username == session['username']][0]
    return render_template('profile_supplier.html')


if __name__ == '__main__':
    app.run(debug=True)
