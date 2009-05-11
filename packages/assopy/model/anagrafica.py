#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('anagrafica',  pkey='id',name_long='!!Anagrafica', name_plural='!!Anagrafiche',
        rowcaption='ragione_sociale,provincia:%s (%s)')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('ragione_sociale', size=':60',name_long='!!Ragione sociale')
        tbl.column('codice_fiscale', size=':16',name_long='!!Codice fiscale')
        tbl.column('partita_iva', size=':16',name_long='!!Partita iva')
        tbl.column('titolo', size=':10',name_long='!!Titolo')
        #tbl.column('civico',size=':10',name_long='!!Civico')
        tbl.column('localita', size=':40',name_long=u'!!Località')       
        tbl.column('localita', size=':40',name_long=u'!!Località')                                                                    
        tbl.column('provincia', size=':3',name_long='!!Provincia').relation('glbl.provincia.sigla')
        tbl.column('cap', size=':5',name_long='!!CAP')
        tbl.column('nazione', size='2',name_long='!!Nazione').relation('glbl.nazione.code')
        tbl.column('recapiti', dtype='X',name_long='Recapiti tel-fax-email')
        tbl.column('cellulare', size=':20',name_long='!!Cellulare')
        tbl.column('tipo_cliente', size=':14',name_long='!!Tipo Cliente').relation('coge.tipo_cliente.codice')
                                                                           
        tbl.column('tipo_iva',size=':14',name_long='Tipo IVA').relation('coge.tipo_iva.codice')
        tbl.column('cond_pagamento', size=':14',                        
                   name_long='Condizioni di pagamento').relation('coge.condizioni_di_pagamento.codice')
        
        tbl.column('coge_id', 'A',size=':10',
                   name_long='Id coge').relation('coge.clienti.sy_id')
        
        tbl.column('ut_anagrafiche_id', 'A',size=':10',
                   name_long='Id ut_anagrafiche').relation('ut.anagrafiche.sy_id')

        tbl.column('utente_id', size='22',name_long='!!Utente').relation('assopy.utente.id', one_one=True, mode='foreignkey')
        tbl.column('esenzione_iva', 'T',name_long='!!Esenzione IVA')
        #tbl.column('privacy', 'B', name_long='!!Firma privacy')
        
        tbl.aliasColumn('username', '@utente_id.username', name_long=u'!!Nome Utente')
        tbl.aliasColumn('email', '@utente_id.email', name_long=u'!!Email')
        tbl.formulaColumn('geolocator', "indirizzo || ',' || localita || ',' || nazione", name_long='!!Geolocator')
        
    def js_validate_partitaIva(self):
        js=u"""var pi = $1;
                var error_msg;
                if( pi == '' )  return true;
                if('0123456789'.indexOf(pi[0])<0) return true;
                if( pi.length != 11 )
                        return false;
                var validi = "0123456789";
                for(var i = 0; i < 11; i++ ){
                        if( validi.indexOf( pi.charAt(i) ) == -1 )
                                return false;
                }
                var s = 0;
                for(var i = 0; i <= 9; i += 2 )
                        s += pi.charCodeAt(i) - '0'.charCodeAt(0);
                for(var i = 1; i <= 9; i += 2 ){
                        var c = 2*( pi.charCodeAt(i) - '0'.charCodeAt(0) );
                        if( c > 9 )  c = c - 9;
                        s += c;
                }
                if( ( 10 - s%10 )%10 != pi.charCodeAt(10) - '0'.charCodeAt(0) ){
                        return false;
                }
                return true;
                """
        return js
    
    def js_validate_codiceFiscale(self):
        js=u"""var value = $1;
var validate_piva = function(pi){
                    var error_msg;
                    if( pi == '' )  return true;
                    if( pi.length != 11 )
                            return false;
                    var validi = "0123456789";
                    for(var i = 0; i < 11; i++ ){
                            if( validi.indexOf( pi.charAt(i) ) == -1 )
                                    return false;
                    }
                    var s = 0;
                    for(var i = 0; i <= 9; i += 2 )
                            s += pi.charCodeAt(i) - '0'.charCodeAt(0);
                    for(var i = 1; i <= 9; i += 2 ){
                            var c = 2*( pi.charCodeAt(i) - '0'.charCodeAt(0) );
                            if( c > 9 )  c = c - 9;
                            s += c;
                    }
                    if( ( 10 - s%10 )%10 != pi.charCodeAt(10) - '0'.charCodeAt(0) ){
                            return false;
                    }
                    return true;
                };
var validate_cf = function(cf){
                    var validi, i, s, set1, set2, setpari, setdisp;
                    if( cf == '' )  return true;
                    cf = cf.toUpperCase();
                    if( cf.length != 16 )
                    	return false;
                    validi = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                    for( i = 0; i < 16; i++ ){
                    	if( validi.indexOf( cf.charAt(i) ) == -1 )
                    		return false;
                    }
                    set1 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
                    set2 = "ABCDEFGHIJABCDEFGHIJKLMNOPQRSTUVWXYZ";
                    setpari = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
                    setdisp = "BAKPLCQDREVOSFTGUHMINJWZYX";
                    s = 0;
                    for( i = 1; i <= 13; i += 2 )
                    	s += setpari.indexOf( set2.charAt( set1.indexOf( cf.charAt(i) )));
                    for( i = 0; i <= 14; i += 2 )
                    	s += setdisp.indexOf( set2.charAt( set1.indexOf( cf.charAt(i) )));
                    if( s%26 != cf.charCodeAt(15)-'A'.charCodeAt(0) )
                    	return false;
                    return true;
                };
if ( value.length == 11 ){
    return validate_piva(value);
}else{
    return validate_cf(value);
}
       """
        return js
    
                                               
        
      