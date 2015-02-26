pydot - Python interface to Graphviz's Dot language
---------------------------------------------------
Ero Carrera (c) 2004-2007

ero@dkbza.org

This code is distributed under the MIT license.

.. image:: https://travis-ci.org/pydot/pydot-ng.svg?branch=master
    :target: https://travis-ci.org/pydot/pydot-ng


Requirements:
=============

pyparsing: pydot requires the pyparsing module in order to be
	able to load DOT files.

GraphViz:  is needed in order to render the graphs into any of
	the plethora of output formats supported.

Installation:
=============

Should suffice with doing:

 python setup.py install

Needless to say, no installation is needed just to use the module. A mere:

 import pydot_ng

should do it, provided that the directory containing the modules is on Python
module search path.

This library is API compatible with original pydot so you can use it like this:

 import pydot_ng as pydot
