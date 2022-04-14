# Copyright 2022 MathWorks, Inc.

import os
import platform
import sys
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)
package_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(package_folder)

def add_dirs_to_path(bin_dir, engine_dir, extern_dir):
        """
        Adds MATLAB engine and extern/bin directories to sys.path.
        """
        path = 'PATH'

        if not os.path.isdir(engine_dir):
            raise RuntimeError("Could not find directory: {0}".format(engine_dir))
        
        if not os.path.isdir(extern_dir):
            raise RuntimeError("Could not find directory: {0}".format(extern_dir))
        
        if platform.system() == 'Windows':
            if not os.path.isdir(bin_dir):
                raise RuntimeError("Could not find directory: {0}".format(bin_dir))
            if path in os.environ:
                paths = os.environ[path]
                os.environ[path] = bin_dir + os.pathsep + paths
            else:
                os.environ[path] = bin_dir
            if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
                os.add_dll_directory(bin_dir)

        sys.path.insert(0, engine_dir)
        sys.path.insert(0, extern_dir)

arch_file = os.path.join(package_folder, 'engine', '_arch.txt')
if not os.path.isfile(arch_file):
    raise RuntimeError("The MATLAB Engine for Python install is corrupted, please try to re-install.")

with open(arch_file, 'r') as root:
    [arch, bin_folder, engine_folder, extern_bin] = [line.strip() for line in root.readlines()]


add_dirs_to_path(bin_folder, engine_folder, extern_bin)

from matlabmultidimarrayforpython import double, single, uint8, int8, uint16, \
    int16, uint32, int32, uint64, int64, logical, ShapeError, SizeError
