#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        tbl =  pkg.table('utente',  pkey='id', name_long='!!Utente', 
                            name_plural='!!Utenti',
                            rowcaption='nome_cognome,email:%s (%s)')
                            
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('username', size=':32',name_long='!!Username')
        tbl.column('email',name_long='!!Email')
        tbl.column('nome_cognome', size=':32',name_long='!!Nome Cognome')
        tbl.column('data_registrazione', 'D' ,name_long='!!Data di registrazione')
        tbl.column('auth_tags', name_long='!!Ruoli')
        tbl.column('stato', name_long='!!Stato', size=':12')
        tbl.column('pwd', name_long='PasswordMD5', size='32')
        tbl.column('locale', name_long='!!Lingua', size=':12')
        

