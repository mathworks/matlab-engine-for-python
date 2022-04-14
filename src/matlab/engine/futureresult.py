#Copyright 2014-2017 MathWorks, Inc.

"""
FutureResult: The class name of a future result returned by the MATLAB Engine.

An instance of FutureResult is returned from each asynchronous invocation of a
function call: start_matlab, connect_matlab, or MatlabEngine.<matlabfunc>.  The
 future result serves as a placeholder of the actual result, so the future
 result can be returned immediately.  The actual result is placed into the
 placeholder when the function finishes its evaluation.  The future result can
 be used to interrupt the execution, check the completion status, and get the
 actual result.
"""

from matlab.engine import pythonengine
from matlab.engine import MatlabFuture
from matlab.engine import FevalFuture

try:
    long
except NameError:
    long = int

class FutureResult():
    """
    A FutureResult object is used to hold the future result of a function call.
    The FutureResult object can be created by start_matlab(async=True),
    connect_matlab(async=True), and MaltabEngine.<matlabfunc>(async=True).
    """
    
    def __init__(self, *args, **kwargs):
        feval = kwargs.pop("feval", False)
        if feval:
            self.__future = FevalFuture(*args)
        else:
            self.__future = MatlabFuture(*args, **kwargs)

    def result(self, timeout=None):
        """
        Get the MatlabEngine object or the result of a MATLAB statement.

        Parameter
            timeout: int
                    Number of seconds to wait before returning.  By default,
            this function will wait until the result is generated.

        Returns
            The MatlabEngine object or the result of MATLAB statement.  A tuple
             is returned if multiple outputs are returned.

        Raises
            SyntaxError - if there is an error in the MATLAB statement.
            InterruptedError - if the task is interrupted.
            CancelledError - if the evaluation of MATLAB function is cancelled already.
            TimeoutError - if this method fails to get the result in timeout seconds.
            MatlabExecutionError - if the MATLAB statement fails in execution.
            TypeError - if the data type of return value is not supported.
            RejectedExecutionError  - an error occurs if the engine is terminated.
        """
        if timeout is not None:
            if not isinstance(timeout, (int, long, float)):
                raise TypeError(pythonengine.getMessage('TimeoutMustBeNumeric', type(timeout).__name__))
            
            if timeout < 0:
                raise TypeError(pythonengine.getMessage('TimeoutCannotBeNegative'))
        
        return self.__future.result(timeout)
    
    def cancel(self):
        """
        Cancel the launch/connection of MATLAB or evaluation of a MATLAB
        task.
    
        Returns 
            bool - True if the corresponding task can be cancelled;
            False otherwise.

        Raises 
            RejectedExecutionError  - an error occurs if the Engine is terminated.
        """
        return self.__future.cancel()
    
    def cancelled(self):
        """
        Obtain the cancellation status of the asynchronous execution of the
        function.
    
        Returns 
            bool - True if the execution is cancelled; False otherwise.

        Raises 
            RejectedExecutionError  - an error occurs if the engine is terminated.
        """
        return self.__future.cancelled()

    def done(self):
        """
        Obtain the completion status of the asynchronous invocation of the
        task.

        Returns 
            bool - True if the execution is finished; False otherwise.  It
            returns True even if there is an error generated from the task
            or the task is cancelled.

        Raises 
            RejectedExecutionError - an error occurs if the engine is terminated.
        """
        return self.__future.done()
    
    def __del__(self):
        if self.__future is not None:
            del self.__future