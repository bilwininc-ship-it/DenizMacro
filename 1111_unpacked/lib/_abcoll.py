# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
# Embedded file name: L:\work\Python-2.7.3\lib\_abcoll.py
# Compiled at: 2012-04-10 02:07:28
"""Abstract Base Classes (ABCs) for collections, according to PEP 3119.

DON'T USE THIS MODULE DIRECTLY!  The classes here should be imported
via collections; they are defined here only to alleviate certain
bootstrapping issues.  Unit tests are in test_collections.
"""
from abc import ABCMeta, abstractmethod
import sys
__all__ = [
 4, 5, 6, 
 7, 8, 9, 
 10, 11, 
 12, 13, 
 14, 15, 16, 17, 
 18, 
 19]

def _hasattr(C, attr):
    try:
        return any(attr in B.__dict__ for B in C.__mro__)
    except AttributeError:
        return hasattr(C, attr)

    return


class Hashable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __hash__(self):
        return 0

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Hashable:
            try:
                for B in C.__mro__:
                    if '__hash__' in B.__dict__:
                        if B.__dict__['__hash__']:
                            return True
                        break

            except AttributeError:
                if getattr(C, '__hash__', None):
                    return True

        return NotImplemented


class Iterable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        while False:
            yield

        return

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterable:
            if _hasattr(C, '__iter__'):
                return True
        return NotImplemented


Iterable.register(str)

class Iterator(Iterable):

    @abstractmethod
    def next(self):
        raise StopIteration
        return

    def __iter__(self):
        return self

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterator:
            if _hasattr(C, 'next') and _hasattr(C, '__iter__'):
                return True
        return NotImplemented


class Sized:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __len__(self):
        return 0

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Sized:
            if _hasattr(C, '__len__'):
                return True
        return NotImplemented


class Container:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __contains__(self, x):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Container:
            if _hasattr(C, '__contains__'):
                return True
        return NotImplemented


class Callable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, *args, **kwds):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Callable:
            if _hasattr(C, '__call__'):
                return True
        return NotImplemented


class Set(Sized, Iterable, Container):
    """A set is a finite, iterable container.

    This class provides concrete generic implementations of all
    methods except for __contains__, __iter__ and __len__.

    To override the comparisons (presumably for speed, as the
    semantics are fixed), all you have to do is redefine __le__ and
    then the other operations will automatically follow suit.
    """

    def __le__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False

        return True

    def __lt__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        return len(self) < len(other) and self.__le__(other)

    def __gt__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        return other < self

    def __ge__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        return other <= self

    def __eq__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        return len(self) == len(other) and self.__le__(other)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def _from_iterable(cls, it):
        """Construct an instance of the class from any iterable input.

        Must override this method if the class constructor signature
        does not accept an iterable for an input.
        """
        return cls(it)

    def __and__(self, other):
        if not isinstance(other, Iterable):
            return NotImplemented
        return self._from_iterable(value for value in other if value in self)

    def isdisjoint(self, other):
        for value in other:
            if value in self:
                return False

        return True

    def __or__(self, other):
        if not isinstance(other, Iterable):
            return NotImplemented
        chain = (e for s in (self, other) for e in s)
        return self._from_iterable(chain)

    def __sub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(value for value in self if value not in other)

    def __xor__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self - other | other - self

    __hash__ = None

    def _hash(self):
        """Compute the hash value of a set.

        Note that we don't define __hash__: not all sets are hashable.
        But if you define a hashable set type, its __hash__ should
        call this function.

        This must be compatible __eq__.

        All sets ought to compare equal if they contain the same
        elements, regardless of how they are implemented, and
        regardless of the order of the elements; so there's not much
        freedom for __eq__ or __hash__.  We match the algorithm used
        by the built-in frozenset type.
        """
        MAX = sys.maxint
        MASK = 2 * MAX + 1
        n = len(self)
        h = 1927868237 * (n + 1)
        h &= MASK
        for x in self:
            hx = hash(x)
            h ^= (hx ^ hx << 16 ^ 89869747) * 3644798167L
            h &= MASK

        h = h * 69069 + 907133923
        h &= MASK
        if h > MAX:
            h -= MASK + 1
        if h == -1:
            h = 590923713
        return h


Set.register(frozenset)

class MutableSet(Set):

    @abstractmethod
    def add(self, value):
        """Add an element."""
        raise NotImplementedError
        return

    @abstractmethod
    def discard(self, value):
        """Remove an element.  Do not raise an exception if absent."""
        raise NotImplementedError
        return

    def remove(self, value):
        """Remove an element. If not a member, raise a KeyError."""
        if value not in self:
            raise KeyError(value)
        self.discard(value)
        return

    def pop(self):
        """Return the popped value.  Raise KeyError if empty."""
        it = iter(self)
        try:
            value = next(it)
        except StopIteration:
            raise KeyError

        self.discard(value)
        return value

    def clear(self):
        """This is slow (creates N new iterators!) but effective."""
        try:
            while True:
                self.pop()

        except KeyError:
            pass

        return

    def __ior__(self, it):
        for value in it:
            self.add(value)

        return self

    def __iand__(self, it):
        for value in self - it:
            self.discard(value)

        return self

    def __ixor__(self, it):
        if it is self:
            self.clear()
        elif not isinstance(it, Set):
            it = self._from_iterable(it)
        for value in it:
            if value in self:
                self.discard(value)
            else:
                self.add(value)

        return self

    def __isub__(self, it):
        if it is self:
            self.clear()
        else:
            for value in it:
                self.discard(value)

        return self


