"""
This module provides access to values in the Django settings file. 
"""
from django.utils import importlib
from django import conf


def _split_python_name(python_name):
    """
    Splits a fully qualified Python import path into package and name.
    
    Examples:
        "foo.bar.baz.Boz" -> ("foo.bar.baz", "Boz")
        "foo" -> ("foo", "")  
    """
    try:
        separator = python_name.rindex(".")
    except ValueError:
        return python_name, ""
    return python_name[:separator], python_name[separator + 1:]

def resolve_object(full_name):
    """
    Imports and returns an object referenced by the fully qualified Python name.
    
    Args:
        name: An importable Python name, e.g. "itertools.groupby".
    Returns: The referenced object.
    Raises:
        ValueError: If the name does not resolve to an object.
    """
    package, name = _split_python_name(full_name)
    try:
        return getattr(importlib.import_module(package), name)
    except AttributeError:
        raise ValueError('Error resolving: "%s": "%s" does not exist in "%s"' %
                (full_name, name, package))
    except ImportError:
        raise ValueError('Error resolving: "%s": Package "%s" does not exist' %
                (full_name, package))

def resolve_callable(full_name):
    """
    Resolves the callable object referenced by full_name. e.g.
    "itertools.groupby". If full_name is a callable it's directly returned.
    """
    if callable(full_name):
        return full_name
    obj = resolve_object(full_name)
    if callable(obj):
        return obj
    raise ValueError("Object resolved at %s is not callable: %s" %
            (full_name, obj))

def get(name, **kwargs):
    """
    Gets the value of a setting, defaulting to a provided value if name does not
    exist.
    """
    try:
        return getattr(conf.settings, name)
    except AttributeError:
        if "default" in kwargs:
            return kwargs["default"]
        raise

def get_callable(name, **kwargs):
    """
    Gets a callable from a settings value. The value can either be a callable
    object, or a fully qualified Python import path to the callable, e.g. 
    "itertools.groupby".
    """
    return resolve_callable(get(name, **kwargs))

def get_list(name, **kwargs):
    val = get(name, **kwargs)
    
    try:
        # Return a list of the values ...
        return list(iter(val))
    except TypeError:
        # ... or a list containing an individual value if the val is not
        # iterable.
        return [val]

def get_callable_list(name, default=None):
    """
    Gets a list of callables from a setting value such as"
    
    SOME_NAME = ("itertools.groupby", "itertools.ifilter", reduce, map)
    """
    return [resolve_callable(n) for n in get_list(name, default=default)]
