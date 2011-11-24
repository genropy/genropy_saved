# -*- coding: UTF-8 -*-
"""DropDownButton"""

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    
    def test_1_basic(self,pane):
        """simple dropdownbutton"""
        fb = pane.formbuilder()
        fb.div('DropDownButton is used to build a menu')
        fb.br()
        fb.div('1) A dropdownbutton with a label')
        ddb = fb.dropdownbutton(label='Save')
        dmenu = ddb.menu()
        dmenu.menuline('Save', action="alert('Saved')")
        dmenu.menuline('Save as...', action="alert('Saved as...')")
        
        fb.div("""2) You can also give to the dropdownbutton the iconClass attribute
                     and CSS attributes (like in this case, the\"height\" attribute)""")
        ddb = fb.dropdownbutton(label='Load', height='30px', width='7em', iconClass='iconbox storage')
        dmenu = ddb.menu()
        dmenu.menuline('Load template', action="alert('Loaded from template')")
        dmenu.menuline('Load from file', action="alert('Loaded from file')")