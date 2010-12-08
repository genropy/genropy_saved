# -*- coding: UTF-8 -*-
# 
import datetime
from gnr.core.gnrbag import Bag

"""Menu"""

class GnrCustomWebPage(object):
    dojo_version='11'
    dojo_source =True
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme='tundra'
    
    def test_1_base(self,pane):
        """Basic"""
        menudiv = pane.div(height='50px',width='50px',background='lime')
        menu = menudiv.menu(action='alert($1.foo)',modifiers='*')
        menu.menuline('abc',foo=35)
        menu.menuline('xyz',foo=60,disabled=True)
        menu.menuline('alpha',action='alert("I am different")',checked=True)
        menu.menuline('-')
        submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
        submenu.menuline('cat',bar=35)
        submenu.menuline('dog',bar=60)
    
    def test_2_bag(self,pane):
        """From Bag"""
        menudiv = pane.div(height='50px',width='50px',background='lime')
        ddb = pane.dropDownButton('test')
        ddb.menu(action='alert($1.code)',modifiers='*',storepath='.menudata')
        menu = menudiv.menu(action='alert($1.code)',modifiers='*',storepath='.menudata')
        menu.data('.menudata',self.menudata())
        pane.checkbox(value='^.disabled',label='aa')
        pane.checkbox(value='^.checked',label='checked')
        pane.button('add menuline',action='this.setRelativeData(".menudata.r6",12,{"code":"PP","caption":"Palau port"})',
        disabled='^.disabled')
        
    def test_3_resolver(self,pane):
        """From Resolver"""
        
        ddm = pane.div(height='50px',width='50px',background='lime')
        menu = ddm.menu(action='alert($1.code)',modifiers='*',storepath='.menudata',_class='smallmenu',id='test3menu')
        ddm2 = pane.div(height='50px',width='50px',background='red',connectedMenu='test3menu')

        pane.dataRemote('.menudata','menudata',cacheTime=5)
        
    def rpc_menudata(self):
        menudata = self.menudata()
        menudata.setItem('r_6',None,code='PP',caption=str(datetime.datetime.now()))
        return menudata
        
    def menudata(self):
        result=Bag()
        result.setItem('r1',None,code='CA',caption='California')
        result.setItem('r2',None,code='IL',caption='Illinois',disabled=True)
        result.setItem('r3',None,code='NY',caption='New York',checked='^.checked')
        result.setItem('r4',None,code='TX',caption='Texas',disabled='^.disabled')
        result.setItem('r5',None,code='AL',caption='Alabama')
        return result
        




