#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):    
    def main(self, root, **kwargs):
        root.dbSelect(value='^anagrafica.id', dbtable='assopy.anagrafica',
                      width='20em',margin='10px',columns='ragione_sociale')
                     # auxColumns='@provincia.@regione.nome')
        root.dataRecord('anagrafica.record', table='assopy.anagrafica', 
                                  pkey='^anagrafica.id')
        blocco_indirizzo=root.div(padding='5px',margin='10px',width='30em',
                                  border='1px solid grey',height='6em',
                                  datapath='anagrafica.record')
        blocco_indirizzo.div('^.ragione_sociale',margin='4px' )
        blocco_indirizzo.div('^.indirizzo',margin='4px')
        ind = blocco_indirizzo.div()
        ind.span('^.cap',margin='4px')
        ind.span('^.localita', mask=' %s ',margin='4px')
        ind.span('^.provincia', mask='(%s)',margin='4px')
        blocco_indirizzo.div('^.@utente_id.email',margin='4px')
        treediv=root.div(padding='5px',margin='10px',height='20em',width='30em',
                                      border='1px solid grey',overflow='auto')
        treediv.tree(storepath='anagrafica.record', inspect='shift',
                                      visible='^anagrafica.id')
        
        
    
    
    
    
