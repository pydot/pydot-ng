#!/usr/bin/env python
from codecs import open
import os
from setuptools import setup


os.environ['COPY_EXTENDED_ATTRIBUTES_DISABLE'] = 'true'
os.environ['COPYFILE_DISABLE'] = 'true'

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='pydot_ng',
    version='1.0.0',
    description='Python interface to Graphviz\'s Dot',
    author='Ero Carrera',
    author_email='ero@dkbza.org',
    maintainer='Sebastian Kalinowski',
    maintainer_email='sebastian@kalinowski.eu',
    license='MIT',
    keywords='graphviz dot graphs visualization',
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    long_description=readme,
    packages=['pydot_ng'],
    package_dir={'pydot_ng': 'pydot_ng'},
    install_requires=[
        'pyparsing>=2.0.1',
    ],
    )
