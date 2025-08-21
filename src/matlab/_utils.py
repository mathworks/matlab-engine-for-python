import functools
import os
import platform
import shutil
from typing import Optional, NamedTuple


def _get_platform_arch() -> str:
    system_name = platform.system()
    
    if system_name == 'Windows':
        return 'win64'
    if system_name == 'Linux':
        return 'glnxa64'
    if system_name == 'Darwin':
        if platform.mac_ver()[-1] == 'arm64':
            return 'maca64'
        return 'maci64'

    raise RuntimeError(f"{system_name} is not a supported platform.")


def _get_matlab_root() -> Optional[str]:
    """Probe matlab root directory"""
    matlab_command = shutil.which('matlab')
    if not matlab_command:
        return None
    matlab_bin_dir = os.path.dirname(matlab_command)
    matlab_root = os.path.normpath(os.path.join(matlab_bin_dir, os.pardir))
    return matlab_root


class MatlabPathInfo(NamedTuple):
    arch: str
    bin_folder: str
    engine_folder: str
    extern_bin: str


@functools.cache
def get_path_info() -> MatlabPathInfo:
    package_folder = os.path.dirname(os.path.realpath(__file__))
    arch_file = os.path.join(package_folder, 'engine', '_arch.txt')
    if os.path.isfile(arch_file):
        with open(arch_file, 'r') as root:
           [arch, bin_folder, engine_folder, extern_bin] = [line.strip() for line in root.readlines() if line.strip()]
           return MatlabPathInfo(arch, bin_folder, engine_folder, extern_bin)

    matlab_root = _get_matlab_root()
    if matlab_root:
        arch = _get_platform_arch()
        bin_folder = os.path.join(matlab_root, 'bin', arch)
        engine_folder = os.path.join(matlab_root, 'extern', 'engines', 'python', 'dist', 'matlab', 'engine', arch)
        extern_bin = os.path.join(matlab_root, 'extern', 'bin', arch)
        if os.path.isdir(bin_folder) and os.path.isdir(engine_folder) and os.path.isdir(extern_bin):
            return MatlabPathInfo(arch, bin_folder, engine_folder, extern_bin)

    raise RuntimeError("The MATLAB Engine for Python install is corrupted or matlab is not available. Please try to re-install.")
