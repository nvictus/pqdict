from distutils.core import setup
import os.path
import pqdict

README = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(name='pqdict',
      version='%d.%d' % pqdict.__version__[:-1],
      description='A dictionary-like indexed priority queue',
      author='Nezar Abdennur',
      author_email='nabdennur@gmail.com',
      url='https://github.com/nvictus/priority-queue-dictionary',
      license='MIT',
      py_modules=['pqdict'],
      long_description=open(README).read(),
      keywords='dict priority queue heap scheduler data structures',
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: Implementation :: CPython",
                   "Programming Language :: Python :: Implementation :: PyPy",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Software Development",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Libraries :: Python Modules"]
     )