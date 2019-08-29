# -*- coding: utf-8 -*-
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


#from builtins import object
try:
    from redbaron import RedBaron
except Exception:
    RedBaron = False

from gnr.core.gnrbag import Bag

class GnrRedBaron(object):
    """docstring for GnrRedBaron"""
    child_types = {'class':True}

    def __init__(self, module=None):
        self.module = module
        if not RedBaron:
            raise Exception('Missing redbaron')
        with open(module,'r') as f:
            self.redbaron = RedBaron(f.read())

    def toTreeBag(self,node=None):
        node = node or self.redbaron
        result = Bag()
        for n in node:
            if n.type in self.child_types:
                result.setItem(n.name,None,caption=n.name,_type=n.type)



    def moduleToTree(self,module):
        pass

    def getModuleElement(self,module,element=None):
        pass

    def saveModuleElement(self,module,element=None):
        pass


if __name__ == '__main__':
    rb = GnrRedBaron('/Users/fporcari/sviluppo/genro//Users/fporcari/sviluppo/genro/resources/common/th/th_view.py')

