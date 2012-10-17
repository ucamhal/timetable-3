'''
Created on Oct 17, 2012

@author: ieb
'''
from django.utils.importlib import import_module
import logging
import types

log = logging.getLogger(__name__)

def newinstance(clsname):
    module_name = ".".join(clsname.split(".")[:-1])
    class_name = clsname.split(".")[-1]
    module = import_module(module_name)
    try:
        identifier = getattr(module,class_name)
    except AttributeError:
        log.error("Class %s not found in %s " % ( class_name, module_name))
        return None
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier()
    log.error("Class %s found in %s is not a class" % ( class_name, module_name))                
    return None
