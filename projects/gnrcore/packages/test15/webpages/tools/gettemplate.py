# -*- coding: UTF-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag,BagCbResolver,DirectoryResolver
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_1_template_a(self,pane):
        """First test description"""
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.data('.pippo',55)
        pane.div(template="""<div><span>$sigla $regione</span>
                             </div><div>$nome</div> $pippo""",datasource='^.record',pippo='^.pippo')

    def test_2_template(self,pane):
        """First test description"""
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.data('.pippo',55)
        pane.div(template="""<div><span>$sigla $regione</span>
                             </div><div>$nome</div> $pippo""",datasource='^.record',pippo='^.pippo')
                             
    def test_3_template(self,pane):
        """First test description"""
        #pane.div('aaa')
        pane.textbox(value='^.template_name',default_value='demotpl1.html')
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.data('.pippo',55)
        pane.dataResource('.remote_tpl',resource='^.template_name')
        pane.div(template='^.remote_tpl',datasource='^.record',pippo='^.pippo')
    


    def test_z_formulasyntax(self,pane):
        fb = pane.formbuilder(cols=1)
        fb.numberTextbox(value='^.width')
        fb.textbox(value='^.pippo',width='==_width+_uu+"px";',_width='^.width',_uu=66,
                     onCreated='console.log("bazinga");')
        fb.checkbox(value='^.prova',lbl='disabled')
        fb.textbox(disabled='^.prova')
        fb.textbox(value='^.dis')
        fb.textbox(value='^.xxx',disabled='==_prova=="disabled";',_prova='^.dis',onCreated='console.log("bazinga");')
        
    
        

