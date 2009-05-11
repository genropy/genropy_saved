#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('anagrafica',  pkey='id',name_long='Anagrafica',  group_ind='Indirizzo', rowcaption='denominazione')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('user_id',size='22',name_long='User id', group='_').relation('adm.user.id', one_one=True)
        tbl.column('denominazione',name_long='Denominazione')#per ora è senza dimensione
        tbl.column('codice_fiscale', size=':16',name_long='Codice fiscale')
        tbl.column('titolo', size=':18',name_long='Titolo', group='*')
        tbl.column('indirizzo',name_long='via', group='ind')        
        tbl.column('localita',size=':32',name_long=u'Località', group='ind')
        tbl.column('comune_istat',name_long=u'Istat comune', group='ind').relation('glbl.localita.codice_istat')            
        tbl.column('provincia', size=':3',name_long='Provincia', group='ind').relation('glbl.province.sigla')
        tbl.column('cap', size=':5',name_long='CAP', group='ind')
        tbl.column('recapiti', dtype='X',name_long='Recapiti tel-fax-email')


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
                  }"""
        return js
    
        

        
