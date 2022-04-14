#Copyright 2014-2017 MathWorks, Inc.

"""
MatlabEngine: The class name of MATLAB Engine.  You can call MATLAB software as
a computational engine using the MatlabEngine class.
"""


from matlab.engine import pythonengine
from matlab.engine import FutureResult
from matlab.engine import RejectedExecutionError
from matlab.engine import MatlabExecutionError
import weakref
import shlex
from matlab.engine import enginehelper

try:
    import StringIO as sIO
except ImportError:
    import io as sIO

class MatlabFunc(object):
    """
    Reference to a MATLAB function, where "matlabfunc" is replaced by the
    function called by the user. *args are passed to MATLAB. **kwargs are
    only passed to the engine.
    """

    def __init__(self, eng, name):
        self.__dict__["_engine"] = weakref.ref(eng)
        self.__dict__["_name"] = name

    def __getattr__(self, name):
        return MatlabFunc(self._engine(), "%s.%s" % (self._name, name))

    def __setattr__(self, kw, value):
        raise AttributeError(pythonengine.getMessage('AttrCannotBeAddedToM'))

    def __call__(self, *args, **kwargs):
        self.__validate_engine()

        nargs = kwargs.pop('nargout', 1)

        if not isinstance(nargs, int):
            raise TypeError(pythonengine.getMessage('NargoutMustBeInt',  type(nargs).__name__))

        if nargs < 0:
            raise ValueError(pythonengine.getMessage('NargoutCannotBeLessThanZero'))

        _stdout = kwargs.pop('stdout', None)
        _stderr = kwargs.pop('stderr', None)

        background = enginehelper._get_async_or_background_argument(kwargs)
        
        _sIO_info = '{0}.{1}'.format(sIO.__name__, sIO.StringIO.__name__);
        if (_stdout is not None) and (not isinstance(_stdout, sIO.StringIO)):
            _stdout_info = '{0}.{1}'.format(_stdout.__class__.__module__, _stdout.__class__.__name__);
            raise TypeError(pythonengine.getMessage('StdoutMustBeStringIO', _sIO_info, _stdout_info))

        if (_stderr is not None) and (not isinstance(_stderr, sIO.StringIO)):
            _stderr_info = '{0}.{1}'.format(_stderr.__class__.__module__, _stderr.__class__.__name__);
            raise TypeError(pythonengine.getMessage('StderrMustBeStringIO', _sIO_info, _stderr_info))

        future = pythonengine.evaluateFunction(self._engine()._matlab,
                                               self._name, nargs,args,
                                               out=_stdout, err=_stderr)
        if background:
            return FutureResult(self._engine(), future, nargs, _stdout, _stderr, feval=True)
        else:
            return FutureResult(self._engine(), future, nargs, _stdout,
                                _stderr, feval=True).result()

    def __validate_engine(self):
        if self._engine() is None or not self._engine()._check_matlab():
            raise RejectedExecutionError(pythonengine.getMessage('MatlabTerminated'))  
                                
class MatlabWorkSpace(object):
    """
        ['<matlabvar>']
        ['<matlabvar>']=vardata

            Pass a variable into the MATLAB workspace and copy a
            variable from the MATLAB workspace.

            Parameters
                <matlabvar>: str
                    Variable name to be used in the MATLAB workspace.

                vardata: object
                    A Python variable to be passed into the MATLAB workspace.

            Returns
                ['<matlabvar>'] returns the variable copied from the
                MATLAB workspace.

                ['<matlabvar>']=vardata returns None.

            Raises
                NameError - if there is no such variable in the MATLAB
                workspace.

                SyntaxError - if the data is passed to the MATLAB
                workspace with an illegal variable name.

                TypeError - if <matlabvar> is not a string, or if
                the data type of vardata is not supported.

                ValueError - if <matlabvar> is empty.

                RejectedExecutionError - if the Engine is terminated.
    """

    def __init__(self,eng):
        self.__dict__["_engine"] = weakref.ref(eng)

    def __getitem__(self,attr):
        self.__validate_engine()
        self.__validate_identity(attr)
        _method=MatlabFunc(self._engine(), "matlab.internal.engine.getVariable")
        future = _method(attr)
        return future

    def __setitem__(self,attr,value):
        self.__validate_engine()
        self.__validate_identity(attr)
       
        _method=MatlabFunc(self._engine(), "assignin")
        return  _method("base", attr, value, nargout=0)
        
    def __repr__(self):
        _method = MatlabFunc(self._engine(), "whos")
        _method(nargout=0)
        return ""

    def __setattr__(self, kw, value):
        raise AttributeError(pythonengine.getMessage('AttrCannotBeAddedToMWS'))

    def __validate_engine(self):
        if self._engine() is None or not self._engine()._check_matlab():
            raise RejectedExecutionError(pythonengine.getMessage('MatlabTerminated'))

    def __validate_identity(self, attr):
        if not isinstance(attr, str):
            raise TypeError(pythonengine.getMessage('VarNameMustBeStr',  type(attr).__name__))
        if not pythonengine.validateIdentity(attr):
            raise ValueError(pythonengine.getMessage('VarNameNotValid'))
      
