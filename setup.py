#!/usr/bin/env python
import ast
import os
import re
from codecs import open

from setuptools import setup


# NOTE(prmtl): found reason on https://superuser.com/q/259703
os.environ['COPY_EXTENDED_ATTRIBUTES_DISABLE'] = 'true'
os.environ['COPYFILE_DISABLE'] = 'true'


CURRENT_DIR = os.path.dirname(__file__)


def get_version():
    init_file = os.path.join(CURRENT_DIR, 'pydot_ng', '__init__.py')
    _version_re = re.compile(r'__version__\s+=\s+(?P<version>.*)')
    with open(init_file, 'r', encoding='utf8') as f:
        match = _version_re.search(f.read())
        version = match.group('version') if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='pydot_ng',
    version=get_version(),
    description='Python interface to Graphviz\'s Dot',
    author='Ero Carrera',
    author_email='ero@dkbza.org',
    maintainer='Sebastian Kalinowski',
    maintainer_email='sebastian@kalinowski.eu',
    url="https://github.com/pydot/pydot-ng",
    license='MIT',
    keywords='graphviz dot graphs visualization',
    platforms=['any'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    long_description=readme,
    packages=['pydot_ng'],
    package_dir={'pydot_ng': 'pydot_ng'},
    install_requires=['pyparsing>=2.0.1'],
)
