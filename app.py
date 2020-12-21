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
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

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


db.create_all()
db.session.commit()

# Lecturas de las tablas y almacenado de sus registros
all_users = Usuarios.query.all()
all_admins = Admins.query.all()
all_clients = Clients.query.all()
all_suppliers = Suppliers.query.all()

# Extrayendo la lista total de usernames
all_Usernames = []
for names in all_users:
    all_Usernames.append(names.username)

print('NOMMMBRES', all_Usernames)
En_lista = Usuarios.query.filter(~Usuarios.rol_id.in_([1, 2])).first()  # Prueba de filtrado directamente en la tabla
# print(En_lista)


# -------  FIN DE CONFIGURAMOS LA BASE DE DATOS ------------------------------------------------------
# --------------------------------------------------------------------------------------------------


# -------  CREAMOS PROVEEDORES ------------------------------------------------------
# --------------------------------------------------------------------------------------------------
nombres_proveedores = []
all_proveedores = Usuarios.query.filter(Usuarios.rol_id == 3)
# for names in all_usuarios if names.access_Level=="proveedor":
for names in all_proveedores:
    nombres_proveedores.append(names.username)

# ------- TABLAS CON PANDAS---------
# --------------------------------------------------------------------------------------------------
# Leemos desde la base de datos
df_pedidos = pd.read_sql_table('PEDIDOS', con=db.engine)  # Indicamos la tabla a coger
df_inventario = pd.read_sql_table('INVENTARIO', con=db.engine)

df_pedidos['fecha'] = pd.to_datetime(df_pedidos['fecha'], format='%Y-%m-%d %H:%M:%S')
df_pedidos.sort_values('fecha', inplace=True)  # el inplace ahorra poner: df['fecha'] = df.sort...

df_compras = df_pedidos[(df_pedidos["comprador"] == 'eduferbur') | (df_pedidos["comprador"] == 'cristian')]
# print(df_compras)
df_all_comprasGR = df_compras.groupby(pd.Grouper(key='fecha', freq="M")).agg({"total": 'sum'})
df_all_comprasGR['Clase'] = 'compra'  # Añadimos columna para unificar luego con venta

df_all_ventas = df_pedidos[(df_pedidos["comprador"] != 'eduferbur') & (df_pedidos["comprador"] != 'cristian')]

df_all_ventasGR = df_all_ventas.resample('M', on='fecha').agg({"total": 'sum'}) # Otra forma de agrupar por meses
df_all_ventasGR['Clase'] = 'venta'

df_resumen_compra_venta = pd.concat([df_all_comprasGR, df_all_ventasGR])  # Unificamos compras y ventas.
df_resumen_compra_venta.sort_values('fecha', inplace=True)

inventario_stock_min = 2  # Valor mínimo de stock donde sadrá un aviso en la pag. de admin
df_inventario_reponer = df_inventario[
    (df_inventario["stock"] <= inventario_stock_min)]  # Elementos que necesitan ser repuestos
del df_inventario_reponer['id']  # Eliminamos la columna id para que la tabla quede más clara

# Extraemos la info del resumen compra/venta para la tabla del admin.
compras_fechas = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'compra'].index)
compras_totales = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'compra']['total'])

ventas_fechas = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'venta'].index)
ventas_totales = list(df_resumen_compra_venta[df_resumen_compra_venta["Clase"] == 'venta']['total'])

compras_totalesACU = []
ventas_totalesACU = []

# Para la compra/venta de la página Admin, queremos el acumulado del año:
suma = 0
for acu in range(len(compras_totales)):
    suma += compras_totales[acu]
    compras_totalesACU.append(suma)

suma = 0
for acu in range(len(ventas_totales)):
    suma += ventas_totales[acu]
    ventas_totalesACU.append(suma)

beneficio_final = round(ventas_totalesACU[-1] - compras_totalesACU[-1], 2)  # Beneficio final de la compra/venta


# compras_cliente = df_pedidos


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
                    print(f"Error ID=2, user_rol_id={session['user_id']}  no válido")
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


@app.route('/profile_admin')
def profile_admin():
    if not g.user:
        return redirect(url_for('login'))
    # Cargamos en g.user los datos del admin actual.
    g.user = [x for x in all_admins if x.username == session['username']][0]
    return render_template('profile_admin.html', tables=[df_inventario_reponer.to_html(classes='data', header="true")],
                           beneficio=beneficio_final)


@app.route('/profile_client')
def profile_client():
    if not g.user:
        return redirect(url_for('login'))

    # Cargamos en g.user los datos del cliente actual.
    g.user = [x for x in all_clients if x.username == session['username']][0]
    compras_cliente = df_pedidos[(df_pedidos["comprador"] == g.user.username)]
    compras_cliente = compras_cliente[['fecha', 'total']].head()  # tabla con los últimos 5 pedidos del cliente
    return render_template('profile_client.html', tables=[compras_cliente.to_html(classes='data', header="true")])


@app.route('/profile_supplier')
def profile_supplier():
    if not g.user:
        return redirect(url_for('login'))

    # Cargamos en g.user los datos del proveedor actual.
    g.user = [x for x in all_suppliers if x.username == session['username']][0]
    ventas_proveedor = df_pedidos[(df_pedidos["proveedor"] == g.user.username)]
    ventas_proveedor = ventas_proveedor[['fecha', 'total']].head()
    return render_template('profile_supplier.html', tables=[ventas_proveedor.to_html(classes='data', header="true")])


@app.route('/plot.png')
def plot_png():
    fig = None
    if session['user_rol_id'] == 1:  # Admin
        fig = crear_grafica(compras_fechas, compras_totalesACU, "plot", "Compras", ventas_fechas, ventas_totalesACU,
                            "Ventas")
    elif session['user_rol_id'] == 2:  # Cliente
        compras_cliente = df_pedidos[(df_pedidos["comprador"] == g.user.username)]
        compras_cliente = compras_cliente[compras_cliente["total"] != 0] # Eliminamos = 0€
        compras_cliente = compras_cliente.groupby(pd.Grouper(key='fecha', freq="M")).agg({"total": 'sum'})
        fig = crear_grafica(compras_cliente.index, compras_cliente['total'], "bar", "Pedidos")
        # print(df_all_comprasGR)
    elif session['user_rol_id'] == 3:  # Proveedor
        compras_a_proveedor = df_pedidos[(df_pedidos["proveedor"] == g.user.username)]
        compras_a_proveedor = compras_a_proveedor[compras_a_proveedor["total"] != 0] # Eliminamos = 0€
        compras_a_proveedor = compras_a_proveedor.groupby(pd.Grouper(key='fecha', freq="M")).agg({"total": 'sum'})
        fig = crear_grafica(compras_a_proveedor.index, compras_a_proveedor['total'], "bar", "Pedidos")
    else:
        print("Algo no contemplrado ha ocurrido. ID:1")

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def crear_grafica(A_eje_x, A_eje_y, tipo="plot", A_label="", B_eje_x=None, B_eje_y=None, B_label=""):
    # Queremos gráficas acumuladas
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    if tipo == "bar":
        axis.bar(A_eje_x, A_eje_y, label=A_label, width=10)
    else:
        axis.plot(A_eje_x, A_eje_y, label=A_label)
        axis.plot(B_eje_x, B_eje_y, label=B_label)
    axis.legend()
    return fig


if __name__ == '__main__':
    app.run(debug=True)
