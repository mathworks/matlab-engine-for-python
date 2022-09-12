#Copyright 2014-2020 MathWorks, Inc.

"""
The MATLAB Engine enables you to call any MATLAB statement either synchronously
or asynchronously.  With synchronous execution, the invocation of a MATLAB
statement returns the result after the call finishes.  With asynchronous
execution, the invocation of a MATLAB statement is performed in the background 
and a FutureResult object is returned immediately.  You can call its "done" 
function to check if the call has finished, and its "result" function to obtain
 the actual result of the MATLAB statement.

This example shows how to call a MATLAB function:

>>> import matlab.engine
>>> eng = matlab.engine.start_matlab()
>>> eng.sqrt(4.0)
2.0
>>> eng.exit()
"""


import os
import sys
import importlib
import atexit
import weakref
import threading

# UPDATE_IF_PYTHON_VERSION_ADDED_OR_REMOVED : search for this string in codebase 
# when support for a Python version must be added or removed
_supported_versions = ['2_7', '3_7', '3_8']
_ver = sys.version_info
_version = '{0}_{1}'.format(_ver[0], _ver[1])
_PYTHONVERSION = None

if _version in _supported_versions:
    _PYTHONVERSION = _version
else:
    raise EnvironmentError("Python %s is not supported." % _version)

_module_folder = os.path.dirname(os.path.realpath(__file__))
_arch_filename = os.path.join(_module_folder, "_arch.txt")
 
try:
    pythonengine = importlib.import_module("matlabengineforpython"+_PYTHONVERSION)
except:
    try:
        _arch_file = open(_arch_filename,'r')
        _lines = _arch_file.readlines()
        [_arch, _bin_dir,_engine_dir, _extern_bin_dir] = [x.rstrip() for x in _lines if x.rstrip() != ""]
        _arch_file.close()
        sys.path.insert(0,_engine_dir)
        sys.path.insert(0,_extern_bin_dir)

        _envs = {'win32': 'PATH', 'win64': 'PATH'}
        if _arch in _envs:
            if _envs[_arch] in os.environ:
                _env = os.environ[_envs[_arch]]
                os.environ[_envs[_arch]] = _bin_dir + os.pathsep + os.environ[_envs[_arch]]
            else:
                os.environ[_envs[_arch]] = _bin_dir
            if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
                os.add_dll_directory(_bin_dir)
        pythonengine = importlib.import_module("matlabengineforpython"+_PYTHONVERSION)
    except Exception as e:
        raise EnvironmentError('Please reinstall MATLAB Engine for Python or contact '
                               'MathWorks Technical Support for assistance: %s' % e)


"""
This lock can make sure the global variable _engines is updated correctly in
multi-thread use case.  Also, it guarantees that only one MATLAB is launched
when connect_matlab() is called if there is no shared MATLAB session.
"""
_engine_lock = threading.RLock()
_engines = []

from matlab.engine.engineerror import RejectedExecutionError
from matlab.engine.basefuture import BaseFuture
from matlab.engine.matlabfuture import MatlabFuture
from matlab.engine.fevalfuture import FevalFuture
from matlab.engine.futureresult import FutureResult
from matlab.engine.enginesession import EngineSession
from matlab.engine.matlabengine import MatlabEngine
from matlab.engine.matlabengine import enginehelper

_session = EngineSession()

def start_matlab(option="-nodesktop", **kwargs):
    """
    Start the MATLAB Engine.  This function creates an instance of the
    MatlabEngine class.  The local version of MATLAB will be launched
    with the "-nodesktop" argument.

    Please note the invocation of this function is synchronous, which
    means it only returns after MATLAB launches.
    
    Parameters
        option - MATLAB startup option.
        async, background: bool - start MATLAB asynchronously or not.  This parameter
        is optional and false by default.  "async" is a synonym for "background"
        that will be removed in a future release.
                
    Returns
        MatlabEngine - if aync or background is false.  This object can be used to evaluate
        MATLAB statements.
        FutureResult - if async or background is true.  This object can be used to obtain the
        real MatlabEngine instance.

    Raises
        EngineError - if MATLAB can't be started.
    """
    if not isinstance(option, str):
        raise TypeError(pythonengine.getMessage('StartupOptionShouldBeStr'))
    
    background = enginehelper._get_async_or_background_argument(kwargs)
    future = FutureResult(option=option)
    if not background:
        #multi-threads cannot launch MATLAB simultaneously
        eng = future.result()
        return eng
    else:
        return future

def find_matlab():
    """
    Discover all shared MATLAB sessions on the local machine. This function 
    returns the names of all shared MATLAB sessions.

    Returns
        tuple - the names of all shared MATLAB sessions running locally.
    """
    engines = pythonengine.findMATLAB()
    return engines

def connect_matlab(name=None, **kwargs):
    """
    Connect to a shared MATLAB session.  This function creates an instance 
    of the MatlabEngine class and connects it to a MATLAB session. The MATLAB 
    session must be a shared session on the local machine. 

    If name is not specified and there is no shared MATLAB available, this 
    function launches a shared MATLAB session with default options. If name 
    is not specified and there are shared MATLAB sessions available, the first 
    shared MATLAB created is connected.  If name is specified and there are no 
    shared MATLAB sessions with that name, an exception is raised. 

    Parameters 
        name: str - the name of the shared MATLAB session, which is optional.
        By default it is None.
        async, background: bool - connect to the shared MATLAB session asynchronously or
        not.  This is optional and false by default.  "async" is a synonym for 
        "background" that will be removed in a future release.

    Returns
        MatlabEngine - if async or background is false.  This object can be used to evaluate
        MATLAB functions.
        FutureResult - if async or background is true.  This object can be used to obtain the
        real MatlabEngine instance.

    Raises
        EngineError - if the MATLAB cannot be connected.
    """
    
    #multi-threads cannot run this function simultaneously 

    background = enginehelper._get_async_or_background_argument(kwargs)
    if name is None:
        with _engine_lock:
            #if there is no shareable or more than one shareable MATLAB
            engines = find_matlab()

            if len(engines) == 0:
                future = FutureResult(option="-r matlab.engine.shareEngine")
            else:
                #if there are shareable MATLAB sessions available
                future = FutureResult(name=engines[0], attach=True)

            if not background:
                eng = future.result()
                return eng
            else:
                return future
    else:
        future = FutureResult(name=name, attach=True)
        if not background:
            eng = future.result()
            return eng
        else:
            return future

@atexit.register
def __exit_engines():
    for eng in _engines:
        if eng() is not None:
            eng().exit()
    _session.release()
