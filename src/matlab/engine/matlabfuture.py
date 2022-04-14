#Copyright 2015 MathWorks, Inc.


"""
MatlabFuture: The class name of a future handle returned by starting MATLAB
asynchronously.

An instance of MatlabFuture is returned from the invocation of starting MATLAB
asyncronously.  The future handle serves as a placeholder of the actual MATLAB
instance, the the future handle can be returned immediately.  The future handle
can be used to interrupt the launch of MATLAB, check the completion status and
get the real MATLAB Engine object.

"""

from matlab.engine import pythonengine
from matlab.engine import TimeoutError
from matlab.engine import CancelledError
from matlab.engine import BaseFuture
from matlab.engine import _engines
from matlab.engine import _engine_lock
import shlex
import weakref


class MatlabFuture(BaseFuture):
    """
    A MatlabFuture object is used to hold the future handle of a MATLAB
    instance.  The MatlabFuture object should be only created by calling
    start_matlab or connect_matlab asynchronously.
    """

    def __init__(self, **kargs):
        tokens = []
        option = kargs.pop("option", None)
        name_ = kargs.pop("name", None)
        attach = kargs.pop("attach", False)
        self._matlab = None
        self._cancelled = False
        self._done = False
        if option is not None:
            tokens = shlex.split(option)
        try:
            if attach:
                self._future = pythonengine.attachMATLABAsync(name_)
                self._attach = True
            else:
                self._future = pythonengine.createMATLABAsync(tokens)
                self._attach = False
        except:
            raise

    def result(self, timeout=None):
        """
        Get the MatlabEngine instance.

        Parameter
            timeout: Number of seconds to wait before returning.  By default,
            this function will wait until the MatlabEngine instance is ready.

        Returns
            An object of MatlabEngine class.

        Raises
            CancelledError - if the launch or connection of MATLAB is cancelled already.
            TimeoutError - if the MATLAB instance is not ready in timeout seconds.
        """
        from matlab.engine import MatlabEngine
        if self._cancelled:
            if self._attach:
                raise CancelledError(pythonengine.getMessage('ConnectMatlabCancelled'))
            else:
                raise CancelledError(pythonengine.getMessage('LaunchMatlabCancelled'))

        if self._matlab is not None:
            return self._matlab

        try:
            result_ready = self.wait(timeout, pythonengine.waitForMATLAB)

            if not result_ready:
                if self._attach:
                    raise TimeoutError(pythonengine.getMessage('ConnectMatlabTimeout'))
                else:
                    raise TimeoutError(pythonengine.getMessage('LaunchMatlabTimeout'))

            handle = pythonengine.getMATLAB(self._future)
            eng = MatlabEngine(handle)
            self._matlab = eng
            with _engine_lock:
                _engines.append(weakref.ref(eng))
            return eng

        except KeyboardInterrupt:
            self.cancel()
            print(pythonengine.getMessage('MatlabCancelled'))
        except:
            raise


    def cancel(self):
        """
        Cancel the launch of or connection to a MATLAB instance.

        Returns
            bool - True if the action can be cancelled; False otherwise.
        """
        if self._matlab is None and not self._cancelled and not self._done:
            pythonengine.cancelMATLAB(self._future)
            self._cancelled = True
            return True
        else:
            return False

    def cancelled(self):
        """
        Obtain the cancellation status of the asynchronous launch or connection
         to a MATLAB instance.

        Returns
            bool - True if the execution was cancelled; False otherwise.
        """
        if self._cancelled:
            return True
        return False

    def done(self):
        """
        Obtain the completion status of the asynchronous launch or connection
         to a MATLAB instance.

        Returns
            bool - True if the action is finished; False otherwise.
        """
        if self._done or self._cancelled or self._matlab is not None:
            return True
        self._done = pythonengine.isDoneMATLAB(self._future)
        return self._done

    def __del__(self):
        if self._future is not None:
            pythonengine.destroyMATLAB(self._future)
            self._future = None
            self._matlab = None