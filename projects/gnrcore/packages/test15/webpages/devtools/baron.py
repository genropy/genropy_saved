# -*- coding: UTF-8 -*-
"""Red Baron test"""

import sys
from gnr.core.gnrdecorator import public_method
from redbaron import RedBaron
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_readcode(self, pane):
        """Basic button"""
        bc=pane.borderContainer(height='500px')
        top=bc.contentPane(region='top',height='60px',background='silver')
        left=bc.contentPane(region='left',width='250px')
        center=bc.contentPane(region='center')
        fb=top.formbuilder(cols=3)
        fb.textBox(value='^.modulepath',lbl='Module path')
        fb.button('Read',fire='.readcode')
        top.dataRpc('.codeTree',self.readCode,modulepath='=.modulepath',_fired='^.readcode')
        left.tree(storepath='.codeTree')
        
        
    @public_method
    def readCode(self,modulepath=None):
        result=Bag()
        modulepath=modulepath or sys.modules[self.__module__].__file__
        with open(modulepath, "r") as source_code:
            red = RedBaron(source_code.read())
        result.fromJson(red.fst())
        return result
            


    def baronToBag(self,fred,formatting=False):
        if isinstance(fred,dict):
            fred = dict(fred)
            value = fred.pop('value',None)
            t = fred.pop('type')
            if not formatting:
                fred = dict([(k,v) for k,v in fred.items() if not k.endswith('_formatting')])
            value = getattr(self,'baronToBag_%s' %t,self.baronToBag_default)(value,fred)
            return (t,value,fred)
        elif isinstance(fred,list):
            result = Bag()
            for f in fred:
                label,value,attrs = self.baronToBag(f,formatting=formatting)
                if isinstance(value,tuple):
                    l,v,a = value
                    value = Bag()   
                    value.setItem(l,v,**a)                 
                result.addItem(label,value,**attrs)
            return result
        else:
            return fred

    def baronToBag_default(self,value,attributes):
        return self.baronToBag(value)

    def baronToBag_call(self,value,attributes):
        args = []
        kwargs = dict()
        for v in value:
            if v['type'] =='call_argument':
                target,value = v['target'].get('value'),v['value']['value']
                if not target:
                    args.append(value)
                else:
                    kwargs[target] = value
        attributes['args'] = args
        attributes['kwargs'] = kwargs


