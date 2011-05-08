# -*- coding: UTF-8 -*-

# contextname.py
# Created by Francesco Porcari on 2011-03-05.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    auto_polling=0
    user_polling=0
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def mystruct(self,struct):
        r = struct.view().rows()
        r.cell('sigla', name='Sigla', width='5em')
        r.cell('nome', name='Nome', width='15em')
        r.cell('regione', name='Regione', width='5em')
        r.cell('@regione.zona', name='Zona', width='5em')



    def test_0_firsttest(self,pane):
        """First test description"""
        pane = pane.contentPane(height='300px')
        pane.dataRecord('.myrecord','glbl.regione',pkey='LOM',_onStart=True)
        pane.includedView(storepath='.myrecord.@glbl_provincia_regione',
                            struct=self.mystruct,configurable=True,nodeId='mygrid')

    def rpc_pippo(self,selection):
        print 'eccomi'