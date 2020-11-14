from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
# long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='inventario',
    version='1.0.0',
    author='Eduardo Fernandez',
    url='https://github.com/eduferbur/ITinventory.git',
    description='IT inventory with Users (Admin, Clients,Dealers ',
    # license='Apache 2.0',
    packages=find_packages(),
    # install_requires=['requests==2.20.0'],
    entry_points={
        'console_scripts': ['inventario = inventario.app:run'],
    }
)