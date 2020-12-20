
from flask import (Flask,
                   g,  # Variables globales entre app.py y html
                   redirect,
                   render_template,
                   request,
                   session,  # gestion de usuarios frontend-backend
                   url_for,
                    Response
                   )

from matplotlib.figure import Figure
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import random

from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
from datetime import datetime, date, time, timedelta

# Variables globales
global generar_grafica_una_vez


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


'''class Inventario(db.Model):
    __tablename__ = "INVENTARIO"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    objeto = db.Column(db.String(200))
    caracteristicas = db.Column(db.String(200))
    fabricante = db.Column(db.String(200))
    ref = db.Column(db.String(200))
    stock = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Artículo: {self.caracteristicas}: {self.objeto}'''


'''class Pedidos(db.Model):
    __tablename__ = "PEDIDOS"  # Creamos la estructura, la tabla
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    comprador = db.Column(db.String(200))
    proveedor = db.Column(db.String(200))
    total = db.Column(db.String(200))

    def __repr__(self):  # Sacado de la web de Alchemy, para que me dé el nombre
        return f'Pedido del: {self.fecha}, de {self.comprador} a {self.proveedor}. Total: {self.total} €'''


db.create_all()
db.session.commit()
# Lecturas de las tablas y almacenado de sus registros
all_users = Usuarios.query.all()
all_admins = Admins.query.all()
all_clients = Clients.query.all()
all_suppliers = Suppliers.query.all()
# all_devices = Inventario.query.all()
# all_Orders = Pedidos.query.all()


# Extrayendo la lista total de usernames
all_Usernames = []
for names in all_users:
    all_Usernames.append(names.username)

print('NOMMMBRES', all_Usernames)
En_lista = Usuarios.query.filter(~Usuarios.rol_id.in_([1, 2])).first()  # Prueba de filtrado directamente en la tabla
# print(En_lista)


# -------  CONFIGURAMOS LA BASE DE DATOS. FIN ------------------------------------------------------
# --------------------------------------------------------------------------------------------------


# -------  CREAMOS PROVEEDORES ------------------------------------------------------
# --------------------------------------------------------------------------------------------------
nombres_proveedores = []
all_proveedores = Usuarios.query.filter(Usuarios.rol_id == 3)
# for names in all_usuarios if names.access_Level=="proveedor":
for names in all_proveedores:
    nombres_proveedores.append(names.username)

# ------- PLOTS ---------
# --------------------------------------------------------------------------------------------------
# Leemos desde la base de datos
df_pedidos = pd.read_sql_table('PEDIDOS', con=db.engine) # Indicamos la tabla a coger
df_inventario = pd.read_sql_table('INVENTARIO', con=db.engine)

df_pedidos['fecha'] = pd.to_datetime(df_pedidos['fecha'], format='%Y-%m-%d %H:%M:%S')
df_pedidos.sort_values('fecha', inplace=True) # el inplace hace: df['fecha'] = df.sort...



df_compras = df_pedidos[(df_pedidos["comprador"] == 'eduferbur') | (df_pedidos["comprador"] == 'cristian')]
# print(df_compras)
df_all_comprasGR = df_compras.groupby(pd.Grouper(key='fecha', freq="M")).agg({"total": 'sum'})
# del df_comprasGR['id']

df_all_comprasGR['Clase'] = 'compra'
# print(df_comprasGR)


df_all_ventas = df_pedidos[(df_pedidos["comprador"] != 'eduferbur') & (df_pedidos["comprador"] != 'cristian')]

df_all_ventasGR = df_all_ventas.resample('M', on='fecha').agg({"total": 'sum'})
df_all_ventasGR['Clase'] = 'venta'
# print(df_all_ventasGR)

df_resumen_compra_venta = pd.concat([df_all_comprasGR, df_all_ventasGR])
df_resumen_compra_venta.sort_values('fecha', inplace=True)

inventario_stock_min = 2
df_inventario_reponer = df_inventario[(df_inventario["stock"] <= inventario_stock_min)] # Elementos que necesitan ser repuestos
del df_inventario_reponer['id']

print(df_resumen_compra_venta)
print(df_inventario_reponer)

# Extraemos la info del resumen compra/venta para la tabla del admin.
compras_fechas = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'compra'].index)
compras_totales = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'compra']['total'])

ventas_fechas = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'venta'].index)
ventas_totales = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'venta']['total'])

compras_totalesACU = []
ventas_totalesACU = []

suma = 0
for acu in range(len(compras_totales)):
    suma += compras_totales[acu]
    compras_totalesACU.append(suma)

suma = 0
for acu in range(len(ventas_totales)):
    suma += ventas_totales[acu]
    ventas_totalesACU.append(suma)

beneficio_final = round(ventas_totalesACU[-1] - compras_totalesACU[-1], 2)
print(beneficio_final, 'beneficiooooooooo')

# ------- FLASK APP ---------
# --------------------------------------------------------------------------------------------------
@app.before_request  # Aun no sé para qué hace esto
def before_request():
    # print(session, "loginbefore")
    g.user = None

    if 'user_id' in session:
        user = [x for x in all_users if x.id == session['user_id']][0]
        g.user = user


@app.route('/')
def home():
    return render_template("index.html")  # Vincula el HTML


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

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
                # print("PRUEBA",session)

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

    # Si llego aquí, el login no ha ido bien asi que voy a login de nuevo
    session.pop("user", None)
    session.pop('username', None)
    return render_template('login.html')


@app.route('/logout')  # Cerrar session.
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    return render_template('index2.html', tables=[df_inventario_reponer.to_html(classes='data', header="true")])


@app.route('/profile_admin')
def profile_admin():
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del admin actual.
    g.user = [x for x in all_admins if x.username == session['username']][0]

    print(df_resumen_compra_venta)
    return render_template('profile_admin.html', tables=[df_inventario_reponer.to_html(classes='data', header="true")], beneficio=beneficio_final)
    # return render_template('profile_admin.html')


@app.route('/profile_client')
def profile_client():

    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del cliente actual.
    g.user = [x for x in all_clients if x.username == session['username']][0]
    # print(g.user.username)
    compras_cliente = df_pedidos[(df_pedidos["comprador"] == g.user.username)]
    print(compras_cliente)

    return render_template('profile_client.html')


@app.route('/profile_supplier')
def profile_supplier():
    print("Aqui?", g.user.username)
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del proveedor actual.
    g.user = [x for x in all_suppliers if x.username == session['username']][0]
    ventas_proveedor = df_pedidos[(df_pedidos["proveedor"] == g.user.username)]
    print(ventas_proveedor)
    return render_template('profile_supplier.html')


@app.route('/plot.png')
def plot_png():
    fig = crear_grafica(compras_fechas, compras_totalesACU, ventas_fechas, ventas_totalesACU)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    del fig
    return Response(output.getvalue(), mimetype='image/png')

def crear_grafica(A_eje_x, A_eje_y, B_eje_x=None, B_eje_y=None):
    # Queremos gráficas acumuladas
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(A_eje_x, A_eje_y, label="Compras")
    axis.plot(B_eje_x, B_eje_y, label="Ventas")
    axis.legend()
    return fig

if __name__ == '__main__':
    app.run(debug=True)



