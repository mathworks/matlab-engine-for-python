# Copyright 2014-2018 MathWorks, Inc.

from _internal.mlarray_utils import _get_strides, _get_size, \
    _normalize_size, _get_mlsize, _reshape
try:
    import collections.abc as collectionsABC
except ImportError:
    import collections as collectionsABC
import array
import matlab

# xrange deprecated in Python3
# In Python3 range() behaves like xrange()
try:
    xrange
except NameError:
    xrange = range

try:
    python_type = {'d': float, 'f': float, 'L': long, 'l': int, 'I': long,
                   'i': int, 'H': int, 'h': int, 'B': int, 'b': int}
except NameError:
    python_type = {'d': float, 'f': float, 'L': int, 'l': int, 'I': int,
                   'i': int, 'H': int, 'h': int, 'B': int, 'b': int}


class _MLArrayMetaClass(collectionsABC.Sequence):
    def __init__(self, typecode, initializer=None,
                 size=None, is_complex=False):
        """
        Provides a concrete implementation for the abstract
        base class collections.sequence.
        :param typecode: single character
        :param initializer: sequence
        :param size: sequence
        :param is_complex: bool
        """
        self._is_complex = is_complex
        self._python_type = python_type[typecode]
        if initializer is not None:
            init_dims = _get_size(initializer)
            try:
                self._size = _normalize_size(size, init_dims)
            except matlab.ShapeError as ex:
                raise ex
            except matlab.SizeError as ex:
                raise ex
            strides = _get_strides(self._size)
            self._strides = strides[:-1]
            try:
                if is_complex:
                    complex_array = flat(self, initializer,
                                         init_dims, typecode)
                    self._real = complex_array['real']
                    self._imag = complex_array['imag']
                else:
                    self._data = flat(self, initializer, init_dims, typecode)
            except:
                raise

        else:
            # initializer is None
            if size is not None:
                self._size = _get_mlsize(size)
                strides = _get_strides(self._size)
                self._strides = strides[:-1]
                if is_complex:
                    self._real = array.array(typecode, [0]) * strides[-1]
                    self._imag = array.array(typecode, [0]) * strides[-1]
                else:
                    self._data = array.array(typecode, [0]) * strides[-1]
            else:
                # size = initializer = None
                self._size = (0, 0)
                if is_complex:
                    self._real = array.array(typecode, [])
                    self._imag = array.array(typecode, [])
                else:
                    self._data = array.array(typecode, [])
        self._start = 0

    def __getitem__(self, index):
        """
        :param index: int
        :return: sequence or scalar value
        :return: self or scalar value
        :raise IndexError, TypeError
        """
        try:
            if index < 0:
                index = self._normalize_index(index)

            # base case: reached the last dimension
            if len(self._size) == 1:
                offset = self._start + (self._strides[0] * index)
                if self._is_complex:
                    return complex(self._real[offset], self._imag[offset])
                else:
                    # __iter__ does not take length into account
                    if index >= len(self):
                        raise IndexError
                    return self._data[offset]

            # sublist case
            elif index < self._size[0]:
                # calling __new__ here instead of the constructor
                # to avoid the overhead of calling __init__
                arraytype = type(self)
                mlslice = arraytype.__new__(arraytype)

                mlslice._is_complex = self._is_complex
                if self._is_complex:
                    mlslice._real = self._real
                    mlslice._imag = self._imag
                else:
                    mlslice._data = self._data

                mlslice._start = self._start + (self._strides[0] * index)
                mlslice._strides = self._strides[1:]
                mlslice._size = self._size[1:]
                mlslice._python_type = self._python_type

                return mlslice
            else:
                raise IndexError
        except:
            # call to isinstance is move to the except clause to avoid
            # its overhead for the common cases
            if isinstance(index, slice):
                return self._getslice(index)
            else:
                raise

    def __setitem__(self, index, value):
        """
        :param index: int
        :param value: sequence or scalar value
        :return: :raise IndexError:
        """
        try:
            if index < 0:
                index = self._normalize_index(index)

            # base case: reached the last dimension
            if len(self._size) == 1:
                offset = self._start + (self._strides[0] * index)
                if self._is_complex:
                    try:
                        self._real[offset] = self._python_type(value.real)
                        self._imag[offset] = self._python_type(value.imag)
                    except:
                        raise
                else:
                    try:
                        self._data[offset] = value
                    except (TypeError, OverflowError):
                        raise
                    except:
                        raise ValueError("can only assign a scalar")
                    return

            # sublist case
            elif index < self._size[0]:
                item = self[index]
                # len(value) is an expensive operation, so
                # we avoid calling it for the base case
                try:
                    num_values = len(value)
                except TypeError:
                    raise ValueError("can only assign a sequence")

                if not (num_values == len(item)):
                    raise ValueError("number of elements to be assigned "
                                     "should match the target's length")
                for idx in xrange(0, len(item)):
                    item[idx] = value[idx]
            else:
                raise IndexError

        except:
            # call to isinstance is move to the except clause to avoid
            # its overhead for the common cases
            if isinstance(index, slice):
                slice_obj = self._getslice(index)
                # len(value) is an expensive operation, so
                # we avoid calling it for the base case
                try:
                    num_values = len(value)
                except TypeError:
                    raise ValueError("can only assign a sequence")

                if len(slice_obj) != num_values:
                    raise ValueError("number of slices do not match "
                                     "number of values")
                for idx, val in enumerate(value):
                    slice_obj[idx] = val
            else:
                raise

    def __len__(self):
        return int(self._size[0])

    @property
    def size(self):
        """
        :return: returns the dimensions of the mlarray
        """
        return tuple(self._size)

    def __repr__(self):
        class_name = 'matlab.' + str(self.__class__.__name__)
        if self._is_complex:
            return class_name + '(' + str(self) + ', ' + \
                'is_complex=' + str(self._is_complex) + ')'
        return class_name + '(' + str(self) + ')'

    # use join ','.join([str(x) for x in range(10)])
    def __str__(self):
        ret = '['
        for i in xrange(0, len(self)):
            if i == (len(self) - 1):
                ret += str(self[i])
            else:
                ret += str(self[i]) + ','
        ret += ']'
        return ret

    def __eq__(self, other):
        try:
            return (self.size == other.size) and \
                all(self[i] == other[i] for i in xrange(0, len(self))) and \
                   (type(self) == type(other))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def reshape(self, size):
        self._size = _reshape(self._size, size)
        self._strides = _get_strides(self._size)[:-1]

    def _normalize_index(self, index):
        if index < 0:
            index += len(self)
            if index < 0:
                raise IndexError
            return index
        return index

    def _getslice(self, index):
        start, stop, step = self._identify_slice_range(index)
        if stop == start:
            return type(self)([])

        if (start < stop) == (step < 0):
            return type(self)([])

        if (start >= len(self)) and (step > 0):
            return type(self)([])

        mlslice = type(self)()
        if self._is_complex:
            mlslice._is_complex = True
            mlslice._real = self._real
            mlslice._imag = self._imag
        else:
            mlslice._data = self._data

        mlslice._size = list(self._size[:])
        mlslice._strides = self._strides[:]
        mlslice._start = self._start

        mlslice._start += (self._strides[0] * start)
        mlslice._strides[0] *= step

        if start < stop:
            mlslice._size[0] = int((stop - start + step - 1) / step)
        else:
            mlslice._size[0] = int((stop - start + step + 1) / step)

        mlslice._size = tuple(mlslice._size)
        return mlslice

    # check None explicitly
    def _identify_slice_range(self, index):
        if index.step is None:
            step = 1
        else:
            step = index.step

        if index.start is None:
            if step < 0:
                start = len(self) - 1
            else:
                start = 0
        else:
            if index.start < 0:
                start = index.start + len(self)
                if start < 0:
                    if step > 0:
                        start = 0
            elif index.start >= len(self):
                if step < 0:
                    start = len(self) - 1
                else:
                    start = index.start
            else:
                start = index.start

        if index.stop is None:
            if step < 0:
                stop = -1
            else:
                stop = len(self)
        else:
            if index.stop < 0:
                stop = index.stop + len(self)
                if stop < 0:
                    stop = -1
            elif index.stop > len(self):
                stop = len(self)
            else:
                stop = index.stop

        if index.step == 0:
            raise ValueError("slice step cannot be zero")

        return start, stop, step


