#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.web.gnrwebpage import GnrWebPage

class GnrCustomWebPage(object):
    py_requires='demo:Demo'
    
    def main(self, root, **kwargs):
        root.dbSelect(value='^anagrafica.id', dbtable='assopy.anagrafica',
                      width='20em',margin='10px',columns='ragione_sociale') 
                      #auxColumns='localita,provincia,cap,codice_fiscale,partita_iva')
        root.dataRecord('anagrafica.record', table='assopy.anagrafica', 
                                  pkey='^anagrafica.id')
                                  
        blocco_indirizzo=root.div(padding='5px',margin='10px',
                                   datapath='anagrafica.record')
        blocco_indirizzo.div('^.ragione_sociale',margin='4px' )
        blocco_indirizzo.div('^.indirizzo',margin='4px')
        ind = blocco_indirizzo.div()
        ind.span('^.cap',margin='4px')
        ind.span('^.localita', mask=' %s ',margin='4px')
        ind.span('^.provincia', mask='(%s)',margin='4px')
        blocco_indirizzo.div('^.@utente_id.email',margin='4px')
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
    
    
    
    
