# Copyright 2014-2020 MathWorks, Inc.

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence
    
import matlab

try:
    reduce
except NameError:
    from functools import reduce


def _is_rectangular(initializer):
    """

    :param initializer:
    :return: A tuple containing (bool, int)
     For a given input, the bool value represents whether it is a valid sequence
     and the int value represents the depth of the sequence.
    """
    if initializer is None:
        return True, 1

    if not isinstance(initializer, Sequence):
        return False, None

    try:
        is_sequence = map(lambda x: (isinstance(x, Sequence)
                                     or hasattr(x, '__len__')), initializer)
        is_sequence = list(is_sequence)
    except TypeError:
        return False, None

    if not any(is_sequence):
        return True, 1

    if not all(is_sequence):
        return False, None

    # handle strings
    for val in initializer:
        if val is initializer:
            return False, None

    rect_vals = list(_is_rectangular(val) for val in initializer)
    first_depth = rect_vals[0][1]
    for rect, depth in rect_vals:
        if not rect or depth != first_depth:
            return False, None

    try:
        size_vals = [len(val) for val in initializer]
    except TypeError:
        return False, None

    if size_vals.count(size_vals[0]) != len(size_vals):
        return False, None
    return True, first_depth + 1


def _get_strides(dimensions):
    strides = [1]
    for idx, dim in enumerate(dimensions):
        if dim < 0:
            raise ValueError("size cannot contain negative dimensions")
        strides.append(strides[idx] * dimensions[idx])
    return strides


def _get_size(initializer):
    is_rect, depth = _is_rectangular(initializer)
    if not is_rect:
        raise ValueError("initializer must be a rectangular nested sequence")

    dims = []
    while True:
        try:
            init_len = len(initializer)
            dims.append(init_len)
            if init_len == 0:
                break
            else:
                initializer = initializer[0]
        except TypeError:
            break
    return tuple(dims)


def _normalize_size(size, init_dims):
    if size is None:
        if init_dims[0] == 0:
            return 0, 0
        return _get_mlsize(init_dims)

    ml_size = _get_mlsize(size)
    ml_init_dims = _get_mlsize(init_dims)
    if tuple(ml_init_dims) == tuple(ml_size):
        return ml_size

    num_elems_initializer = reduce(lambda x, y: x * y, init_dims)
    num_elems_size = reduce(lambda x, y: x * y, size)
    if not (num_elems_initializer == num_elems_size):
        raise matlab.ShapeError("total number of elements "
                                "must remain unchanged")
    if (num_elems_size == num_elems_initializer) and not \
            (init_dims[0] == num_elems_initializer and len(init_dims) == 1):
        raise matlab.SizeError("size argument does not match "
                               "dimensions of initializer")
    return ml_size


def _reshape(from_ml_size, to_size):
    to_ml_size = _get_mlsize(to_size)
    if tuple(from_ml_size) == tuple(to_ml_size):
        return to_ml_size

    num_seq_elems = reduce(lambda x, y: x * y, from_ml_size)
    num_exp_elems = reduce(lambda x, y: x * y, to_ml_size)
    if not (num_seq_elems == num_exp_elems):
        raise matlab.ShapeError("total number of elements "
                                "must remain unchanged")
    return to_ml_size


def _get_mlsize(size):
    if not hasattr(size, '__getitem__'):
        raise TypeError("invalid size")
    if len(size) == 0:
        raise ValueError("size cannot be empty")
    if len(size) == 2:
        return size
    if len(size) == 1:
        return 1, size[0]
    if size[-1] != 1:
        return size
    return _get_mlsize(size[:-1])
