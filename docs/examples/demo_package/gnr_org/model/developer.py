#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        tbl =  pkg.table('developer', name_long='!!Developer', rowcaption='nome,cognome')
        self.sysFields(tbl)
        tbl.column('user_id', size='22',name_long='!!User Id', indexed='y', group='_').relation('adm.user.id', many_name='!!Utente')
        tbl.column('nome', size=':32',name_long='!!Nome')
        tbl.column('cognome', size=':32',name_long='!!Cognome')
        tbl.column('ruolo', size=':20', name_long='!!Ruolo')
        tbl.column('email',name_long='!!Email')
        tbl.column('anagrafica_id',size='22',
                    name_long='!!Anagrafica',
                    group='_').relation('cdxbase.anagrafica.id', one_one=True)

    #def trigger_onInserting(self, record_data):
    #    tbl= self.db.table('adm.user')
    #    tbl.insert(record_data['@user_id'])
    #
    #
    #def trigger_onUpdating(self, record_data):
    #    
    #    tbl= self.db.table('adm.user')
    #    user_record=tbl.record(record_data['user_id']).output('bag')
    #    if record_data['email'] != user_record['email']:
    #        user_record['email']=record_data['email']
    #    if record_data['nome'] != user_record['firstname']:
    #        user_record['firstname']=record_data['nome']
    #    if record_data['cognome'] != user_record['lastname']:
    #        user_record['lastname']=record_data['cognome']
    #    tbl.update(user_record)
    #    
    #def trigger_onDeleting(self, record_data):
    #    tbl= self.db.table('adm.user')
    #    tbl.delete(tbl.record(record_data['user_id']).output('bag'))

