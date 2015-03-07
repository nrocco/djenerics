#!/usr/bin/env python
import re

from setuptools import setup

setup(
    name = 'djenerics',
    version = re.search(r'''^__version__\s*=\s*["'](.*)["']''', open('djenerics/__init__.py').read(), re.M).group(1),
    packages = [
        'djenerics'
    ],
    download_url = 'http://github.com/nrocco/djenerics',
    url = 'http://nrocco.github.io/',
    author = 'Nico Di Rocco',
    author_email = 'dirocco.nico@gmail.com',
    description = 'A collection of Django 1.5+ and Django Rest Framework 3.0+ utilities',
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
