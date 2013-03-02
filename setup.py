from distutils.core import setup

long_description = open('README.rst').read()

from mosql import __version__

setup(
    name    = 'mosql',
    description = 'MoSQL is a lightweight Python library which assists programmer to use SQL.',
    long_description = long_description,
    version = __version__,
    author  = 'Mosky',
    author_email = 'mosky.tw@gmail.com',
    url = 'http://github.com/moskytw/mosql',
    packages = ['mosql'],
)
