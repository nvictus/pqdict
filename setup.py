#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


classifiers = """\
    Development Status :: 5 - Production/Stable
    Operating System :: OS Independent
    License :: OSI Approved :: MIT License
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: 3.7
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
"""


def _read(*parts, **kwargs):
    filepath = os.path.join(os.path.dirname(__file__), *parts)
    encoding = kwargs.pop('encoding', 'utf-8')
    with io.open(filepath, encoding=encoding) as fh:
        text = fh.read()
    return text


def get_version():
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        _read('pqdict', '__init__.py'),
        re.MULTILINE).group(1)
    return version


def get_long_description():
    return _read('README.rst')


setup(
    name='pqdict',
    version=get_version(),
    license='MIT',
    description='A Pythonic indexed priority queue',
    long_description=get_long_description(),
    keywords=['dict', 'priority queue', 'heap', 'scheduler', 'data structures'],
    author='Nezar Abdennur',
    author_email='nabdennur@gmail.com',
    url='https://github.com/nvictus/priority-queue-dictionary',
    packages=['pqdict'],
    zip_safe=False,
    classifiers=[s.strip() for s in classifiers.split('\n') if s],
    install_requires=['six'],
    tests_require=['pytest'],
    extras_require={'docs': ['Sphinx>=1.1', 'numpydoc']},
)
