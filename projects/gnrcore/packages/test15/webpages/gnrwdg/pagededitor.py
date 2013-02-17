# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import TableTemplateToHtml
import tempfile


class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/pagededitor/pagededitor:PagedEditor"""
    
         
    def test_0_base(self,pane):
        """basic"""
        frame = pane.framePane(height='600px')
        #frame.script('genro.newCkeditor=true;')
        fb = frame.top.slotBar('5,fb,*')
        fb = frame.top.bar.fb.formbuilder(cols=4,border_spacing='3px')
        fb.dbselect(value='^.letterhead_id',dbtable='adm.htmltemplate',hasDownArrow=True)
        fb.dbselect(value='^.following_id',dbtable='adm.htmltemplate',hasDownArrow=True)
        fb.dataController('SET .letterhead_pkeys=following_id?letterhead_id+","+following_id:letterhead_id;',letterhead_id='^.letterhead_id',following_id='^.following_id',_if='letterhead_id')
        #fb.dataRpc()
        pe = frame.pagedEditor(value='^.test_0_base',border='1px solid silver',letterhead_id='^.letterhead_pkeys',pagedText='^.pagedText',printAction=True)

        fb.button('Add page',action='pe._pe_manager.addPage();',pe=pe)

    def test_1_letterhead(self,pane):
        frame = pane.framePane(height='600px')
        fb = frame.top.slotBar('5,fb,*')
        fb = fb.formbuilder(cols=2,border_spacing='3px')
        fb.dbselect(value='^.letterhead_id_1',dbtable='adm.htmltemplate',hasDownArrow=True)
        fb.dbselect(value='^.letterhead_id_2',dbtable='adm.htmltemplate',hasDownArrow=True)
        fb.dataRpc('.result',self.mixLetterhead,letterhead_id_1='^.letterhead_id_1',letterhead_id_2='^.letterhead_id_2')


    @public_method
    def mixLetterhead(self,letterhead_id_1=None,letterhead_id_2=None):
        tblobj = self.db.table('adm.htmltemplate')
        result = ''
        pkeys = []
        if letterhead_id_1:
            pkeys.append(letterhead_id_1)
        if letterhead_id_2:
            pkeys.append(letterhead_id_2)
        if pkeys:
            result = tblobj.getHtmlBuilder(pkeys)
        return result

