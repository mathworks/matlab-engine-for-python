# Copyright 2022-2023 Mathworks, Inc.

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
    MATLAB_REL = 'R2023a'

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    MATLAB_VER = '9.14.2'

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    SUPPORTED_PYTHON_VERSIONS = set(['3.8', '3.9', '3.10'])

    # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
    VER_TO_REL = {
        "9.9": "R2020b",
        "9.10": "R2021a",
        "9.11": "R2021b",
        "9.12": "R2022a",
        "9.13": "R2022b",
        "9.14": "R2023a"
    }

    DEFAULT_INSTALLS = {
        'Darwin': f"/Applications/MATLAB_{MATLAB_REL}.app",
        'Linux': f"/usr/local/MATLAB/{MATLAB_REL}"
    }

    arch = ''
    path_env_var_name = ''
    python_ver = ''
    platform = ''
    found_matlab_release = ''
    found_matlab_version = ''
    found_matlab_with_wrong_arch_in_default_install = ''
    found_matlab_with_wrong_arch_in_path = ''
    verbose = False
    
    # ERROR MESSAGES
    minimum_maximum = "No compatible version of MATLAB was found. " + \
        "Version {this_v:s} was found, but this feature only supports MATLAB {min_v:s} ({min_r:s}) through {max_v:s} ({max_r:s}), inclusive."
    dir_not_found = "Directory not found: "
    no_windows_install = "MATLAB installation not found in Windows Registry:"
    unsupported_platform = "{platform:s} is not a supported platform."
    unsupported_python = "{python:s} is not supported. The supported Python versions are {supported:s}."
    unset_env = "Environment variable {path1:s} has not been set. Add <matlabroot>/bin/{arch:s} to {path2:s}, where <matlabroot> is the root of a valid MATLAB installation."
    install_or_set_path = "MATLAB {ver:s} installation not found. Install to default location, or add <matlabroot>/bin/{arch:s} to {path:s}, where <matlabroot> is the root of a MATLAB {ver:s} installation."
    no_compatible_matlab = "No compatible MATLAB installation found in Windows Registry. This release of " + \
        "MATLAB Engine API for Python is compatible with version {ver:s}. The found versions were"
    no_matlab = "No compatible MATLAB installation found in Windows Registry."
    incompatible_ver = "MATLAB version {ver:s} ({rel:s}) was found, but this release of MATLAB Engine API for Python is not compatible with it. " + \
        "To install a compatible version, call 'python -m pip install matlabengine=={ver:s}'."
    invalid_version_from_matlab_ver = "Format of MATLAB version '{ver:s}' is invalid."
    invalid_version_from_eng = "Format of MATLAB Engine API version '{ver:s}' is invalid."
    next_steps = "Reinstall MATLAB, use DYLD_LIBRARY_PATH to specify a different MATLAB installation, or use a different Python interpreter."
    wrong_arch_in_default_install = "MATLAB installation in {path1:s} is {matlab_arch:s}, but Python interpreter is {python_arch:s}. {next_steps:s}."
    wrong_arch_in_path = "MATLAB installation in {path1:s}, listed in DYLD_LIBRARY_PATH, is {matlab_arch:s}, but Python interpreter is {python_arch:s}. {next_steps:s}."
    
    def _print_if_verbose(self, msg):
        if self.verbose:
            print(msg)
            
    def set_platform_and_arch(self):
        """
        Sets the platform and architecture. 
        """
        self.platform = platform.system()
        if self.platform not in self.PLATFORM_DICT:
            raise RuntimeError(self.unsupported_platform.format(platform=self.platform))
        else:
            self.path_env_var_name = self.PLATFORM_DICT[self.platform]
        
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
        if not os.path.exists(path):
            return False
        
        if self.platform == 'Darwin':
            # On Mac, we need to further verify that there is a 'bin/maci64' subdir if the Python is maci64
            # or a 'bin/maca64' subdir if the Python is maca64.
            path_to_bin = os.path.join(path, 'bin', self.arch)
            if os.path.exists(path_to_bin):
                # The path exists, and we don't need to do anything further.
                return True
                
            if self.arch == 'maci64':
                alternate_arch = 'maca64'
            else:
                alternate_arch = 'maci64'
                
            if os.path.exists(os.path.join(path, 'bin', alternate_arch)):
                # There is a default install, but its arch doesn't match the Python arch. Save this info
                # so that if we don't find an install with a valid arch in DYLD_LIBRARY_PATH, we can
                # issue an error message that says that there is a Mac installation in the default 
                # location that has the wrong arch. The user can choose whether to change the
                # Python interpreter or the MATLAB installation so that the arch will match.
                self.found_matlab_with_wrong_arch_in_default_install = path
                return False
                
        return True
    
    def _create_path_list(self):
        """
        Creates a list of directories on the path to be searched.
        """
        path_dirs = []
        path_string = ''
        if self.path_env_var_name in os.environ:
            path_string = os.environ[self.path_env_var_name]
            path_dirs.extend(path_string.split(os.pathsep))
        
        if not path_dirs:
            raise RuntimeError(self.install_or_set_path.format(
                ver=self.MATLAB_REL, arch=self.arch, 
                    path=self.path_env_var_name))
                    
        self._print_if_verbose(f'_create_path_list returned: {path_dirs}')
        return path_dirs
    
    def _get_alternate_arch(self):
        if self.arch == 'maci64':
            return 'maca64'
        if self.arch == 'maca64':
            return 'maci64'
        return self.arch

    def _arch_in_mac_dir_is_correct(self, dir):
        ARCH_LEN = 6 # == len('maci64') or len('maca64')
        BIN_ARCH_LEN = ARCH_LEN + 4 # == len('bin/maci64') or len('bin/maca64')
        
        if len(dir) < BIN_ARCH_LEN:
            return False
        
        if dir[-1] == os.sep:
            # It's safe to look at dir[[-1 * (ARCH_LEN+1)] because BIN_ARCH_LEN > ARCH_LEN + 1.
            possible_arch = dir[-1 * (ARCH_LEN+1) : -1]
        else:
            possible_arch = dir[-1 * ARCH_LEN :]
        
        self._print_if_verbose(f'possible_arch: {possible_arch}; self.arch: {self.arch}')
        if possible_arch == self.arch:
            return True
        else:
            return False            
            
    def _get_matlab_root_from_unix_bin(self, dir):
        """
        Searches bin directory for presence of MATLAB file. Used only for
        UNIX systems. 
        """
        matlab_path = os.path.join(dir, 'MATLAB')
        possible_root = os.path.normpath(os.path.join(dir, os.pardir, os.pardir))
        matlab_root = ''
        if os.path.isfile(matlab_path) and self.verify_matlab_release(possible_root):
            if self.platform == 'Darwin' and not self._arch_in_mac_dir_is_correct(dir):
                self.found_matlab_with_wrong_arch_in_path = possible_root
                self._print_if_verbose(f'self.found_matlab_with_wrong_arch_in_path: {self.found_matlab_with_wrong_arch_in_path}')
            else:
                matlab_root = possible_root
        self._print_if_verbose(f'_get_matlab_root_from_unix_bin returned: {matlab_root}')
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
        ret = self._get_root_from_version_key(reg, matlab_ver_key)
        self._print_if_verbose(f'get_matlab_root_from_windows_reg returned: {ret}')
        return ret
    
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
        
        self._print_if_verbose(f'_get_root_from_version_key returned: {matlab_root}')
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
                eng_ver_major_minor = self._get_engine_ver_major_minor(self.MATLAB_VER)
                eng_ver_major_minor_as_str = '{}.{}'.format(eng_ver_major_minor[0], eng_ver_major_minor[1])
                raise RuntimeError(f"{self.no_compatible_matlab.format(ver=eng_ver_major_minor_as_str)} {vers}.")
            else:
                raise RuntimeError(f"{self.no_matlab}")

        self._print_if_verbose(f'_find_matlab_key_from_windows_registry returned: {key_value}')
        return key_value       

    def _get_engine_ver_major_minor(self, id):
        re_major_minor = "^(\d+)\.(\d+)"
        eng_match = re.match(re_major_minor, id)
        if not eng_match:
            raise RuntimeError(f"{self.invalid_version_from_eng.format(ver=self.MATLAB_VER)}")
        ret = (eng_match.group(1), eng_match.group(2))
        self._print_if_verbose(f'_get_engine_ver_major_minor returned: {ret}')
        return ret
        
    def _check_matlab_ver_against_engine(self, matlab_ver):
        re_major_minor = "^(\d+)\.(\d+)"
        matlab_ver_match = re.match(re_major_minor, matlab_ver)
        if not matlab_ver_match:
            raise RuntimeError(f"{self.invalid_version_from_matlab_ver.format(ver=matlab_ver)}")
        eng_major_minor = self._get_engine_ver_major_minor(self.MATLAB_VER)
        matlab_ver_major_minor = (matlab_ver_match.group(1), matlab_ver_match.group(2))
        return (matlab_ver_major_minor == eng_major_minor)
    
    def verify_matlab_release(self, root):
        """
        Parses VersionInfo.xml to verify that the MATLAB release matches the supported release
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
                matlab_release = self.found_matlab_release = child.text
            elif child.tag == 'version':
                major, minor = self._get_engine_ver_major_minor(child.text)
                self.found_matlab_version = f'{major}.{minor}'
        return matlab_release == self.MATLAB_REL

    def search_path_for_directory_unix(self, arch, path_dirs):
        """
        Used for finding MATLAB root in UNIX systems. Searches all paths ending in
        /bin/<arch> for the presence of MATLAB file to ensure the path is within
        the MATLAB tree. 
        """
        dir_to_find = os.path.join('bin', arch)
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
        self._print_if_verbose(f'search_path_for_directory_unix returned: {matlab_root}')
        return matlab_root
    
    def _err_msg_if_bad_matlab_root(self, matlab_root):
        if not matlab_root:
            if self.found_matlab_version:
                self._print_if_verbose(f'self.found_matlab_version: {self.found_matlab_version}; self.VER_TO_REL: {self.VER_TO_REL}')
                if self.found_matlab_version in self.VER_TO_REL:
                    return self.incompatible_ver.format(ver=self.found_matlab_version, rel=self.found_matlab_release)
                # Found a MATLAB release but it is older than the oldest version supported,
                # or newer than the newest version supported.
                else:
                    v_to_r_keys = list(self.VER_TO_REL.keys())
                    self._print_if_verbose(f'v_to_r_keys: {v_to_r_keys}')
                    min_v = v_to_r_keys[0]
                    min_r = self.VER_TO_REL[min_v]
                    max_v = v_to_r_keys[-1]
                    max_r = self.VER_TO_REL[max_v]
                    return self.minimum_maximum.format(this_v=self.found_matlab_release, min_v=min_v, min_r=min_r, max_v=max_v, max_r=max_r)
            else:
                # If we reach this line, we assume that the default location has already been checked for an
                # appropriate MATLAB installation but none was found.
                return self.install_or_set_path.format(ver=self.MATLAB_REL, arch=self.arch, 
                    path=self.path_env_var_name)
        
        if not os.path.isdir(matlab_root):
            return f"{self.dir_not_found} {matlab_root}"
            
        return ''
        
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
            root_file.write(engine_arch + '\n')
            root_file.write(extern_bin)

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
                path_dirs = self._create_path_list()
                matlab_root = self.search_path_for_directory_unix(self.arch, path_dirs)
            err_msg = self._err_msg_if_bad_matlab_root(matlab_root)
            if err_msg:
                if self.platform == 'Darwin':
                    if self.found_matlab_with_wrong_arch_in_default_install:
                        raise RuntimeError(
                            self.wrong_arch_in_default_install.format(
                                path1=self.found_matlab_with_wrong_arch_in_default_install,
                                matlab_arch=self._get_alternate_arch(),
                                python_arch=self.arch,
                                next_steps=self.next_steps))
                    if self.found_matlab_with_wrong_arch_in_path:
                        raise RuntimeError(
                            self.wrong_arch_in_path.format(
                                path1=self.found_matlab_with_wrong_arch_in_path,
                                matlab_arch=self._get_alternate_arch(),
                                python_arch=self.arch,
                                next_steps=self.next_steps))
                raise RuntimeError(err_msg)

        self.write_text_file(matlab_root)
        build_py.run(self)


if __name__ == '__main__':
    with open('README.md', 'r', encoding='utf-8') as rm:
        long_description = rm.read()

    setup(
        name="matlabengine",
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        version="9.14.2",
        description='A module to call MATLAB from Python',
        author='MathWorks',
        license="MathWorks XSLA License",
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
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10"
        ],
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        python_requires=">=3.8, <3.11"
    )
