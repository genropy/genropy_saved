# -*- coding: UTF-8 -*-

# speechinput.py
# Created by Francesco Porcari on 2012-05-08.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        fb.textbox(value='^.prova',speech=True,lbl='Textbox')
        fb.div('^.prova')
        fb.dbSelect(dbtable='glbl.provincia',value='^.provincia',lbl='Provincia',speech=True)
        fb.div('^.provincia')

        fb.simpleTextArea(value='^.note',height='300px',width='400px',lbl='Note',speech=True)
        fb.geoCoderField(lbl='Full Address',
                        selected_street_address='.street_address',selected_locality='.locality',
                        selected_postal_code='.zip',
                        selectedRecord='.addressbag',
                        colspan=2,width='100%',speech=True)
        fb.textbox(value='^.street_address',lbl='Route')
        fb.textbox(value='^.locality',lbl='Locality')
        fb.textbox(value='^.zip',lbl='Zip')
        