# MATLAB Engine API for Python

The MATLAB&reg; Engine API for Python&reg; provides a package to integrate MATLAB functionality directly with a Python application, creating an interface to call functions from your MATLAB installation from Python code. 

---
## Requirements
### Required MathWorks Products
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
* MATLAB release R2023a

### Required 3rd Party Products
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
* Python 3.8, 3.9, or 3.10
    * Supported Python versions by MATLAB release can be found [here](https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/python-compatibility.pdf).

---

## Install

### Windows
MATLAB Engine API for Python can be installed directly from the Python Package Index.
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
```bash
$ python -m pip install matlabengine==9.14.2
```



### Linux&reg; 
Prior to installation, check the default install location of MATLAB by calling ```matlabroot``` in a MATLAB Command Window. By default, Linux installs MATLAB at:<br>
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
```/usr/local/MATLAB/R2023a```

When MATLAB is not installed in the default location, the bin/*architecture* directory within the MATLAB root directory must be added to an environment variable. The path can be added to the environment variable within the shell startup configuration file (for example, .bashrc for bash shell or .tcshrc for tcsh).

```bash
# in .bashrc
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<matlabroot>/bin/glnxa64
```

```bash
# in .tcshrc
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:<matlabroot>/bin/glnxa64
```

MATLAB Engine API for Python can be installed directly from the Python Package Index.
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
```bash
$ python -m pip install matlabengine==9.14.2
```

### macOS
Prior to installation, check the default install location of MATLAB by calling ```matlabroot``` in a MATLAB Command Window. By default, macOS installs MATLAB at:<br>

<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
```/Applications/MATLAB_R2023a.app```

When MATLAB is not installed in the default location, the bin/*architecture* directory within the MATLAB root directory must be added to an environment variable. The path can be added to the environment variable within the shell startup configuration file (for example, .bashrc for bash shell or .tcshrc for tcsh).

```bash
# in .bashrc
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<matlabroot>/bin/maci64
```

```bash
# in .tcshrc
setenv DYLD_LIBRARY_PATH ${DYLD_LIBRARY_PATH}:<matlabroot>/bin/maci64
```

MATLAB Engine API for Python can be installed directly from the Python Package Index.
<!-- MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string) -->
```bash
$ python -m pip install matlabengine==9.14.2
```

---

## Getting Started
* Start Python.
* Import the ```matlab.engine``` package into the Python session.
* Start a new MATLAB process by calling ```start_matlab```. The ```start_matlab``` function returns a Python object which enables you to pass data and call functions executed by MATLAB.

```python
>>> import matlab.engine
>>> eng = matlab.engine.start_matlab()
>>> eng.sqrt(4.0)
2.0
```

* Call either the ```exit``` or ```quit``` function to stop the engine. Exiting Python with an engine running stops the engine and its MATLAB processes.

```python
>>> eng.quit()
```

See [Start and Stop MATLAB Engine for Python](https://www.mathworks.com/help/matlab/matlab_external/start-the-matlab-engine-for-python.html) for advanced startup examples.

---

## Examples
You can call any MATLAB function directly and return the results to Python. 
```python
>>> eng.plus(2, 3)
5
>>> eng.isprime(37)
True
>>> eng.gcd(100.0, 80.0, nargout=3)
(20.0, 1.0, -1.0)
```
See [Call MATLAB Functions from Python](https://www.mathworks.com/help/matlab/matlab_external/call-matlab-functions-from-python.html) for more usage examples.

---

## Limitations
Limitations of the MATLAB Engine API for Python can be found [here](https://www.mathworks.com/help/matlab/matlab_external/limitations-to-the-matlab-engine-for-python.html).

---

## Troubleshooting
See [Troubleshoot MATLAB Errors in Python](https://www.mathworks.com/help/matlab/matlab_external/troubleshoot-matlab-errors-in-python.html) for troubleshooting assistance.

---

## License
This software is licensed under the MathWorks XSLA License, which is available in the LICENSE.txt file within this repository.

---

## Support
Technical issues or enhancement requests can be submitted [here](https://github.com/mathworks/matlab-engine-for-python/issues). 

---

Copyright &copy; 2022 MathWorks, Inc. All rights reserved.

Linux&reg; is the registered trademark of Linus Torvalds in the U.S. and other countries.

Mac OS is a trademark of Apple Inc., registered in the U.S. and other countries.

"Python" and the Python logos are trademarks or registered trademarks of the Python Software Foundation, used by MathWorks with permission from the Foundation.
