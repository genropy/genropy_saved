# -*- coding: utf-8 -*-

"""Menu"""

import datetime
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrsys import expandpath

class GnrCustomWebPage(object):
    dojo_version = '11'
    dojo_source = True
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    
    def test_1_base(self, pane):
        """Basic"""
        ddb = pane.dropdownbutton('Menu')
        menu = ddb.menu(action='alert($1.foo)',modifiers='*')
        menu.menuline('Save',foo='Saved!')
        menu.menuline('Save As...',foo=60)
        menu.menuline('Load',action='alert("I\'m different")')
        menu.menuline('-')
        submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
        submenu.menuline('cat',bar=35)
        submenu.menuline('dog',bar=60)

    def test_11_base(self, pane):
        pane.checkbox(value='^.disabled')
        pane.menudiv(disabled='^.disabled',storepath='.menudata',iconClass='add_row',label='Piero')
        pane.dataRemote('.menudata', 'menudata', cacheTime=5)

    def test_12_menudiv_caption(self, pane):
        #pane.data('.opzione','p',label='Pippo')
        pane.menudiv(value='^.opzione',values='p:Pippo,z:Zio,r:Rummo,g:Gennaro o pizzaiolo',
                    placeholder='Scegli',color='red',font_size='20px')

    def test_2_base(self, pane):
        """Basic 2"""
        menudiv = pane.div('-MENU-',height='20px',width='50px',background='teal')
        menu = menudiv.menu(action='alert($1.foo)')
        menu.menuline('abc',foo=35)
        menu.menuline('xyz',foo=60,disabled=True)
        menu.menuline('alpha',action='alert("I\'m different")',checked=True)
        menu.menuline('-')
        submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
        submenu.menuline('cat',bar=35)
        submenu.menuline('dog',bar=60)
        

    def test_20_base(self, pane):
        """Basic 2"""
        bc = pane.borderContainer(height='400px')
        th = bc.contentPane(region='center').plainTableHandler(table='glbl.provincia',view_store_onStart=True)
 

    def test_3_bag(self, pane):
        """From Bag"""
        menudiv = pane.div(height='50px',width='50px',background='lime')
        ddb = pane.dropDownButton('test')
        ddb.menu(action='alert($1.code)',modifiers='*',storepath='.menudata')
        menu = menudiv.menu(action='alert($1.code)',modifiers='*',storepath='.menudata')
        menu.data('.menudata',self.menudata())
        pane.checkbox(value='^.disabled',label='disable button')
        pane.checkbox(value='^.checked',label='checked')
        pane.button('add menuline',
                    action='this.setRelativeData(".menudata.r6",12,{"code":"PP","caption":"Palau port"})',
                    disabled='^.disabled')
                    
    def test_4_resolver(self, pane):
        """From Resolver"""
        ddm = pane.div(height='50px', width='50px', background='lime')
        menu = ddm.menu(action='alert($1.code)', modifiers='*', storepath='.menudata', _class='smallmenu',
                        id='test3menu')
        ddm2 = pane.div(height='50px', width='50px', background='red', connectedMenu='test3menu')
        pane.dataRemote('.menudata', 'menudata', cacheTime=5)
        
    def test_7_dir_resolver(self,pane):
        #d = DirectoryResolver(,cacheTime=10,include='*.py', exclude='__*,.*',dropext=True,readOnly=False)()
        pane.data('.store',DirectoryResolver(expandpath('~/sviluppo'),cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)()
                            )

        ddm = pane.div(height='50px', width='50px', background='lime')
        ddm.menu(action='console.log($1)', modifiers='*', storepath='.store', _class='smallmenu',
                        id='test99menu')

    def test_5_resolver(self, pane):
        """From resolver user"""
        ddm = pane.div(height='50px', width='50px', background='lime')
        ddm.menu(action='alert($1.code)', modifiers='*', storepath='.menudata', _class='smallmenu',
                        id='test3menu')
        pane.dataRemote('.menudata', 'connection.connected_users_bag', cacheTime=5)

    def test_6_resolver(self, pane):
        """From resolver user"""
        ddm = pane.div(height='50px', width='50px', background='lime')
        ddm.menu(action='alert($1.code)', modifiers='*', storepath='.menudata', _class='smallmenu',
                        id='test3menu')
        pane.textbox(value='^.pippo')
        pane.dataRemote('.menudata', self.testcb,cacheTime=0,zzz='=.pippo')

    def test_99_menucolor(self, pane):
        pane.css('.colorMenuLine',"height:10px;width:50px")

        pane.div(height='20px',width='20px',
                    border='1px solid silver',background='^.color').menu(contentCb="""
                    var result = new gnr.GnrBag();

                    result.setItem('r_1',null,{code:'red',caption:'div class="colorMenuLine" style="background:red;">&nbsp;</div>'})
                    result.setItem('r_2',null,{code:'green',caption:'div class="colorMenuLine" style="background:green;">&nbsp;</div>'})
                    return result;
                    """,
                    action='SET .color=$1.code',modifiers='*',_class='smallmenu')



    @public_method
    def testcb(self,zzz=None):
        print 'mmmm'
        menudata = self.menudata()
        menudata.setItem('r_6', None, code=zzz or 'zzz', caption=zzz)
        return menudata

    def rpc_menudata(self):
        menudata = self.menudata()
        menudata.setItem('r_6', None, code='PP', caption=str(datetime.datetime.now()))
        return menudata

    def menudataColors(self):
        result = Bag()
        result.setItem('r1', None, code='red', caption='<div class="colorMenuLine" style="background:red;">&nbsp;</div>')
        result.setItem('r2', None, code='green', caption='<div class="colorMenuLine" style="background:green;">&nbsp;</div>')
        result.setItem('r3', None, code='navy', caption='<div class="colorMenuLine" style="background:navy;">&nbsp;</div>')
        return result

    def menudata(self):
        result = Bag()
        result.setItem('r1', None, code='CA', caption='California')
        result.setItem('r2', None, code='IL', caption='Illinois', disabled=True)
        result.setItem('r3', None, code='NY', caption='New York', checked='^.checked')
        result.setItem('r4', None, code='TX', caption='Texas', disabled='^.disabled')
        result.setItem('r5', None, code='AL', caption='Alabama')
        return result
        
    def test_101_menuEdit(self, pane):
        ddm = pane.div(height='50px', width='50px', background='lime')
        m = ddm.menu(modifiers='*', _class='menupane')
        m.menuItem(label='Line 1')
        box = m.menuItem().div(max_height='350px',min_width='300px',overflow='auto')
        box.horizontalSlider(value='^.scaleX',width='8em',intermediateChanges=True)
        box.verticalSlider(value='^.scaleY',height='8em',intermediateChanges=True)
        m.menuItem(label='Line last')

        pane.div('^.scaleX')
        pane.div('^.scaleY')