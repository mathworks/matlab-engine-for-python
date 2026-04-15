# Copyright 2021-2025 MathWorks, Inc.
"""
Array interface between Python and MATLAB

This package defines classes and exceptions that create and manage
multidimensional arrays in Python that are passed between Python and MATLAB.

Modules
-------
    * mcpyarray - type-specific multidimensional array classes for working
    with MATLAB, implemented in C++
"""

import os
import platform
import sys
import warnings
from pkgutil import extend_path
__path__ = extend_path(__path__, '__name__')

_package_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_package_folder)

# This code allows us to put the proper extern/bin/<arch> directory on the Python path 
# to avoid a situation in which some shared libraries are loaded from a MATLAB while
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
            # determine ARM or Intel Mac machine
            if platform.mac_ver()[-1] == 'arm64':
                self.arch = 'maca64'
            else:
                self.arch = 'maci64'
        else:
            raise RuntimeError('Operating system {0} is not supported.'.format(self.system))

    def get_extern_bin_from_path_element_ending_with_runtime_arch(self, dir_found):
        extern_bin_dir = ''
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
            
        return extern_bin_dir

    def get_extern_bin_from_py_sys_path(self):
        #Retrieve Python sys.path as a single string, and search for the substring "extern/bin/<arch>" (with
        #the proper directory separator). If it's already present, assume it's the one we want.
        substr_to_find = os.path.join('extern', 'bin', self.arch)
        for item in sys.path:
            if item.find(substr_to_find) != -1:
                return item
        return ''
        
    def put_extern_bin_on_py_sys_path(self):
        """ 
        Look through the system path for the first directory ending with "runtime/<arch>" or
        "bin/<arch>" (with/without trailing slash). Use this to construct a new path ending 
        with "extern/bin/<arch>".
        """

        path_elements = []
        path_elements_orig = ''
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

        extern_bin_dir = ''
        for elem in path_elements:
            for trailing_substring in trailing_substrings_to_find:
                if elem.endswith(trailing_substring):
                    extern_bin_dir = self.get_extern_bin_from_path_element_ending_with_runtime_arch(elem)
                    if extern_bin_dir:
                        break

        if not extern_bin_dir:
            format_str = 'Could not find an appropriate directory in {0} from which to read binaries. Details::\n{1}'
            raise RuntimeError(format_str.format(self.path_var, path_elements_orig))
        
        if not os.path.isdir(extern_bin_dir):
            raise RuntimeError('Could not find the directory {0}'.format(extern_bin_dir))
        self.extern_bin_dir = extern_bin_dir
        sys.path.insert(0, self.extern_bin_dir)

def get_python_version():
    # UPDATE_IF_PYTHON_VERSION_ADDED_OR_REMOVED : search for this string in codebase 
    # when support for a Python version must be added or removed
    _supported_versions = ['3_9', '3_10', '3_11', '3_12', '3_13']
    _ver = sys.version_info
    _version = '{0}_{1}'.format(_ver[0], _ver[1])  
    newer_than_supported = _ver[1] > 12  

    _PYTHONVERSION = None

    if _version in _supported_versions:
        _PYTHONVERSION = _version
    elif newer_than_supported:
        warnings.warn('Python versions 3.9, 3.10, 3.11, 3.12, and 3.13 are supported, but your version of Python is %s' % _version)
        _PYTHONVERSION = _version  
    else:
        raise EnvironmentError("Python %s is not supported." % _version)

    return _PYTHONVERSION

def get_arch_filename():
    _module_folder = os.path.dirname(os.path.realpath(__file__))
    _arch_filename = os.path.join(_module_folder, 'engine', '_arch.txt')
    return _arch_filename

def add_dll_dir_on_win(arch, dir_to_add):
    if arch == 'win64':
        if not dir_to_add:
            raise RuntimeError('Cannot add empty DLL directory')
        os.add_dll_directory(dir_to_add)
    
def get_dirs_from_arch_file_without_import():
    _PYTHONVERSION = get_python_version()
    _arch_filename = get_arch_filename()
    firstExceptionMessage = ''
    if not os.path.isfile(_arch_filename):
        return False

    try:
        _arch_file = open(_arch_filename,'r')
        _lines = _arch_file.readlines()
        [_arch, _bin_dir,_engine_dir, _extern_bin_dir] = [x.rstrip() for x in _lines if x.rstrip() != ""]
        _arch_file.close()
        sys.path.insert(0,_engine_dir)
        sys.path.insert(0,_extern_bin_dir)
        add_dll_dir_on_win(_arch, _bin_dir)
    except Exception as exc:
        firstExceptionMessage = 'Please contact MathWorks Technical Support for assistance:\nDetails: {}'.format(
            exc)
                
    if firstExceptionMessage:
        return False
    else:    
        return True

def subdir_exists(folder_name, subfolder_name):
    return os.path.exists(os.path.join(folder_name, subfolder_name))


_mpi = _MiniPathInitializer()
_mpi.get_platform_info()
extern_bin_dir = ''
if subdir_exists(_package_folder, 'engine'):
    success = get_dirs_from_arch_file_without_import()
    if not success:
        if 'MWE_INSTALL' in os.environ:
            mroot_from_env_var = os.environ['MWE_INSTALL']
            extern_bin_dir = os.path.join(mroot_from_env_var, 'extern', 'bin', _mpi.arch)
            if not os.path.exists(extern_bin_dir):
                raise RuntimeError('directory {} does not exist'.format(extern_bin_dir))
            sys.path.insert(0, extern_bin_dir)
            bin_dir = extern_bin_dir.replace('extern' + os.sep + 'bin', 'bin')
            add_dll_dir_on_win(_mpi.arch, bin_dir)
        else:
            raise RuntimeError('unable to read {}'.format(get_arch_filename()))
else:
    extern_bin_dir = _mpi.get_extern_bin_from_py_sys_path()
    if not extern_bin_dir:
        _mpi.put_extern_bin_on_py_sys_path()
        extern_bin_dir = _mpi.extern_bin_dir

    bin_dir = extern_bin_dir.replace('extern' + os.sep + 'bin', 'bin')
    add_dll_dir_on_win(_mpi.arch, bin_dir)
        
        
from matlabmultidimarrayforpython import double, single, uint8, int8, uint16, \
    int16, uint32, int32, uint64, int64, logical, ShapeError, SizeError

