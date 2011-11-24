# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrdict : gnrdict implementation
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

def dictExtract(mydict, prefix, pop=False, slice_prefix=True):
    """Return a dict of the items with keys starting with prefix.
    
    :param mydict: sourcedict 
    :param prefix: the prefix of the items you need to extract
    :param pop: removes the items from the sourcedict
    :param slice_prefix: shortens the keys of the output dict removing the prefix
    :returns: a dict of the items with keys starting with prefix"""
    lprefix = len(prefix) if slice_prefix else 0
    
    cb = mydict.pop if pop else mydict.get
    reserved_names = ['class']
    return dict([(k[lprefix:] if not k[lprefix:] in reserved_names else '_%s' %k[lprefix:], cb(k)) for k in mydict.keys() if k.startswith(prefix)])

class FakeDict(dict):
    pass

class GnrDict(dict):
    """An ordered dictionary"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._list = []
        if args:
            source = args[0]
            if hasattr(source, 'items'):
                [self.__setitem__(k, v) for k, v in source.items()]
            else:
                [self.__setitem__(k, v) for k, v in source]
        if kwargs:
            [self.__setitem__(k, v) for k, v in kwargs.items()]
            
    def __setitem__(self, key, value):
        key = self._label_convert(key)
        if not key in self:
            self._list.append(key)
        dict.__setitem__(self, key, value)
        
    def __iter__(self):
        return self._list.__iter__()
        
    def __delitem__(self, key):
        key = self._label_convert(key)
        self._list.remove(key)
        dict.__delitem__(self, key)
        
    def get(self, label, default=None):
        """TODO
        
        :param label: TODO
        :param default: TODO"""
        return dict.get(self, self._label_convert(label), default)
        
    def __getitem__(self, label):
        return dict.__getitem__(self, self._label_convert(label))
        
    def _label_convert(self, label):
        if isinstance(label, basestring) and label.startswith('#') and label[1:].isdigit():
            label = self._list[int(label[1:])]
        return label
        
    def items(self):
        """TODO"""
        return [(k, self[k]) for k in self._list]
        
    def keys(self):
        """TODO"""
        return list(self._list)
        
    def index(self, value):
        """TODO"""
        if value in self._list:
            return self._list.index(value)
        return -1
        
    def values(self):
        """TODO"""
        return [self[k] for k in self._list]
        
    def pop(self, key, dflt=None):
        """TODO
        
        :param key: TODO
        :param dflt: TODO"""
        key = self._label_convert(key)
        if key in self._list:
            self._list.remove(key)
            return dict.pop(self, key)
        return dflt
        
    def __str__(self):
        return "{%s}" % (', '.join(["%s: %s" % (repr(k), repr(self[k])) for k in self._list]))
        
    __repr__ = __str__
        
    #def __repr__(self):
    #return "%s ordered on %s" % (dict.__repr__(self), str(self._list))
        
    def clear(self):
        """TODO"""
        self._list[:] = []
        dict.clear(self)
        
    def update(self, o, removeNone=False):
        """TODO
        
        :param o: TODO
        :param removeNone: TODO"""
        [self.__setitem__(k, v) for k, v in o.items()]
        if removeNone:
            [self.__delitem__(k) for k, v in o.items() if v == None]
            
    def copy(self):
        """TODO"""
        return GnrDict(self)
        
    def setdefault(self, key, d=None):
        """TODO
        
        :param key: TODO
        :param d: TODO"""
        key = self._label_convert(key)
        if not key in self:
            self.__setitem__(key, d)
        return self[key]
        
    def popitem(self):
        """TODO"""
        k = self._list.pop()
        return (k, dict.pop(self, k))
        
    def iteritems(self):
        """TODO"""
        for k in self._list:
            yield (k, self[k])
            
    def iterkeys(self):
        """TODO"""
        for k in self._list:
            yield k
            
    def itervalues(self):
        """TODO"""
        for k in self._list:
            yield self[k]
            
    def __add__(self, o):
        return GnrDict(self.items() + o.items())
        
    def __sub__(self, o):
        return GnrDict([(k, self[k]) for k in self if not k in o])
        
    def __getslice__(self, start=None, end=None):
        return GnrDict([(k, self[k]) for k in self._list[start:end]])
        
    def __setslice__(self, start=None, end=None, val=None):
        [dict.__delitem__(self, k) for k in self._list[start:end]]
        val = GnrDict(val)
        l = list(self._list)
        newkeys = val.keys()
        newkeysrange = range(start, start + len(newkeys))
        l[start:end] = newkeys
        self._list[:] = [x for i, x in enumerate(l) if (x not in newkeys) or i in newkeysrange]
        dict.update(self, val)
        
    def reverse(self):
        """TODO"""
        self._list.reverse()
        
    def sort(self, cmpfunc=None):
        """TODO
        
        :param cmpfunc: TODO"""
        self._list.sort(cmpfunc)
        
class GnrNumericDict(GnrDict):
    """TODO"""
    def __getitem__(self, label):
        if isinstance(label, int):
            return dict.__getitem__(self, self._list[label])
        else:
            return dict.__getitem__(self, self._label_convert(label))
            
    def __iter__(self):
        for k in self._list:
            yield self[k]
            
if __name__ == '__main__':
    a = GnrDict([('pino', 55), ('gionni', 88)], ugo=56, mario=False)
    print a.get('#1')
    try:
        print a['gvhjf hvj']
    except:
        print 36