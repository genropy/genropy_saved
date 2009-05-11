#!/usr/bin/env python
# encoding: utf-8
import os

from gnr.core.gnrbag import Bag

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
from gnr.core.gnrstring import templateReplace, splitAndStrip

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='assopy',
                    comment='assopy package',
                    name_short='assopy',
                    name_long='assopy',
                    name_full='assopy')

    def config_db(self, pkg):
        pass

    def authenticate(self, username):
        result = self.application.db.query('assopy.utente', columns='*',
                                           where='$username = :user AND $stato != :provv', user=username, provv='provvisorio').fetch()
        if result:
            result = dict(result[0])
            result['tags'] = result.pop('auth_tags')
            result['userid'] = result['id']
            result['id'] = username            
            return result
            
            
    def onAuthentication(self, avatar): 
        result = self.application.db.query(table='assopy.socio', columns='*', where='@anagrafica_id.utente_id = :userid', 
                                        userid = avatar.userid).fetch() 
        if result: 
            avatar.assopy_socio = result[0] 
            avatar.addTags('socio')
        
        result = self.application.db.query(table='assopy.partecipante', columns='$id',  
                                                 where="""@ordine_riga_id.@ordine_id.@anagrafica_id.utente_id = :userid 
                                                 AND @ordine_riga_id.@ordine_id.data_conferma is not null """, 
                                                  userid = avatar.userid).fetch() 
        if result: 
            avatar.addTags('partecipanti') 

        result = self.application.db.query(table='assopy.talk', columns='$id',  
                                                 where='@oratore_id.@anagrafica_id.utente_id = :userid', 
                                                  userid = avatar.userid).fetch() 
        if result: 
            avatar.addTags('candidatoOratore')

    
class Table(GnrDboTable):
    pass