def flat(ml_array, nested_list, dimensions, typecode):
    strides = _get_strides(dimensions)
    is_complex = ml_array._is_complex
    if len(dimensions) == 1 and (not is_complex):
        if isinstance(ml_array, matlab.logical):
            return array.array(typecode, [bool(x) for x in nested_list])
        return array.array(typecode, nested_list)
    depth = len(dimensions)

    if is_complex:
        real_array = array.array(typecode, [0] * strides[-1])
        imag_array = array.array(typecode, [0] * strides[-1])
        flat_array = {'real': real_array, 'imag': imag_array}
    else:
        flat_array = array.array(typecode, [0] * strides[-1])

    generic_flattening(ml_array, flat_array, nested_list, 0, strides,
                       dimensions, depth, typecode, is_complex)
    return flat_array


def generic_flattening(ml_array, flat_array, source, start, strides,
                       dimsarray, depth, typecode, is_complex):
    if depth == 1:
        numelemstocopy = dimsarray[0]
        stride = strides[0]
        for idx in range(0, numelemstocopy):
            try:
                if is_complex:
                    flat_array['real'][start] = \
                        python_type[typecode](source[idx].real)
                    flat_array['imag'][start] = \
                        python_type[typecode](source[idx].imag)
                if isinstance(ml_array, matlab.logical):
                    flat_array[start] = bool(source[idx])
                else:
                    flat_array[start] = source[idx]
            except:
                raise
            start += stride
    else:
        depth -= 1
        stride = strides[0]
        dimsize = dimsarray[0]
        substride = strides[1:]
        subdimsarray = dimsarray[1:]
        for idx in range(0, dimsize):
            generic_flattening(ml_array, flat_array, source[idx], start,
                               substride, subdimsarray, depth,
                               typecode, is_complex)
            start += stride
