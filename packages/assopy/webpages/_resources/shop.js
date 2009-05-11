var ordine = {
    initDays:function(g1,g2,g3){
        this.g1=g1;
        this.g2=g2;
        this.g3=g3;
    },
    prepSave: function(paymode){
        var maxslots = genro.getData('aux.rectariffa.ingressi_omaggio');
        if (maxslots && (paymode!='bozza')){
            var righe=genro.getData('form.ordine.children.ordine_riga').getNodes();
            var riga,tbag;
            var totale=0;
            for (var i=0; i < maxslots; i++){
                var riga=righe[i].getValue();
                if(!riga.getItem('tariffa_id')){
                    riga.setItem('partecipante.cognome',' ');
                    this.calcola(i);
                }
            }
        }
    },
    setTariffa: function(riga){
        var tariffa_code;
        if (riga.getItem('partecipante.nome')|| riga.getItem('partecipante.cognome')){
            var studente = riga.getItem('partecipante.studente');
            if (studente!=true){
                riga.setItem('partecipante.studente', false);
            }
            if (genro.getData('form.sponsorizzazione')){
                tariffa_code = 'OMG';
            } else {
                tariffa_code=riga.getItem('partecipante.studente')? 'TK_STU':'TK_PRO';
            }
            
        }else{
            riga.setItem('partecipante',new gnr.GnrBag());
            riga.setItem('partecipante.presenza_g1',true);
            riga.setItem('partecipante.presenza_g2',true);
            riga.setItem('partecipante.presenza_g3',true);
        }
        var tbag= genro.getData('tariffe.'+tariffa_code) || new gnr.GnrBag();
        riga.setItem('tariffa_id',tbag.getItem('id'));
        riga.setItem('tariffa_codice',tbag.getItem('codice'));
        riga.setItem('tariffa_descrizione',tbag.getItem('descrizione'));
        riga.setItem('partecipante.tariffa_tipo',tbag.getItem('tipo'));
        var importo = tbag.getItem('importo');
        if(!tbag.getItem('prezzo_ivato')){
            importo = importo * (1+(tbag.getItem('aliquota_iva')/100));
        }
        riga.setItem('importo',importo);
        riga.setItem('aliquota_iva',tbag.getItem('aliquota_iva'));
        return tbag.getItem('id');
    },
    calcola: function(nslot){
        var maxslots = genro.getData('aux.rectariffa.ingressi_omaggio');
        var righe=genro.getData('form.ordine.children.ordine_riga').getNodes();
        var riga,imponibile,iva,empty,id_tariffa,cod_tariffa;
        var totale=0;
        for (var i=0; i < righe.length; i++){
            var riga=righe[i].getValue();
            var id_tariffa=riga.getItem('tariffa_id');
            if(maxslots != null){
                if (i >= maxslots){
                    genro.dom.hide('slot_'+i);
                    riga.setItem('partecipante', null);
                } else {
                    genro.dom.show('slot_'+i);
                }
            }
            if((nslot==null) || (i==nslot)){
                var slot=dojo.byId('slot_'+i);
                var id_tariffa= this.setTariffa(riga);
                if (id_tariffa){
                    genro.dom.removeClass(slot,'empty_ticket');
                    genro.dom.addClass(slot,'filled_ticket');
                    var presenze=[];
                    if(riga.getItem('partecipante.presenza_g1')) {presenze.push(this.g1);}
                    if(riga.getItem('partecipante.presenza_g2')) {presenze.push(this.g2);}
                    if(riga.getItem('partecipante.presenza_g3')) {presenze.push(this.g3);}
                    riga.setItem('partecipante.presenze',presenze.join(' - '));
                }else{
                    genro.dom.removeClass(slot,'filled_ticket');
                    genro.dom.addClass(slot,'empty_ticket');
                }

            }
            if(id_tariffa){
                totale=totale+riga.getItem('importo');
            }
        
        }
        
        sponsor=genro.getData('form.ordine.sponsorizzazione.importo')
        if (sponsor){
            totale = totale + sponsor
        }
        var tiva = genro.getData('form.ordine.related.anagrafica.tipo_iva');
        if(tiva && (tiva!='00')){
            var imponibile=Math.floor(totale*100/1.20)/100;
            totale = imponibile;
            var iva=0;
        } else {
            var imponibile=Math.floor(totale*100/1.20)/100;
            var iva=dojo.number.round(totale-imponibile,2);
        }
        genro.setData('form.ordine.mainrecord.totale',totale);
        genro.setData('form.ordine.mainrecord.iva',iva);
        genro.setData('form.ordine.mainrecord.imponibile',imponibile);
        genro.setData('aux.totale_txt', genro.format(totale, {currency: "EUR"}));
        genro.setData('aux.iva_txt',  genro.format(iva, {currency: "EUR"}));
        genro.setData('aux.imponibile_txt',  genro.format(imponibile, {currency: "EUR"})); 
        genro.dom.removeClass(dojo.byId('tickets'),'tickets_hidden');
    },
    presenze_partecipanti: function(nslot){
        var righe=genro.getData('form.partecipanti').getNodes();
        if (nslot==null){
            for (var i=0; i < righe.length; i++){
                this.presenze_partecipanti(i);
            }
        } else {
            var riga=righe[nslot].getValue();

            var presenze=[];
            if(riga.getItem('presenza_g1')) {presenze.push(this.g1);}
            if(riga.getItem('presenza_g2')) {presenze.push(this.g2);}
            if(riga.getItem('presenza_g3')) {presenze.push(this.g3);}
            riga.setItem('presenze',presenze.join(' - '));
        }
    }
}