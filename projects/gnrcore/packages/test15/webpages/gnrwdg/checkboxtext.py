# -*- coding: UTF-8 -*-

# checkboxgroup.py
# Created by Francesco Porcari on 2011-06-24.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"

    def windowTitle(self):
        return ''
         
    def test_0_mode_values(self,pane):
        """First test description"""
        pane.checkBoxText(value='^.pluto',values='Foo,Bar,/,Span,Mol,Tol,Rol,Cor,Sar',
                    table_border_spacing='10px',label_color='red',cols=3)
        pane.textbox(value='^.pluto')
    
    def test_1_mode_codes(self,pane):
        """First test description"""
        pane.checkBoxText(values='foo:Foo,bar:Bar,span:Span',value='^.pluto')
        pane.textbox(value='^.pluto')
        pane.textbox(value='^.pluto?value_caption')

    def test_2_mode_codes(self,pane):
        """First test description"""
        pane.radioButtonText(values='foo:Foo,bar:Bar,span:Span',value='^.pluto',group='test')
        pane.textbox(value='^.pluto')
        pane.textbox(value='^.pluto?value_caption')

    def test_3_multicbpopup(self,pane):
        pane.checkbox(value='^.disabled',label='disabled')
        #pane.checkbox(value='^.readonly',label='readonly')

        pane.checkBoxText(values="""0:Lunedì\\2,1:Mar,2:Mer,3:Gio,4:Ven,5:Sab,6:Dom""",
        value='^.pluto',cols=3,popup=True,disabled='^.disabled',readOnly=True)
                            
    def test_4_mode_numbcode(self,pane):
        """First test description"""
        pane.checkBoxText(values='0:Foo,1:Bar,2:Span',value='^.pluto',separator=' -     ')
        pane.textbox(value='^.pluto')
        pane.textbox(value='^.pluto?value_caption')

    def test_5_multicb(self,pane):
        pane.checkBoxText(values="""0:Foo,1:Bar,/,3:Span,4:Zum,5:Pap,6:Mas,/,8:Ilo""",value='^.pluto')
        


    def test_6_mode_values(self,pane):
        """First test description"""
        pane.data('.values','M:Maschio,F:Femmina')
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.checkBoxText(values='^.values',value='^.pluto')
        fb.textbox(value='^.pluto',lbl='code')
        fb.textbox(value='^.pluto?_displayedValue',lbl='Caption')

        fb.textbox(value='^.values',lbl='Values')

    def test_7_mode_values(self,pane):
        """First test description"""
        pane.data('.values','M:Maschio,F:Femmina')
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.radioButtonText(values='^.values',value='^.pluto')
        fb.textbox(value='^.pluto',lbl='code')
        fb.textbox(value='^.pluto?_displayedValue',lbl='Caption')

        fb.textbox(value='^.values',lbl='Values')   


    def test_10_mode_table(self,pane):
        """First test description"""
        pane.checkBoxText(value='^.pluto',table='adm.user',popup=True,disabled=True)
        pane.checkbox(value='^.disabled',label='disabled')
        pane.checkBoxText(value='^.paperino',table='adm.user',popup=True,disabled='^.disabled')

        pane.textbox(value='^.pluto')
   
    def test_11_mode_table(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='400px')
        def struct(struct):
            r = struct.view().rows()
            r.cell('users_pkeys',name='users',edit=dict(tag='checkBoxText',table='adm.user'),width='40em',caption_field='users')

        bc.contentPane(region='center').bagGrid(storepath='main.test',struct=struct)

    def test_12_testhatag(self,pane):
        """First test description"""
        pane.button('TEST',action='SET .tag="admin,manager";')
        pane.checkBoxText(value='^.tag',table='adm.htag',popup=True,hierarchical=True,alt_pkey_field='code',
                            labelAttribute='code')

   
    def test_13_localization(self,pane):
        pane.checkBoxText(values="fatt:[!![it]Fattura],cli:[!![it]Cliente]",value='^.cbt',popup=True)
        pane.filteringSelect(values="fatt:!![it]Fattura,cli:!![it]Cliente",value='^.flt')
        pane.multiButton(values="fatt:!![it]Fattura,cli:!![it]Cliente",value='^.mb')

    def test_14_mode_valuesCb(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.source',lbl='Source for cb')
        fb.checkBoxText(value='^.currval',
                        valuesCb="""var result = [];
                            source = this.getRelativeData('.source');
                            source = source?source.split(','):['Foo','Bar','Span'];
                            source.forEach(function(n,idx){
                                var code = 'val_'+idx;
                                result.push(code+':'+n);
                            });
                            return result.join(',');
                        """,lbl='Checkbox dynamic')
        fb.textbox(value='^.currval',lbl='val')
        fb.textbox(value='^.currval?_displayedValue',lbl='val caption')

