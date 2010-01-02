# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbag : an advanced data storage system
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

from gnr.core.gnrbag import Bag

class DojoApiReader(object):
    def __init__(self,apipath):
        b=Bag(apipath)
        self.p=[]
        self.apibag=Bag()
        self.convert(b['javascript'])

        
    def convert(self, src,destpath=''):
        for node in src:
            label=node.label
            node_value = node.value
            attr=dict(node.attr)
            handler=getattr(self,'cpl_%s'%label,None)
            if not handler:
                print label
            else:
                label,node_value=handler(label,node_value,attr,destpath)
                if node_value and isinstance(node_value, Bag):
                    self.convert(node_value,label)
                    value=None
                else:
                    value=node_value
            self.p.append ((label,value,attr))
            curr=self.apibag.getNode(label)
            if not curr:
                self.apibag.setItem(label,value,attr)
            else:
                curr.attr.update(attr)

    def cpl_object(self,label,node_value,attr,destpath):
        return attr['location'],node_value
    
    def cpl_properties(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_methods(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_parameters(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_mixins(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_description(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_example(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,label),node_value
    
    def cpl_property(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,attr['name']),node_value
    
    def cpl_parameter(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,attr['name']),node_value,None
    
    def cpl_method(self,label,node_value,attr,destpath):
        return '%s.%s'%(destpath,attr.get('name') or 'noname'),None
    
    def cpl_mixin(self,label,node_value,attr,destpath):
        return attr['location'],None
    
if __name__=='__main__':
    obj=DojoApiReader("/Users/gpo/sviluppo/Dojo/dojo_14/api.xml")
    print obj.apibag.keys()
    print x