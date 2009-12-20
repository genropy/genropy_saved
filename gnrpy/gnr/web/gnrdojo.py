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
    obj=DojoApiReader("/Users/gpo/sviluppo/genro/dojo_libs/dojo_13/dojo/api.xml")
    print obj.apibag.keys()
    print x