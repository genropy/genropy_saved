#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag
from random import randint
import datetime
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.personaggio'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'
    caratteristiche = [('ac',5),('ab',5),('forza',5),('resistenza',5),('agilita',5),('intelligenza',5),('volonta',5),('simpatia',5)]
    caratteristiche2 = [('attacchi',1),('ferite',1),('bonus_forza',1),('bonus_res',1),('mov',1),('magia',1),('follia',1),('fato',1)]

######################## STANDARD TABLE OVERRIDDEN METHODS ################ 
    def windowTitle(self):
        return '!!Schede Personaggi'

    def barTitle(self):
        return '!!Schede Personaggi'

#   def columnsBase(self):
#       return """sigla:4,nome:20,razza_codice/RC:3,@razza_codice.nome/Razza:10"""

    def lstBase(self,struct):
        """!!Vista base"""
        r = struct.view().rows()
        r.fieldcell('sigla',width='4em')
        r.fieldcell('nome',width='12em')
        r.fieldcell('@razza_codice.nome',width='10em')
        r.fieldcell('@carriera_id.nome',width='16em')
        return struct

    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True

    def orderBase(self):
        return 'nome'

    def queryBase(self):
        return dict(column='nome',op='contains', val='')

    def userCanWrite(self):
        return True

    def userCanDelete(self):
        return True

############################## FORM METHODS ##################################
        
    def formBase(self, parentBC, disabled=False, **kwargs):
               # !!! borderContainer == è la cornice
        pane = parentBC.contentPane(**kwargs)
               # !!! contentPane == è la tela (si attacca alla cornice)
        self.formIntro(pane,disabled=disabled)
        self.formStats(pane,disabled=disabled)
        self.controllers(pane)
        
    def formIntro(self,pane,disabled=None):
        cols=5
        infobase = pane.titlePane(title='Personaggio')
        fb = infobase.formbuilder(cols=cols,border_spacing='4px',disabled=disabled,
             width='550px',background='^.@razza_codice.colore')
               # !!! formbuilder == sono le caselline (si attaccano alla tela)
        fb.field('sigla',width='100%',colspan=3)
        fb.field('nome',width='100%',colspan=2)
        fb.field('razza_codice',width='100%',colspan=3)
        fb.button('Genera valori', fire='call_generavalori',width='100%',colspan=2)       
        fb.field('carriera_id',width='100%', colspan=3)
        fb.field('exp',width='100%',colspan=2)

    def formStats(self,pane,disabled=None):
        stats = pane.titlePane(title='Statistiche')
        cols=8
        fb = stats.formbuilder(cols=cols, border_spacing='4px', disabled=disabled, width='450px') 
#       fb.horizontalSlider(value='^.ac',minimum=0,maximum=100,width='15em',discreteValues='==101-minimum',intermediateChanges=True,colspan=2)
        
        for col,inc in self.caratteristiche:
            fb.field(col,width='3em',readOnly=True)

        for col,inc in self.caratteristiche:
            if inc:
                fb.field('%s_incr' % col,width='3em',readOnly=True)
            else:
                fb.div()

        for col,inc in self.caratteristiche:
            if inc:
                kwargs = {}
                kwargs['fire_%s_%i' % (col,inc)] = 'incremento'
                fb.button('+',**kwargs)
            else:
                fb.div()

        for col,inc in self.caratteristiche2:
            fb.field(col,width='3em',readonly=True)
        
        for col,inc in self.caratteristiche2:
            if inc:
                fb.field('%s_incr' % col,width='3em',readOnly=True)
            else:
                fb.div()

        for col,inc in self.caratteristiche2:
            if inc:
                kwargs = {}
                kwargs['fire_%s_%i' % (col,inc)] = 'incremento'
                fb.button('+',**kwargs)
            else:
                fb.div()
#        fb.button('+',fire_ferite_1='incremento')
#        fb.div(colspan=3)
        pane.dataController("""var inc = incremento.split('_');
                               var tipo = inc[0];
                               var delta = parseInt(inc[1]);
                               var cur_inc = data.getItem(tipo+'_incr');
                               if(cur_inc){
                               var cur_val = data.getItem(tipo);
                               data.setItem(tipo,cur_val+delta);
                               data.setItem(tipo+'_incr',cur_inc-delta);
                               data.setItem('exp',esperienza-100);
                               }
                               """,incremento='^incremento',data='=form.record',esperienza='=.exp',_if='esperienza >= 100')
                           
