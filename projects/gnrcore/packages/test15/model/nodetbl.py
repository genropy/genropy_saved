# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('nodetbl',pkey='id',name_long='!!Node tbl',
                      name_plural='!!Node tbl')
        self.sysFields(tbl)
        tbl.column('partenza',size=':2',name_long='!!Partenza').relation('glbl.provincia.sigla', mode='foreignkey', onDelete='raise', 
                    many_name='Nodi',
                    one_name='Partenza')
        tbl.column('arrivo',size=':2',name_long='!!Arrivo').relation('glbl.provincia.sigla', mode='foreignkey', onDelete='raise', 
                    many_name='Nodi',
                    one_name='Arrivo')
        
        tbl.aliasColumn('reg_part',relation_path='@partenza.regione_nome',name_long='Regione partenza')
        tbl.aliasColumn('reg_arr',relation_path='@arrivo.regione_nome',name_long='Regione arrivo')

