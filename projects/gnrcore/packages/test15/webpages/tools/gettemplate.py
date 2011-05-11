# -*- coding: UTF-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_0_firsttest(self,pane):
        """First test description"""
        pane.dataRecord('.record','glbl.provincia',pkey='MI',_onStart=True)
        pane.div('==dataTemplate(_tpl,_record)',_tpl="""<div><span>$sigla $regione</span>
                                                        </div><div>$nome</div>""",_record='^.record')

    def test_1_firsttest(self,pane):
        """First test description"""
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.data('.pippo',55)
        pane.div(template="""<div><span>$sigla $regione</span>
                             </div><div>$nome</div> $pippo""",datasource='^.record',pippo='^.pippo')

    def test_2_firsttest(self,pane):
        """First test description"""
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.data('.pippo',55)
        pane.div(template="""<div><span>$sigla $regione</span>
                             </div><div>$nome</div> $pippo""",datasource='^.record',pippo='^.pippo')
    
    def test_3_firsttest(self,pane):
        fb = pane.formbuilder(cols=1)
        fb.numberTextbox(value='^.width')
        fb.textbox(value='^.pippo',width='==_width+_uu+"px";',_width='^.width',_uu=66,
                     onCreated='console.log("bazinga");')
        fb.checkbox(value='^.prova',lbl='disabled')
        fb.textbox(disabled='^.prova')
        fb.textbox(value='^.dis')
        fb.textbox(value='^.xxx',disabled='==_prova=="disabled";',_prova='^.dis',onCreated='console.log("bazinga");')
        

