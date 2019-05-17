# -*- coding: utf-8 -*-
# 

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from time import time

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,services/pdfform/pdftk/component:PalettePdfFormEditor"
    
    def test_1_pdfformeditor(self, pane):
        bc = pane.borderContainer(height='500px')
        bc.pdfTkEditor(region='center',pdfFile='^.pdfFile', table='cond.mav',
            storepath='.pdfMapping')


    def test_2_pdfformpalette(self, pane):
        palette = pane.pdfFormEditorPalette(maintable='cond.mav',dockButton=True)

    def test_3_printpdfform(self, pane):
        bc = pane.borderContainer(height='500px')
        top = bc.contentPane(region='top', height='2em')
        fb = top.formbuilder(cols=3)
        fb.dbselect(value='^.tpl_id',dbtable='adm.userobject', 
            condition="$objtype=:ot AND $tbl=:tbl", 
            condition_ot='pdfform', condition_tbl='cond.mav',
            caption='$code')
        fb.dbselect(value='^.record_id',dbtable='cond.mav')
        fb.button('Stampa', action='FIRE .stampa')
        fb.dataRpc('.url', self.stampa, userObject='=.uo', record_id='=.record_id',
            _fired='^.stampa')
        bc.contentPane(region='center').iframe(src='^.url',height='100%',
                                        width='100%',border=0)

    @public_method
    def stampa(self, userObject=None, record_id=None, **kwargs):
        pdfform_service = self.site.getService('pdfform')
        output = self.site.storageNode('page:%s.pdf'%record_id)
        pdfform_service.fillFromUserObject(userObject=userObject,
            table='cond.mav', record_id=record_id, output=output)
        return output.url(nocache="%i"%time())