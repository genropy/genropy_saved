#!/usr/bin/python

from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"
    def main(self,root,**kwargs):
        fb = root.formbuilder(cols=1,datapath='main',margin='10px')
        fb.checkbox(value='^.hasDownArrow',label='hasDownArrow')
        fb.dbSelect(value='^.regione',dbtable='glbl.regione',hasDownArrow='^.hasDownArrow',lbl='Regione')
        fb.dbSelect(value='^.provincia',dbtable='glbl.provincia',condition='$regione=:regione',
                    condition_regione='^.regione',  hasDownArrow='^.hasDownArrow',      
                    lbl='Provincia')
        fb.dbSelect(value='^.comune',dbtable='glbl.comune', auxColumns='$sigla_provincia,$altitudine,$popolazione_residente',
                    lbl='Comune', selected_altitudine='.altitudine')
        fb.textbox(value='^.altitudine', lbl='Altitudine')
