# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
# Embedded file name: L:\work\Python-2.7.3\lib\types.py
# Compiled at: 2012-04-10 02:07:32
"""Define names for all type symbols known in the standard interpreter.

Types that are part of optional modules (e.g. array) are not listed.
"""
import sys
NoneType = type(None)
TypeType = type
ObjectType = object
IntType = int
LongType = long
FloatType = float
BooleanType = bool
try:
    ComplexType = complex
except NameError:
    pass

StringType = str
try:
    UnicodeType = unicode
    StringTypes = (StringType, UnicodeType)
except NameError:
    StringTypes = (
     StringType,)

BufferType = buffer
TupleType = tuple
ListType = list
DictType = DictionaryType = dict

def _f():
    return


FunctionType = type(_f)
LambdaType = type((lambda : None))
CodeType = type(_f.func_code)

def _g():
    yield 1
    return


GeneratorType = type(_g())

class _C:

    def _m(self):
        return


ClassType = type(_C)
UnboundMethodType = type(_C._m)
_x = _C()
InstanceType = type(_x)
MethodType = type(_x._m)
BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)
ModuleType = type(sys)
FileType = file
XRangeType = xrange
try:
    raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    del tb

SliceType = slice
EllipsisType = type(Ellipsis)
DictProxyType = type(TypeType.__dict__)
NotImplementedType = type(NotImplemented)
GetSetDescriptorType = type(FunctionType.func_code)
MemberDescriptorType = type(FunctionType.func_globals)
del sys
del _f
del _g
del _C
del _x
return
