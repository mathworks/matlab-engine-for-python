# Copyright 2014-2015 MathWorks, Inc.
"""
Array interface between Python and MATLAB.

This package defines classes and exceptions that create and manage
multidimensional arrays in Python that are passed between Python and MATLAB.
The arrays, while similar to Python sequences, have different behaviors.

Modules
-------
    * mlarray - type-specific multidimensional array classes for working
    with MATLAB
    * mlexceptions - exceptions raised manipulating mlarray objects
"""

import os
import sys
from pkgutil import extend_path
__path__ = extend_path(__path__, '__name__')

_package_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_package_folder)

from mlarray import double, single, uint8, int8, uint16, \
    int16, uint32, int32, uint64, int64, logical
from mlexceptions import ShapeError as ShapeError
from mlexceptions import SizeError as SizeError
