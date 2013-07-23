from distutils.core import setup
import os.path

README = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(name='pqdict',
      version='0.3',
      description='An indexed priority queue implementation with a dictionary interface',
      author='Nezar Abdennur',
      author_email='nabdennur@gmail.com',
      url='https://github.com/nvictus/priority-queue-dictionary',
      license='MIT',
      py_modules=['pqdict'],
      test_suite='test_pqdict',
      long_description=open(README).read(),
      classifiers=["Development Status :: 4 - Beta",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Topic :: Software Development",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Libraries :: Python Modules"]
     )