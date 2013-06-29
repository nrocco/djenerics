#!/usr/bin/env python
from setuptools import setup
import djangogenerics

setup(
    name = 'djangogenerics',
    version = djangogenerics.__version__,
    packages = [
        'djangogenerics'
    ],
    download_url = 'http://github.com/nrocco/djangogenerics',
    url = 'http://nrocco.github.io/',
    author = djangogenerics.__author__,
    author_email = 'dirocco.nico@gmail.com',
    description = 'A collection of Django 1.5+ utilities',
    long_description = open('README.rst').read(),
    include_package_data = True,
    license = open('LICENSE').read(),
    zip_safe = False,
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
