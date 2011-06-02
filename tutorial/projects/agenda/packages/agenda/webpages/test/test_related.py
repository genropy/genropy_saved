# -*- coding: UTF-8 -*-

# test_related.py
# Created by Francesco Porcari on 2011-06-01.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        form = pane.frameForm(frameCode='tel',height='300px',store=True,table='agenda.telefonata',onSaved='reload',store_startKey='*newrecord*')
        tb = form.top.slotToolbar('selectrecord,*,|,semaphore,|,formcommands,|,locker')
        pane = form.record
        fb = pane.formbuilder(cols=3,fld_width='15em',lbl_color='teal')
        fb.field('giorno',name='!!Day',
                  width='6em')
        fb.field('ora',name='!!Hour',
                  width='6em')
        fb.field('username',readOnly=True,lbl='!!User',tooltip='The field is not editable')
       #fb.field('contatto_id',zoom=True,lbl='!!Caller',colspan=2,
       #          selected_azienda_id='.azienda_id',
       #          validate_notnull=True,validate_notnull_error='!!Required field')
        #fb.field('@contatto_id.@anagrafica_id.ragione_sociale')
        fb.field('@contatto_id.ruolo')
        