class MatlabEngine(object):
    """
    By default, the MATLAB Engine starts a MATLAB instance in a separate 
    process without the desktop on the local machine.  The MATLAB version 
    used by the engine application is the version of MATLAB specified in PATH.

    The MATLAB Engine supports calling MATLAB functions directly. MATLAB 
    functions are dynamically added to a MatlabEngine object as callable 
    attributes.  The function name <matlabfunc> is a replaceable MATLAB 
    function name (for example, sqrt). The function signature is the same as in
    MATLAB, with optional named arguments nargout, async|background, stdout, and stderr.

    workspace['<matlabvar>']
        A property to represent the MATLAB workspace.  Variables in
        the MATLAB workspace can be accessed through <matlabvar>.  The
        type of this property is MatlabWorkSpace.


    <matlabfunc>(*args, nargout=1, async=False, stdout=sys.stdout, stderr=sys.stderr)
    <matlabfunc>(*args, nargout=1, background=False, stdout=sys.stdout, stderr=sys.stderr)

        The invocation of a MATLAB statement can be either synchronous
        or asynchronous.  While a synchronous function call returns
        the result after it finishes executing, an asynchronous
        function call is performed in the background and returns a FutureResult
        immediately.  This FutureResult object can be used to retrieve the 
        actual result later.  If there are any output or error messages 
        generated from <matlabfunc>, by default they will be redirected to the
        standard output or standard error of the Python console.

        Please note that you can call an arbitrary MATLAB function
        available in the MATLAB path using feval and eval.

        Parameters
            args:
                Arguments accepted by the MATLAB function to be called.
            nargout: int
                By default, the number of output is 1.  If the number of output
            is more than 1, a tuple is returned.
            async, background: bool
                This parameter is used to specify how the MATLAB command is
            evaluated: asynchronously or synchronously. By default, async|background
            is chosen to be False so the MATLAB command is evaluated synchronously.
            "async" is a synonym for "background" that will be removed in a future release.
            stdout: StringIO.StringIO (Python 2.7),  io.StringIO (Python 3)
                Stream used to capture the output of the MATLAB command.  By
            default, the system standard output sys.stdout is used.
            stderr: StringIO.StringIO (Python 2.7),  io.StringIO (Python 3)
                Stream used to capture the error message of the MATLAB command.
            By default, the system standard error output sys.stderr is used.

        Returns
            The type of the return value of this function varies based on the
            value of parameter async or background.  For the case of synchronously invocation,
            the result of the MATLAB command is returned directly.  For the case
            of asynchronous invocation, a FutureResult is returned which can be
            used to retrieve the actual result, check completion status, and
            interrupt the execution of the MATLAB function.

        Raises
            RejectedExecutionError - if the engine is terminated.
            SyntaxError - if there is an error in parsing the MATLAB statement.
            MatlabExecutionError - if the MATLAB statement fails in execution.
            TypeError - if the data types of *args are not supported by
            MATLABEngine; or if the data type of a return value is not supported.

    """

    def __init__(self, matlab):
        self.__dict__["_matlab"] = matlab
        self.__dict__["workspace"] = MatlabWorkSpace(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit()

    def exit(self):
        """
        Stop the MATLAB session.  Calling this method will terminate the
        MatlabEngine instance immediately.
        """
        if self._check_matlab():
            pythonengine.closeMATLAB(self.__dict__["_matlab"])
            self.__dict__.pop("_matlab")

    def quit(self):
        """
        Stop the MATLAB session.  Calling this method will terminate the
        MatlabEngine instance immediately.
        """
        self.exit()

    def __getattr__(self,name):
        """Dynamic attribute of MatlabEngine"""
        return MatlabFunc(self, name)
    
    def __setattr__(self, kw, value):
        raise AttributeError(pythonengine.getMessage('AttrCannotBeAddedToM'))

    def __del__(self):
        self.exit()
        
    def _check_matlab(self):
         return "_matlab" in self.__dict__
