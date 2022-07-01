# Copyright 2021 MathWorks, Inc.
"""
Array interface between Python and MATLAB.

This package defines classes and exceptions that create and manage
multidimensional arrays in Python that are passed between Python and MATLAB.
The arrays, while similar to Python sequences, have different behaviors.

Modules
-------
    * mlarray - type-specific multidimensional array classes for working
    with MATLAB, implemented in Python
    * mcpyarray - type-specific multidimensional array classes for working
    with MATLAB, implemented in C++
    * mlexceptions - exceptions raised when manipulating mlarray objects
"""

import os
import sys

# These can be removed once we no longer use _MiniPathInitializer.
import platform
import re

from pkgutil import extend_path
__path__ = extend_path(__path__, '__name__')

_package_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_package_folder)

# This code allows us to:
# (1) switch from a pure Python ("mlarray") to a C++ extension ("mcpyarray") 
# implementation by setting the environment variable USE_MCPYARRAY to 1
# (2) put the proper extern/bin/<arch> directory on the Python path to avoid 
# a situation in which some shared libraries are loaded from a MATLAB while
# others are loaded from a runtime. The first directory on the path that contains
# the string "bin/<arch>" (with the proper directory separator)
# will be checked. If it is "extern/bin/<arch>", it will be used as the
# extern/bin/<arch> directory. Otherwise, we'll go up two directories and down
# to extern/bin/<arch>.
class _MiniPathInitializer(object):
    PLATFORM_DICT = {'Windows': 'PATH', 'Linux': 'LD_LIBRARY_PATH', 'Darwin': 'DYLD_LIBRARY_PATH'}

    def __init__(self):
        self.arch = ''
        self.extern_bin_dir = ''
        self.path_var = ''
        self.system = ''
        self.use_mcpyarray = False
        if os.environ.get('USE_MCPYARRAY') and os.environ['USE_MCPYARRAY'] == '1':
            self.use_mcpyarray = True
            
    def get_platform_info(self):
        """Ask Python for the platform and architecture."""
        # This will return 'Windows', 'Linux', or 'Darwin' (for Mac).
        self.system = platform.system() 
        if not self.system in _MiniPathInitializer.PLATFORM_DICT:
            raise RuntimeError('{0} is not a supported platform.'.format(self.system))
        else:
            # path_var is the OS-dependent name of the path variable ('PATH', 'LD_LIBRARY_PATH', "DYLD_LIBRARY_PATH')
            self.path_var = _MiniPathInitializer.PLATFORM_DICT[self.system]

        if self.system == 'Windows':
            self.arch = 'win64'
        elif self.system == 'Linux':
            self.arch = 'glnxa64'
        elif self.system == 'Darwin':
            self.arch = 'maci64'
        else:
            raise RuntimeError('Operating system {0} is not supported.'.format(self.system))

    def is_extern_bin_on_py_sys_path(self):
        #Retrieve Python sys.path as a single string, and search for the substring "extern/bin/<arch>" (with
        #the proper directory separator). If it's already present, assume it's the one we want.
        substr_to_find = os.path.join('extern', 'bin', self.arch)
        for item in sys.path:
            if item.find(substr_to_find) != -1:
                return True
        return False
        
    def put_extern_bin_on_py_sys_path(self):
        """ 
        Look through the system path for the first directory ending with "runtime/<arch>" or
        "bin/<arch>" (with/without trailing slash). Use this to construct a new path ending 
        with "extern/bin/<arch>".
        """

        path_elements = []
        if self.path_var in os.environ:
            path_elements_orig = os.environ[self.path_var]
            # On Windows, some elements of the path may use forward slashes while others use backslashes. 
            # Make them all backslashes.
            if self.system == 'Windows':
                path_elements_orig = path_elements_orig.replace('/', '\\')
            path_elements = path_elements_orig.split(os.pathsep)
        if not path_elements:
            if self.system == 'Darwin':
                raise RuntimeError('On the Mac, you must run mwpython rather than python ' + 
                    'to start a session or script that imports your package. ' +
                    'For more details, execute "mwpython -help" or see the package documentation.')
            else:
                raise RuntimeError('On {0}, you must set the environment variable "{1}" to a non-empty string. {2}'.format(
                    self.system, self.path_var, 
                    'For more details, see the package documentation.'))

        dir_to_search = os.path.join('runtime', self.arch)
        trailing_substrings_to_find = [dir_to_search, dir_to_search + os.sep]

        dir_found = ''
        for elem in path_elements:
            for trailing_substring in trailing_substrings_to_find:
                if elem.endswith(trailing_substring):
                    dir_found = elem
                    break
            if dir_found:
                break

        if not dir_found:
            raise RuntimeError('Could not find an appropriate directory in {0} from which to read binaries.'.format(
                self.path_var))

        path_components = dir_found.split(os.sep)
        
        if path_components[-1]:
            last_path_component = path_components[-1]
            possible_extern = -3
        else:
            # The directory name ended with a slash, so the last item in the list was an empty string. Go back one more.
            last_path_component = path_components[-2]
            possible_extern = -4

        if last_path_component != self.arch:
            output_str = ''.join(('To call deployed MATLAB code on a {0} machine, you must run a {0} version of Python, ',
                'and your {1} variable must contain an element pointing to "<MR>{2}runtime{2}{0}", ',
                'where "<MR>" indicates a MATLAB or MATLAB Runtime root. ',
                'Instead, the value found was as follows: {3}'))
            raise RuntimeError(output_str.format(self.arch, self.path_var, os.sep, dir_found))

        if (len(path_components) + possible_extern) >= 0 and path_components[possible_extern] == 'extern':
            extern_bin_dir = dir_found
        else:
            mroot = os.path.dirname(os.path.dirname(os.path.normpath(dir_found)))
            extern_bin_dir = os.path.join(mroot, 'extern', 'bin', self.arch)
        if not os.path.isdir(extern_bin_dir):
            raise RuntimeError('Could not find the directory {0}'.format(extern_bin_dir))
        self.extern_bin_dir = extern_bin_dir
        sys.path.insert(0, self.extern_bin_dir)

_mpi = _MiniPathInitializer()
if _mpi.use_mcpyarray:
    _mpi.get_platform_info()
    if not _mpi.is_extern_bin_on_py_sys_path():
        _mpi.put_extern_bin_on_py_sys_path()
    from matlabmultidimarrayforpython import double, single, uint8, int8, uint16, \
        int16, uint32, int32, uint64, int64, logical, ShapeError, SizeError
else:
    from mlarray import double, single, uint8, int8, uint16, \
        int16, uint32, int32, uint64, int64, logical
    from mlexceptions import ShapeError as ShapeError
    from mlexceptions import SizeError as SizeError
