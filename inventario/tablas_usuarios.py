#!/urs/bin/python3
"""
CREACIÓN DE TABLAS DE USUARIOS:
ADMIN: ADMINISTRADORES DE LA PÁGINA
CLIENTES:
PROVEEDORES.

FINALMENTE UNA TABLA RELACIONAL CON TODOS LOS USUARIOS (PK: CIF o DNI)
"""
# METADATA:
__author__ = "Eduardo Fernandez Burraco"
__copyright__ = "Copyright 2020, EFB"
__credits__ = "Tokio School"

__license__ = "Tokio School"
__version__ = "1.0"
__maintainer__ = "Yo mismo"
__email__ = "eduferbur@gmail.com"
__status__ = "Developer"


from app import db_usuarios

class Usuarios(db_usuarios.Model):
    __tablename__ = "Users"  # Creamos la estructura, la tabla
    id = db_usuarios.Column(db_usuarios.Integer, primary_key=True)  # Columna ID con una clave única
    username = db_usuarios.Column(db_usuarios.String(200))
    password = db_usuarios.Column(db_usuarios.String(200))
    rol_id = db_usuarios.Column(db_usuarios.Integer)

    def __repr__(self): # Sacado de la web de Alchemy, para que me dé el nombre
        return '<User %r>' % self.username

