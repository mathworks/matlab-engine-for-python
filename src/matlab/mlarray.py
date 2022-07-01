# Copyright 2014-2015 MathWorks, Inc.
"""
Type-specific multidimensional arrays for
use when working with MATLAB.

This module defines type-specific multidimensional arrays to use when
evaluating functions using MATLAB. They are different from Python
sequences in the following ways:
    * They use strong typing. They can only contain values of the
     specified type. Attempting to insert values that cannot be represented
     in the specified type raises an exception.
    * They are multidimensional. The size of an empty array is (0,0).
    All arrays created using these classes are rectangular.
    * They use MATLAB style indexing.
    * They slice using views and not shallow copies.

Classes
-------
    * double - array of Python float seen as MATLAB double
    * single - array of Python float seen as MATLAB single
    * uint8 - array of Python int seen as MATLAB uint8
    * int8 - array of Python int seen as MATLAB int8
    * uint16 - array of Python int seen as MATLAB uint16
    * int16 - array of Python int seen as MATLAB int16
    * uint32 - array of Python int or long seen as MATLAB uint32
    * int32 - array of Python int seen as MATLAB int32
    * uint64 - array of Python int or long seen as MATLAB uint64
    * int64 - array of Python int or long seen as MATLAB int64
    * logical - array of Python bool seen as MATLAB logical
"""
from _internal.mlarray_sequence import _MLArrayMetaClass


class double(_MLArrayMetaClass):

    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of doubles,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool

        """
        try:
            super(double, self).__init__('d', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class single(_MLArrayMetaClass):

    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
         marshaled as an array of singles,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(single, self).__init__('f', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class uint8(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of uint8,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(uint8, self).__init__('B', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class int8(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of int8,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(int8, self).__init__('b', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class uint16(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of uint16,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
         in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(uint16, self).__init__('H', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class int16(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
         "initializer" value which must be a sequence. Initializer will be
         marshaled as an array of int16,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(int16, self).__init__('h', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class uint32(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of unit32,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(uint32, self).__init__('I', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class int32(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of int32,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(int32, self).__init__('i', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class uint64(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of uint64,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(uint64, self).__init__('L', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class int64(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None, is_complex=False):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of int64,if possible, inside of MATLAB.
        "is_complex" can be set to True if the elements should be marshaled
        in as complex values.
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        try:
            super(int64, self).__init__('l', initializer, size, is_complex)
        except Exception as ex:
            raise ex


class logical(_MLArrayMetaClass):
    def __init__(self, initializer=None, size=None):
        """
        A new matlab array whose items are initialized from the optional
        "initializer" value which must be a sequence. Initializer will be
        marshaled as an array of logicals,if possible, inside of MATLAB.
        :param initializer: sequence
        :param size: sequence
        """
        try:
            super(logical, self).__init__('B', initializer, size)
        except Exception as ex:
            raise ex

    def __getitem__(self, index):
        value = super(logical, self).__getitem__(index)
        if isinstance(value, type(self)):
            return value
        else:
            return bool(value)
