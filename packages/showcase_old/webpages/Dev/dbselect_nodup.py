#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os, datetime

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,public:IncludedView'
    def main(self, root, **kwargs):
        root, top, bottom = self.pbl_rootBorderContainer(root)
        
        root.data('form.canWrite', True)
        
        fb = root.contentPane(region='top', height='10ex').formbuilder(cols=2)
        fb.dbselect(dbtable='glbl.provincia', exclude='MI,TO', lbl='string')
        
        fb.dataFormula('lista_prov_exclude', "lista_prov.columns('provincia')[0]", lista_prov='^lista_prov',
                        _if='lista_prov', _else='null')
                        
        fb.dbselect(dbtable='glbl.provincia', exclude='=lista_prov_exclude', lbl='list')
        
        grid_bc = root.borderContainer(region='center')
        
        iv =self.includedViewBox(grid_bc,label=u'!!Province',autoWidth=True,
                                storepath='lista_prov',
                                nodeId='provGrid',
                                datamode='bag', add_action=True, del_action=True,
                                struct=self._gridStruct())

        gridEditor = iv.gridEditor()
        gridEditor.dbselect(gridcell='provincia', dbtable='glbl.provincia', exclude=True)
        
    def _gridStruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('provincia')
        r.cell('regione')
        return struct
            

