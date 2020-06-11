# -*- coding: utf-8 -*-

# remote.py
# Created by Francesco Porcari on 2011-05-01.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrbag import Bag

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''


    def test_0_rendertemplate(self,pane,**kwargs):
        pane.dbSelect(value='^.comune_id', dbtable='glbl.comune')
        pane.button('Stampa Sticker', action='FIRE .stampaSticker')
        pane.dataRpc(None, self.renderTemplate, _fired='^.stampaSticker',
                     table='glbl.comune',
                     record_id='=.comune_id',
                     tplname='sticker')


    def test_1_button(self,pane,**kwargs):
        """First test description"""
        pane.dbSelect(value='^.comune_id', dbtable='glbl.comune')
        pane.button('Stampa Sticker', action='FIRE .stampaSticker')
        pane.dataRpc(None, self.downloadTemplatePrint, _fired='^.stampaSticker',
                     table='glbl.comune',
                     record_id='=.comune_id',
                     tplname='sticker')

    @public_method
    def downloadTemplatePrint(self,table=None,tplname=None,letterhead_id=None,record_id=None,**kwargs):
        from gnr.web.gnrbaseclasses import TableTemplateToHtml
        htmlbuilder = TableTemplateToHtml(table=self.db.table(table))
        htmlbuilder(record=record_id,template=self.loadTemplate('%s:%s' %(table,tplname)))
        sn = self.site.storageNode('page:pippo.pdf')
        htmlbuilder.writePdf(sn)
        self.setInClientData(path='gnr.downloadurl',
                                    value=sn.url(),
                                    fired=True)
