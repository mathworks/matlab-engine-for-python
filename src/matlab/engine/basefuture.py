#Copyright 2015 MathWorks, Inc.

"""
BaseFuture: The base class of FevalFuture and MatlabFuture.

"""

import time


class BaseFuture(object):

    def wait(self, timeout, wait_for_func):
        """
        Wait for the execution of a function.

        Parameter
            timeout: int
                    Number of seconds to wait before returning.

        Returns
            The result is ready or not.
        """
        time_slice = 1
        if timeout is None:
            result_ready = self.done()
            while not result_ready:
                result_ready = wait_for_func(self._future, time_slice)
        else:
            result_ready = self.done()
            current_time = time.time()
            sleep_until = current_time + timeout
            while (not result_ready) and (current_time < sleep_until):
                if (sleep_until - current_time) >= time_slice:
                    result_ready = wait_for_func(self._future, time_slice)
                else:
                    time_to_sleep = sleep_until - current_time
                    result_ready = wait_for_func(self._future, time_to_sleep)
                current_time = time.time()
        return result_ready