MutableSet.register(set)

class Mapping(Sized, Iterable, Container):

    @abstractmethod
    def __getitem__(self, key):
        raise KeyError
        return

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

        return

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False

        return True
        return

    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for key in self:
            yield self[key]

        return

    def iteritems(self):
        for key in self:
            yield (
             key, self[key])

        return

    def keys(self):
        return list(self)

    def items(self):
        return [(key, self[key]) for key in self]

    def values(self):
        return [self[key] for key in self]

    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    def __ne__(self, other):
        return not self == other


class MappingView(Sized):

    def __init__(self, mapping):
        self._mapping = mapping
        return

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return ('{0.__class__.__name__}({0._mapping!r})').format(self)


class KeysView(MappingView, Set):

    @classmethod
    def _from_iterable(self, it):
        return set(it)

    def __contains__(self, key):
        return key in self._mapping

    def __iter__(self):
        for key in self._mapping:
            yield key

        return


class ItemsView(MappingView, Set):

    @classmethod
    def _from_iterable(self, it):
        return set(it)

    def __contains__(self, item):
        key, value = item
        try:
            v = self._mapping[key]
        except KeyError:
            return False

        return v == value
        return

    def __iter__(self):
        for key in self._mapping:
            yield (
             key, self._mapping[key])

        return


class ValuesView(MappingView):

    def __contains__(self, value):
        for key in self._mapping:
            if value == self._mapping[key]:
                return True

        return False

    def __iter__(self):
        for key in self._mapping:
            yield self._mapping[key]

        return


class MutableMapping(Mapping):

    @abstractmethod
    def __setitem__(self, key, value):
        raise KeyError
        return

    @abstractmethod
    def __delitem__(self, key):
        raise KeyError
        return

    __marker = object()

    def pop(self, key, default=__marker):
        try:
            value = self[key]
        except KeyError:
            if default is self.__marker:
                raise
            return default

        del self[key]
        return value
        return

    def popitem(self):
        try:
            key = next(iter(self))
        except StopIteration:
            raise KeyError

        value = self[key]
        del self[key]
        return (key, value)

    def clear(self):
        try:
            while True:
                self.popitem()

        except KeyError:
            pass

        return

    def update(*args, **kwds):
        if len(args) > 2:
            raise TypeError(('update() takes at most 2 positional arguments ({} given)').format(len(args)))
        elif not args:
            raise TypeError('update() takes at least 1 argument (0 given)')
        self = args[0]
        other = args[1] if len(args) >= 2 else ()
        if isinstance(other, Mapping):
            for key in other:
                self[key] = other[key]

        elif hasattr(other, 'keys'):
            for key in other.keys():
                self[key] = other[key]

        else:
            for key, value in other:
                self[key] = value

        for key, value in kwds.items():
            self[key] = value

        return

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default

        return default


MutableMapping.register(dict)

class Sequence(Sized, Iterable, Container):
    """All the operations on a read-only sequence.

    Concrete subclasses must override __new__ or __init__,
    __getitem__, and __len__.
    """

    @abstractmethod
    def __getitem__(self, index):
        raise IndexError
        return

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1

        except IndexError:
            return

        return

    def __contains__(self, value):
        for v in self:
            if v == value:
                return True

        return False

    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]

        return

    def index(self, value):
        for i, v in enumerate(self):
            if v == value:
                return i

        raise ValueError
        return

    def count(self, value):
        return sum(1 for v in self if v == value)


Sequence.register(tuple)
Sequence.register(basestring)
Sequence.register(buffer)
Sequence.register(xrange)

class MutableSequence(Sequence):

    @abstractmethod
    def __setitem__(self, index, value):
        raise IndexError
        return

    @abstractmethod
    def __delitem__(self, index):
        raise IndexError
        return

    @abstractmethod
    def insert(self, index, value):
        raise IndexError
        return

    def append(self, value):
        self.insert(len(self), value)
        return

    def reverse(self):
        n = len(self)
        for i in range(n // 2):
            self[i], self[n - i - 1] = self[n - i - 1], self[i]

        return

    def extend(self, values):
        for v in values:
            self.append(v)

        return

    def pop(self, index=-1):
        v = self[index]
        del self[index]
        return v

    def remove(self, value):
        del self[self.index(value)]
        return

    def __iadd__(self, values):
        self.extend(values)
        return self


MutableSequence.register(list)
return
