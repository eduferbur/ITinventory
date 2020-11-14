#!/urs/bin/python3
"""
INFORMACIÓN SOBRE EL MÓDULO
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


class User:
    def __init__(self, name, cif, phone, address):
        self.__name = name
        self.__cif = cif
        self.__phone: int = phone
        self.__address = address


class Admin (User):
    def __init__(self, name, cif, phone, address):
        self.__access_level = "admin"
        super().__init__(name, cif, phone, address)


class Client (User):
    def __init__(self, name, cif, phone, address):
        self.__access_level = "client"
        super().__init__(name, cif, phone, address)



class Dealer (User):
    def __init__(self, name, cif, phone, address):
        self.__access_level = "dealer"
        super().__init__(name, cif, phone, address)
