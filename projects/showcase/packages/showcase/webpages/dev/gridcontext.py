#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def main(self, root, **kwargs):
        root, top, bottom = self.pbl_rootTabContainer(root)

        self.test1(root.contentPane(title='test 1'))
        #self.test2(root.contentPane(title='test 2'))
        # 

    def test1(self, pane):
        self.setJoinCondition('ctxregione', from_fld='glbl.regione.sigla', target_fld='glbl.provincia.regione',
                              condition='$tbl.nome ILIKE :lettera',
                              lettera='^mycontext.lettera')
        pane.data('test.lettera', _serverpath='mycontext.lettera')
        pane.dataRecord('regione', 'glbl.regione', pkey='^regione_id', _if='pkey',
                        sqlContextName='ctxregione', _fired='^_reload_record')

        fb = pane.formbuilder(cols=1, border_spacing='4px')

        fb.dbSelect(dbtable='glbl.regione', value='^regione_id', lbl='regione', hasDownArrow=True)
        fb.textbox(value='^aux.lett', lbl='iniziale provincia')
        fb.dataController("SET test.lettera = lett+'%'; FIRE _reload_record;", lett="^aux.lett")
        grid = pane.div(width='100%', height='300px').IncludedView(struct=self._gridStruct(),
                                                                   storepath='regione.@glbl_provincia_regione')

    def test2(self, pane):
        pane.data('mycontext2', context='mycontext2')
        self.setJoinCondition('ctxregione2',
                              condition='$tbl.nome ILIKE :lettera',
                              lettera='^mycontext2.lettera')

        self.setJoinCondition('ctxregione2', from_fld='glbl.regione.sigla', target_fld='glbl.provincia.regione',
                              condition='$tbl.nome ILIKE :lettera',
                              lettera='^mycontext2.lettera')

        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^aux2.lett', lbl='iniziale')
        fb.dataController("SET mycontext2.lettera = lett+'%';", lett="^aux2.lett")

        pane.dataSelection('lista_regioni', 'glbl.regione', sqlContextName='ctxregione2', _fired='^mycontext2.lettera',
                           columnsFromView='regioni_grid')

        pane.div(width='100%', height='300px').IncludedView(struct=self._gridStruct2(),
                                                            storepath='lista_regioni', nodeId='regioni_grid')

        pane.div(width='100%', height='300px').IncludedView(struct=self._gridStruct(),
                                                            storepath='lista_regioni.r_0.@glbl_provincia_regione')


    def _gridStruct(self):
        struct = self.newGridStruct('glbl.provincia')
        r = struct.view().rows()
        r.fieldcell('sigla')
        r.fieldcell('nome')
        r.fieldcell('regione')
        r.fieldcell('@regione.nome')
        return struct

    def _gridStruct2(self):
        struct = self.newGridStruct('glbl.regione')
        r = struct.view().rows()
        r.fieldcell('sigla')
        r.fieldcell('nome')
        r.fieldcell('@glbl_provincia_regione.nome')
        return struct