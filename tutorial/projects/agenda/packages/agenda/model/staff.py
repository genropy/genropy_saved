# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('staff', pkey='id', rowcaption='@anagrafica_id.nome, @anagrafica_id.cognome: %s %s',
                          name_long='!!Staff', name_plural='!!Staff')
        self.sysFields(tbl)
        tbl.column('anagrafica_id',size=':22',name_long='!!Registry id').relation('sw_base.anagrafica.id', mode='foreignkey')
        tbl.column('user_id',size=':22',name_long='!!User').relation('adm.user.id',mode='foreignkey')
        tbl.column('interno',size=':15',name_long ='!!Intern')
        tbl.column('ruolo',size=':30',name_long ='!!Role')
        #tbl.aliasColumn()
        #tbl.aliasColumn()
        #tbl.formulaColumn('cognome_nome', "(@anagrafica_id.cognome OR @anagrafica_id.nome IS NOT NULL)", name_long='!!Cognome nome')