#       IF/ELSE in Javascript:
#       if(exp>0){} else{alert('');};
#             alcune note: le graffe nell'if vanno messe anche se non ci sono istanze!
#                          punteggiatura: non ci vuole punteggiatura tra l'if e l'else
#                                         quando si scrive dentro alle graffe bisogna chiudere con un ";" 
            
        pane.dataController("""SET .ac = razza.getItem('ac_base');
                               SET .ab = razza.getItem('ab_base');
                               SET .forza = razza.getItem('f_base');
                               SET .resistenza = razza.getItem('r_base');
                               SET .agilita = razza.getItem('ag_base');
                               SET .intelligenza = razza.getItem('int_base');
                               SET .volonta = razza.getItem('vol_base');
                               SET .simpatia = razza.getItem('simp_base');
                               SET .attacchi = razza.getItem('att_base');
                               SET .bonus_forza = razza.getItem('b_forza_base');
                               SET .bonus_res = razza.getItem('b_res_base');
                               SET .mov = razza.getItem('mov_base');
                               SET .magia = razza.getItem('magia_base');
                               SET .follia = razza.getItem('fol_base');
                               SET .fato = razza.getItem('pf_base');"""
                               ,_fired="^.razza_codice",razza='=.@razza_codice',_userChanges=True)
               # sintassi: pane.dataController("""SET .nome_tblColumn = nome_table.getItem('nome_di_una_colonna');"""
               # ,_fired="^.cio_che_fa_scattare_il_dataController"
               # ,???='=.@cio_che_fa_scattare_il_dataController',userChanges=True)
        
        pane.dataController("""SET .ac_incr = carriera.getItem('ac');
                             SET .ab_incr = carriera.getItem('ab');
                             SET .forza_incr = carriera.getItem('forza');
                             SET .resistenza_incr = carriera.getItem('resistenza');
                             SET .agilita_incr = carriera.getItem('agilita');
                             SET .intelligenza_incr = carriera.getItem('intelligenza');
                             SET .volonta_incr = carriera.getItem('volonta');
                             SET .simpatia_incr = carriera.getItem('simpatia');
                             SET .attacchi_incr = carriera.getItem('attacchi');
                             SET .ferite_incr = carriera.getItem('ferite');
                             SET .bonus_forza_incr = carriera.getItem('bonus_forza');
                             SET .bonus_res_incr = carriera.getItem('bonus_res');
                             SET .mov_incr = carriera.getItem('mov');
                             SET .magia_incr = carriera.getItem('magia');
                             SET .follia_incr = carriera.getItem('follia');
                             SET .fato_incr = carriera.getItem('fato');"""
        ,_fired="^.carriera_id",carriera='=.@carriera_id',_userChanges=True)
        
    def controllers(self,pane):
##################### inizio rpc_caller ###
        pane.dataRpc('valori',"generaValori",_fired="^call_generavalori",razza='=.razza_codice',
                    _if='razza',_else="alert('Scegli una razza!')")
#       pane.dataRpc('risultato_della_Rpc','nome_della_Rpc',_fired='call_nome_di_chi_spara',
#                     variabile_che_passo='=.nomi_variabile')                    
        pane.dataFormula(".ac", "x", x="^valori.ac")
        pane.dataFormula(".ab", "x", x="^valori.ab")
        pane.dataFormula(".forza", "x", x="^valori.f")
        pane.dataFormula(".resistenza", "x", x="^valori.r")
        pane.dataFormula(".agilita", "x", x="^valori.ag")
        pane.dataFormula(".intelligenza", "x", x="^valori.int")
        pane.dataFormula(".volonta", "x", x="^valori.vol")
        pane.dataFormula(".simpatia", "x", x="^valori.simp")
        pane.dataFormula(".ferite", "x", x="^valori.fer_base")        
        pane.dataFormula(".bonus_forza", "x", x="^valori.b_forza_base")
        pane.dataFormula(".bonus_res", "x", x="^valori.b_res_base")
        pane.dataFormula(".fato", "x", x="^valori.pf_base")
               # un'alternativa alla dataFormula --> fb.dataController("""SET .simpatia = x""", x = "^valori.simp")
##################### fine rpc_caller ###
        
    def rpc_generaValori(self,razza=None):
        tblrazza = self.db.table('warh.razza')
        record = tblrazza.record(pkey=razza).output('dict')
        risultato = Bag()
        tiro_fato = randint(1,10)
        griglia_fato = Bag(record['pf_base'])
        for riga in griglia_fato.values():
            if tiro_fato >= riga['da'] and tiro_fato <= riga['a']:
                risultato['pf_base'] = riga['valore']

        for x in ('ac','ab','f','r','ag','int','vol','simp'):
            risultato[x] = record['%s_base' % x]+randint(1,10)+randint(1,10)

        tiro_ferite = randint(1,10)
        griglia_ferite = Bag(record['fer_base'])
        for riga in griglia_ferite.values():
            da = long(riga['da'])
            a = long(riga['a'])
            if tiro_ferite >= da and tiro_ferite <= a:
                risultato['fer_base'] = riga['valore']
        risultato['b_forza_base'] = risultato['f'] / 10
        risultato['b_res_base'] = risultato['r']/10
        
        return risultato        
        
