# Copyright 2022 Mathworks, Inc.

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py 
import os
import re
import sys
import platform
import xml.etree.ElementTree as xml
if platform.system() == 'Windows':
    import winreg

class _MatlabFinder(build_py):
    """
    Private class that finds MATLAB on user's computer prior to package installation.
    """
    PLATFORM_DICT = {
        'Windows': 'PATH', 
        'Linux': 'LD_LIBRARY_PATH', 
        'Darwin': 'DYLD_LIBRARY_PATH'
    }
    
    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    MATLAB_REL = 'R2020b'

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    MATLAB_VER = '9.9.5' 

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    SUPPORTED_PYTHON_VERSIONS = set(['3.6', '3.7', '3.8'])

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    VER_TO_REL = {
        "9.9": "R2020b",
        "9.10": "R2021a",
        "9.11": "R2021b",
        "9.12": "R2022a",
        "9.13": "R2022b"
    }

    DEFAULT_INSTALLS = {
        'Darwin': f"/Applications/MATLAB_{MATLAB_REL}.app",
        'Linux': f"/usr/local/MATLAB/{MATLAB_REL}"
    }

    arch = ''
    path_name = ''
    python_ver = ''
    platform = ''
    found_matlab = ''

    # ERROR MESSAGES
    minimum_maximum = "No compatible version of MATLAB was found. " + \
        "This feature supports MATLAB {min_v:s} ({min_r:s}) through {max_v:s} ({max_r:s}), inclusive."
    dir_not_found = "Directory not found: "
    no_windows_install = "MATLAB installation not found in Windows Registry:"
    unsupported_platform = "{platform:s} is not a supported platform."
    unsupported_python = "{python:s} is not supported. The supported Python versions are {supported:s}."
    unset_env = "Environment variable {path1:s} has not been set. Add <matlabroot>/bin/{arch:s} to {path2:s}, where <matlabroot> is the root of a valid MATLAB installation."
    set_path = "MATLAB installation not found in {path1:s}. Add <matlabroot>/bin/{arch:s} to {path2:s}, where <matlabroot> is the root of a valid MATLAB installation."
    no_compatible_matlab = "No compatible MATLAB installation found in Windows Registry. This release of " + \
        "MATLAB Engine API for Python is compatible with version {ver:s}. The found versions were"
    no_matlab = "No compatible MATLAB installation found in Windows Registry."
    incompatible_ver = "MATLAB version {ver:s} was found, but MATLAB Engine API for Python is not compatible with it. " + \
        "To install a compatible version, call python -m pip install matlabengine=={found:s}."
    invalid_version_from_matlab_ver = "Format of MATLAB version '{ver:s}' is invalid."
    invalid_version_from_eng = "Format of MATLAB Engine API version '{ver:s}' is invalid."
    
    def set_platform_and_arch(self):
        """
        Sets the platform and architecture. 
        """
        self.platform = platform.system()
        if self.platform not in self.PLATFORM_DICT:
            raise RuntimeError(self.unsupported_platform.format(platform=self.platform))
        else:
            self.path_name = self.PLATFORM_DICT[self.platform]
        
        if self.platform == 'Windows':
            self.arch = 'win64'
        elif self.platform == 'Linux':
            self.arch = 'glnxa64'
        elif self.platform == 'Darwin':
            if platform.mac_ver()[-1] == 'arm64':
                self.arch = 'maca64'
            else:
                self.arch = 'maci64'
        else:
            raise RuntimeError(self.unsupported_platform.format(platform=self.platform))
    
    def set_python_version(self):
        """
        Gets Python version and ensures it is supported.
        """
        ver = sys.version_info
        self.python_ver = f"{ver.major}.{ver.minor}"

        if self.python_ver not in self.SUPPORTED_PYTHON_VERSIONS:
            raise RuntimeError(self.unsupported_python.format(python=self.python_ver, supported=str(self.SUPPORTED_PYTHON_VERSIONS)))

    def unix_default_install_exists(self):
        """
        Determines whether MATLAB is installed in default UNIX location.
        """
        path = self.DEFAULT_INSTALLS[self.platform]
        return os.path.exists(path)
    
    def _create_path_list(self):
        """
        Creates a list of directories on the path to be searched.
        """
        path_dirs = []
        path_string = ''
        if self.path_name in os.environ:
            path_string = os.environ[self.path_name]
            path_dirs.extend(path_string.split(os.pathsep))
        
        if not path_dirs:
            raise RuntimeError(self.unset_env.format(path1=self.path_name, arch=self.arch, path2=self.path_name))
        
        return path_dirs
    
    def _get_matlab_root_from_unix_bin(self, dir):
        """
        Searches bin directory for presence of MATLAB file. Used only for
        UNIX systems. 
        """
        matlab_path = os.path.join(dir, 'MATLAB')
        possible_root = os.path.normpath(os.path.join(dir, os.pardir, os.pardir))
        matlab_root = ''
        if os.path.isfile(matlab_path) and self.verify_matlab_release(possible_root):
            matlab_root = possible_root
            
        return matlab_root
    
    def get_matlab_root_from_windows_reg(self):
        """
        Searches Windows Registry for MATLAB installs and gets the root directory of MATLAB.
        """
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, "SOFTWARE\\MathWorks\\MATLAB")
        except OSError as err:
            raise RuntimeError(f"{self.no_windows_install} {err}")
        
        matlab_ver_key = self._find_matlab_key_from_windows_registry(key)
        return self._get_root_from_version_key(reg, matlab_ver_key)
    
    def _get_root_from_version_key(self, reg, ver_key):
        """
        Opens a registry corresponding to the version of MATLAB specified and queries for
        MATLABROOT.
        """
        try:
            key = winreg.OpenKey(reg, "SOFTWARE\\MathWorks\\MATLAB\\" + ver_key)
            matlab_root = winreg.QueryValueEx(key, "MATLABROOT")[0]
        except (OSError, FileNotFoundError) as err:
            raise RuntimeError(f"{self.no_windows_install} {err}")
        
        return matlab_root
    
    def _find_matlab_key_from_windows_registry(self, key):
        """
        Searches the MATLAB folder in Windows registry for the specified version of MATLAB. When found, 
        the MATLAB root directory will be returned.
        """
        # QueryInfoKey returns a tuple, index 0 is the number of sub keys we need to search
        num_keys = winreg.QueryInfoKey(key)[0]
        key_value = ''
        found_vers = []
        for idx in range(num_keys):
            sub_key = winreg.EnumKey(key, idx)
            if sub_key in self.VER_TO_REL:
                found_vers.append(sub_key)
                # Example: the version in the registry could be "9.X" whereas the version in this file could be "9.X.Y".
                # We want to allow this.
                if self._check_matlab_ver_against_engine(sub_key):
                    key_value = sub_key
                    break
        
        if not key_value:
            if found_vers:
                vers = ', '.join(found_vers)
                eng_ver_major_minor = self._get_engine_ver_major_minor()
                eng_ver_major_minor_as_str = '{}.{}'.format(eng_ver_major_minor[0], eng_ver_major_minor[1])
                raise RuntimeError(f"{self.no_compatible_matlab.format(ver=eng_ver_major_minor_as_str)} {vers}.")
            else:
                raise RuntimeError(f"{self.no_matlab}")

        return key_value       

    def _get_engine_ver_major_minor(self):
        re_major_minor = "^(\d+)\.(\d+)"
        eng_match = re.match(re_major_minor, self.MATLAB_VER)
        if not eng_match:
            raise RuntimeError(f"{self.invalid_version_from_eng.format(ver=self.MATLAB_VER)}")
        return (eng_match.group(1), eng_match.group(2))
        
    def _check_matlab_ver_against_engine(self, matlab_ver):
        re_major_minor = "^(\d+)\.(\d+)"
        matlab_ver_match = re.match(re_major_minor, matlab_ver)
        if not matlab_ver_match:
            raise RuntimeError(f"{self.invalid_version_from_matlab_ver.format(ver=matlab_ver)}")
        eng_major_minor = self._get_engine_ver_major_minor()
        matlab_ver_major_minor = (matlab_ver_match.group(1), matlab_ver_match.group(2))
        return (matlab_ver_major_minor == eng_major_minor)
    
    def verify_matlab_release(self, root):
        """
        Parses VersionInfo.xml to verify the MATLAB release matches the supported release
        for the Python Engine.
        """
        version_info = os.path.join(root, 'VersionInfo.xml')
        if not os.path.isfile(version_info):
            return False
        
        tree = xml.parse(version_info)
        tree_root = tree.getroot()

        matlab_release = ''
        for child in tree_root:
            if child.tag == 'release':
                matlab_release = self.found_matlab = child.text
                break
        return matlab_release == self.MATLAB_REL

    def search_path_for_directory_unix(self):
        """
        Used for finding MATLAB root in UNIX systems. Searches all paths ending in
        /bin/<arch> for the presence of MATLAB file to ensure the path is within
        the MATLAB tree. 
        """
        path_dirs = self._create_path_list()
        dir_to_find = os.path.join('bin', self.arch)
        # directory could end with slashes
        endings = [dir_to_find, dir_to_find + os.sep]

        matlab_root = ''
        dir_idx = 0
        while not matlab_root and dir_idx < len(path_dirs):
            path = path_dirs[dir_idx]
            ending_idx = 0
            while not matlab_root and ending_idx < len(endings):
                ending = endings[ending_idx]
                if path.endswith(ending):
                    # _get_matlab_root_from_unix_bin will return an empty string if MATLAB is not found.
                    # Non-empty string (MATLAB found) will break both loops.
                    matlab_root = self._get_matlab_root_from_unix_bin(path)
                ending_idx += 1
            dir_idx += 1
        
        if not matlab_root:
            if self.found_matlab:
                if self.found_matlab in self.VER_TO_REL:
                    raise RuntimeError(self.incompatible_ver.format(ver=self.VER_TO_REL[self.found_matlab], found=self.found_matlab))
                # We found a MATLAB release but it is older than the oldest version we support,
                # or newer than the newest version we support.
                else:
                    v_to_r_keys = list(self.VER_TO_REL.keys())
                    min_v = v_to_r_keys[0]
                    min_r = self.VER_TO_REL[min_v]
                    max_v = v_to_r_keys[-1]
                    max_r = self.VER_TO_REL[max_v]
                    raise RuntimeError(self.minimum_maximum.format(min_v=min_v, min_r=min_r, max_v=max_v, max_r=max_r))
            else:
                raise RuntimeError(self.set_path.format(path1=self.path_name, arch=self.arch, path2=self.path_name))
        
        if not os.path.isdir(matlab_root):
            raise RuntimeError(f"{self.dir_not_found} {matlab_root}")
        return matlab_root
    
    def write_text_file(self, matlab_root):
        """
        Writes root.txt for use at import time.
        """
        file_location = os.path.join(os.getcwd(), 'src', 'matlab', 'engine', '_arch.txt')
        bin_arch = os.path.join(matlab_root, 'bin', self.arch)
        engine_arch = os.path.join(matlab_root, 'extern', 'engines', 'python', 'dist', 'matlab', 'engine', self.arch)
        extern_bin = os.path.join(matlab_root, 'extern', 'bin', self.arch)
        with open(file_location, 'w') as root_file:
            root_file.write(self.arch + '\n')
            root_file.write(bin_arch + '\n')
            root_file.write(engine_arch)

    def run(self):
        """
        Logic that runs prior to installation.
        """
        self.set_platform_and_arch()
        self.set_python_version()

        if self.platform == 'Windows':
            matlab_root = self.get_matlab_root_from_windows_reg()
        else:
            if self.unix_default_install_exists():
                matlab_root = self.DEFAULT_INSTALLS[self.platform]
            else:
                matlab_root = self.search_path_for_directory_unix()
        self.write_text_file(matlab_root)
        build_py.run(self)


if __name__ == '__main__':
    with open('README.md', 'r', encoding='utf-8') as rm:
        long_description = rm.read()

    setup(
        name="matlabengine",
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        version="9.9.5",
        description='A module to call MATLAB from Python',
        author='MathWorks',
        license="LICENSE.txt, located in this repository",
        url='https://github.com/mathworks/matlab-engine-for-python/',
        long_description=long_description,
        long_description_content_type="text/markdown",
        package_dir={'': 'src'},
        packages=find_packages(where="src"),
        cmdclass={'build_py': _MatlabFinder},
        package_data={'': ['_arch.txt']},
        zip_safe=False,
        project_urls={
            'Documentation': 'https://www.mathworks.com/help/matlab/matlab-engine-for-python.html',
            'Source': 'https://github.com/mathworks/matlab-engine-for-python',
            'Tracker': 'https://github.com/mathworks/matlab-engine-for-python/issues'
        },
        keywords=[
            "MATLAB",
            "MATLAB Engine for Python"
        ],
        classifiers=[
            "Natural Language :: English",
            "Intended Audience :: Developers",
            # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8"
        ],
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        python_requires=">=3.6, <3.9"
    )
