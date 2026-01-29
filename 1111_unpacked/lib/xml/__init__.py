# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
# Embedded file name: L:\work\rtsummit_RTSUMMIT-PC\metin2\dev\Srcs\Client\bin\lib\xml\__init__.py
# Compiled at: 2011-03-08 03:45:24
"""Core XML support for Python.

This package contains four sub-packages:

dom -- The W3C Document Object Model.  This supports DOM Level 1 +
       Namespaces.

parsers -- Python wrappers for XML parsers (currently only supports Expat).

sax -- The Simple API for XML, developed by XML-Dev, led by David
       Megginson and ported to Python by Lars Marius Garshol.  This
       supports the SAX 2 API.

etree -- The ElementTree XML library.  This is a subset of the full
       ElementTree XML release.

"""
__all__ = [
 'dom', 'parsers', 'sax', 'etree']
_MINIMUM_XMLPLUS_VERSION = (0, 8, 4)
try:
    import _xmlplus
except ImportError:
    pass

try:
    v = _xmlplus.version_info
except AttributeError:
    pass

if v >= _MINIMUM_XMLPLUS_VERSION:
    import sys
    _xmlplus.__path__.extend(__path__)
    sys.modules[__name__] = _xmlplus
else:
    del v
return
