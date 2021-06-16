"""
The decorator module has useful decorators to facilitate coding.
"""
import functools

__all__ = ['copy_docstring']


def copy_docstring(origin):
    """
    Decorator to initialize the docstring from another source.

    This is useful to duplicate a docstring for inheritance and composition.

    If origin is a method or a function, it copies its docstring.
    If origin is a class, the docstring is copied from the method
    of that class which has the same name as the method/function
    being decorated.

    Parameters
    ----------
    origin : object
        The origin object with the docstring.

    Raises
    ------
    ValueError
        If the origin class does not have the method with the same name.
    """
    def _docstring(dest, origin):
        if not isinstance(dest, type) and isinstance(origin, type):
            try:
                origin = getattr(origin, dest.__name__)
            except AttributeError:
                raise ValueError('Origin class has no method called '
                                 f'{dest.__name__}')

        dest.__doc__ = origin.__doc__
        return dest
    return functools.partial(_docstring, origin=origin)
