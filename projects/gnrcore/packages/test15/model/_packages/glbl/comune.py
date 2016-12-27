#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('comune')
        tbl.column('voto_si',dtype='B',name_long=u'!!Sì')
        tbl.column('voto_no',dtype='B',name_long='!!No')
        tbl.column('voto_astenuto',dtype='B',name_long='!!Astenuto')
        tbl.column('mill_si',dtype='L',name_long=u'!!Mill.Sì')
        tbl.column('mill_no',dtype='L',name_long=u'!!Mill.No')
        tbl.column('mill_ast',dtype='L',name_long=u'!!Mill.Ast.')
        tbl.formulaColumn('millesimi',select=dict(columns='SUM($popolazione_residente)',
                                                    where='$sigla_provincia=#THIS.sigla'),dtype='L')