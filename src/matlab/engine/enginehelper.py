#Copyright 2017-2020 MathWorks, Inc.
import warnings
from matlab.engine import pythonengine
import sys

def _get_async_or_background_argument(kwargs):
    if 'async' in kwargs and 'background' in kwargs:
        raise KeyError(pythonengine.getMessage('EitherAsyncOrBackground'))
    background = False
    if 'async' in kwargs:
        background = kwargs.pop('async', False)
        if not isinstance(background, bool):
            raise TypeError(pythonengine.getMessage('AsyncMustBeBool'))
        if sys.version_info.major >= 3 and sys.version_info.minor >= 7:
            # No test should be passing "async" with Python 3.7 or higher, so throw an exception
            # if a test tries to do it.
            raise SyntaxError(pythonengine.getMessage('AsyncWillDeprecate'))

    if 'background' in kwargs:
        background = kwargs.pop('background', False)
        if not isinstance(background, bool):
            raise TypeError(pythonengine.getMessage('BackgroundMustBeBool'))

    if kwargs:
        raise TypeError((pythonengine.getMessage('InvalidKwargs', list(kwargs.keys())[0].__repr__())))

    return background