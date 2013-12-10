# -*- coding: UTF-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag,BagCbResolver,DirectoryResolver
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:ChunkEditor"

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
    
    def test_4_tableTemplate(self,pane):
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        pane.dataRecord('.record','glbl.provincia',pkey='^.pkey',_onStart=True)
        pane.div(template=self.tableTemplate('glbl.provincia','short'),datasource='^.record')
    
    def test_5_templateChunk(self,pane):
        pane.dbSelect(dbtable='glbl.regione',value='^.pkey',_class='gnrfield')
        pane.textbox(value='^ggg')

        rpc = pane.dataRecord('.record','glbl.regione',pkey='^.pkey')
        pane.templateChunk(innerHTML='^.piero',template='custom',table='glbl.regione',datasource='^.record',
                        tpl_test='^ggg',tpl_root='^*D',
                    height='100px',dataProvider=rpc,editable=True)


    def test_7_templateChunk_provincia(self,pane):
        pane.dbSelect(dbtable='glbl.provincia',value='^.pkey',_class='gnrfield')
        rpc = pane.dataRecord('.record','glbl.provincia',pkey='^.pkey')
        pane.templateChunk(template='custom',table='glbl.provincia',datasource='^.record',
                            height='100px',dataProvider=rpc)


    def test_9_templateChunk(self,pane):
        pane.dbSelect(dbtable='glbl.regione',value='^.pkey',_class='gnrfield')
        pane.textbox(value='^ggg')
        pane.div(nodeId='zzz')

        #rpc = pane.dataRecord('.record','glbl.regione',pkey='^.pkey')
        pane.templateChunk(innerHTML='^.piero',template='custom',table='glbl.regione',#datasource='^.record',
                        tpl_test='^ggg',tpl_root='^*D',record_id='^.pkey',
                    height='100px',#dataProvider=rpc,
                    editable=True)



    def test_6_templateChunkNoResource(self,pane):
        pane.dataRecord('.tipo_protocollo','studio.pt_tipo',pkey='PiWA-zDGMhSbDKS5AYRR5g',_onStart=True)
        
        pane.dbSelect(dbtable='studio.pt_protocollo',value='^.protocollo_esempio.pkey')
        rpc = pane.dataRecord('.protocollo_esempio.record','studio.pt_protocollo',pkey='^.protocollo_esempio.pkey')
        
        pane.templateChunk(template='^.tipo_protocollo.template_associato',
                            table='studio.pt_protocollo',editable=True,dataProvider=rpc,
                            datasource='^#FORM.protocollo_esempio.record', height='100px')


                    
    def test_z_formulasyntax(self,pane):
        fb = pane.formbuilder(cols=1)
        fb.numberTextbox(value='^.width')
        fb.textbox(value='^.pippo',width='==_width+_uu+"px";',_width='^.width',_uu=66,
                     onCreated='console.log("bazinga");')
        fb.checkbox(value='^.prova',lbl='disabled')
        fb.textbox(disabled='^.prova')
        fb.textbox(value='^.dis')
        fb.textbox(value='^.xxx',disabled='==_prova=="disabled";',_prova='^.dis',onCreated='console.log("bazinga");')
        
    
        

