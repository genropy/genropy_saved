#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Anagrafica """
import time
import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.talk'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    def windowTitle(self):
        return '!!Assopy Talks'
    
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def tableWriteTags(self):
        return 'talkadmin,superadmin'
        
    def tableDeleteTags(self):
        return 'superadmin'
        
    def barTitle(self):
        return '!!Gestione Talks'
    
    def lstBase(self):
        struct = self.newGridStruct()
        r=struct.view().rows(classes='tablewiew_grid',cellClasses='tablewiew_cells',headerClasses='tablewiew_headers')
        r.cell('@oratore_id.@anagrafica_id.@utente_id.nome_cognome',width='15em',name='Oratore')
        r.cell('titolo',width='30em',name='Titolo')
        r.cell('@track_id.codice',name='Track',width='6em')
        r.cell('ora_inizio',name='Inizio',width='6em',format_time='short')
        r.cell('ora_fine',name='Fine',width='6em',format_time='short')
        
        return struct
    
    def lstBase_full(self):
        struct = self.newGridStruct()
        view=struct.view()
        rows1=view.rows(classes='tablewiew_grid',cellClasses='talk_cell_row1 tablewiew_cells',headerClasses='tablewiew_headers')
        rows1.cell('@oratore_id.@anagrafica_id.@utente_id.nome_cognome',width='15em',name='Oratore')
        rows1.cell('titolo',width='30em',name='Titolo',font_weight='bold',text_align='center')
        rows1.cell('durata',name='Durata',width='6em')
        rows1.cell('@track_id.codice',name='Track',width='6em')
        rows1.cell('voto',name='Voto',width='6em',text_align='center',color='red',fonr_weight='bold')
        rows2=view.rows(classes='tablewiew_grid',cellClasses='tablewiew_cells talk_cell_row2 preformattato',headerClasses='tablewiew_headers')
        rows2.cell('abstract',width='60em',name='Abstract',colSpan=5)
        return struct
        
    def formBase(self,pane,disabled=False,datapath=''):
        p1=pane.layoutContainer(datapath=datapath,height='100%')
        top=p1.layoutContainer(layoutAlign='top',height='1.8em')
        top.contentPane(layoutAlign='right',width='14em').div('^.@track_id.titolo',_class='talk_track',padding_right='5px')
        top.contentPane(layoutAlign='left',width='14em').div('^.@oratore_id.@anagrafica_id.@utente_id.nome_cognome',
                                           _class='talk_oratore',padding_left='5px')
        top.contentPane(layoutAlign='client').div('^.titolo',_class='talk_titolo')
        cli=p1.layoutContainer(layoutAlign='client')
        top=cli.contentPane(layoutAlign='top',height='60px',border='1px solid gray')
        fb=top.formbuilder(cols=3,border_spacing='4px',margin_top='3px',margin_left='3px')
        fb.filteringSelect(value='^.lingua',lbl='Lingua', values='!!it:Italiano,en:Inglese',disabled=disabled)
        fb.filteringSelect(value='^.sala',lbl='Sala', values='!!A:Sala A,B:Sala B,C:Sala C,-:Candidato,X:Non accettato',disabled=disabled)
        fb.filteringSelect(value='^.durata',lbl='Durata',  values='!!30:30 minuti,45:45 minuti,60:60 minuti,90:90 minuti',disabled=disabled)
        fb.DateTextBox(value='^.data',lbl='Data',disabled=disabled)
        fb.TimeTextBox(value='^.ora_inizio',lbl='Dalle',disabled=disabled)
        fb.TimeTextBox(value='^.ora_fine',lbl='Alle',disabled=disabled)
        
        tc=cli.tabContainer(layoutAlign='client',selected='selectedTab')
        tc.contentPane(title='Abstract').div('^.abstract',font_size='.9em',padding='1em',_class='preformattato')
        tc.contentPane(title='Presentazione').div('^.@oratore_id.presentazione',font_size='.9em',padding='1em',_class='preformattato') 
        valutazione=tc.contentPane(title='Valutazione')   
        voti=tc.contentPane(title='Voti e commenti',connect_onLoad='genro.wdgById("votiGrid").render()')       
        self.paneValutazioni(valutazione)
        self.visualizzaVoti(voti)
        
        et=tc.contentPane(title='Edit talk')   
        self.editTalk(et)
        ab=tc.contentPane(title='Edit abstract')   
        self.editAbstract(ab)
        ab=tc.contentPane(title='Edit abstract ing.')   
        self.editAbstractEn(ab)
    def paneValutazioni(self,pane): 
        pane.dataRpc('voto.save_result','salvaVoto', data='=valutazione', _POST=True, _voto='=valutazione.voto' ,
                                 _if='_voto!=null',_fired='^salvavoto',
                                 _else=u'alert("Per votare devi esprimere un voto valido")',
                                 _onResult=u'alert("Il voto è stato registrato")')
        pane.dataRecord('valutazione','assopy.valutazione',talk_id='^form.record.id',_fired='^voto.save_result',
                                    utente_id='^_pbl.user_record.id',_if='talk_id',
                                    _onResult="""var talk_id = GET form.record.id;
                                               var utente_id = GET _pbl.user_record.id;
                                               SET valutazione.talk_id=talk_id;
                                               SET valutazione.utente_id=utente_id;""")
        fb=pane.formBuilder(cols=3,datapath='valutazione')
        fb.horizontalslider(lbl='!!Voto', value = '^.voto',margin_top='2px', 
                                discreteValues='5', width='200px', minimum=0, maximum=4)
        fb.div('^.voto',_class='talk_voto')
        fb.button(label='Vota',fire='salvavoto')
        fb.textArea(lbl='Commento',lbl_vertical_align='top', value='^.note',
                      _class='talk_commento',colspan='3')
        
        
    def editTalk(self,pane,disabled=False,datapath=''): 
        fb = pane.formbuilder(datapath=datapath,cols=2, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.talk.@oratore_id.@anagrafica_id.@utente_id.nome_cognome',width='15em',colspan=2) 

        fb.field('assopy.talk.titolo',width='30em',colspan=2)
        fb.field('assopy.talk.argomento',value='^.argomento',width='30em',colspan=2)
        
        fb.field('assopy.talk.data',value='^.data')
        fb.filteringSelect(value='^.record.durata',lbl='Durata',
                           values='!!30:30 minuti,60:60 minuti,90:90 minuti',default=60)
        fb.field('assopy.talk.lingua',value='^.lingua')
        fb.field('assopy.talk.track_id',value='^.track_id',lbl='Track')
        fb.field('assopy.talk.sala',value='^.sala')
        fb.field('assopy.talk.evento_id',colspan=2,value='^.evento_id')
    
    def editAbstract(self,pane,disabled=False,datapath=''): 
        fb = pane.formbuilder(datapath=datapath,cols=2, margin_left='2em',border_spacing='3px',margin_top='1em',disabled=disabled)
        fb.textarea(lbl_vertical_align='top',width='53em',height='16em'
                    ,colspan=2,_class='form_textarea',value='^.abstract')
        fb.field('assopy.talk.oratore2_id',lbl='!!Speaker2',value='^.oratore2_id')
    
    def editAbstractEn(self,pane,disabled=False,datapath=''): 
        fb = pane.formbuilder(datapath=datapath,cols=2, margin_left='2em',border_spacing='3px',margin_top='1em',disabled=disabled)
        fb.textarea(lbl_vertical_align='top',width='53em',height='16em'
                    ,colspan=2,_class='form_textarea',value='^.abstract_en')
    def visualizzaVoti(self,pane):
        """docstring for visualizzaVoti"""
        ic=pane.includedView(storepath='.@assopy_valutazione_talk_id',
                                 struct=self._structVotiGrid())
                                 
       #pane.staticGrid(nodeId='votiGrid', selectedIndex='form.votiGrid.selectedIndex', 
       #                storepath='.@assopy_valutazione_talk_id', structpath='form.votiGrid.struct',
       #                elasticView=0, autoWidth=True, autoHeight=False)
       #pane.data('form.votiGrid.struct', self._structVotiGrid())
        
    def _structVotiGrid(self):
        struct = self.newGridStruct('assopy.valutazione')
        r = struct.view().rows(classes='df_grid', cellClasses='df_cells', headerClasses='df_headers')
        r.fieldcell('@utente_id.nome_cognome',width='15em')
        #r.fieldcell('@utente_id.@assopy_anagrafica_utente_id.cellulare')
        r.fieldcell('voto',width='3em')
        r.fieldcell('note',width='45em')
        return struct
        
    def sqlContextRecord(self):
        result = Bag()
        result['relatedcolumns.assopy.valutazione.talk_id'] = self._structVotiGrid().getFieldNames()
        return result

    def joinConditions(self):
        self.setJoinCondition('standard_list',
                              target_fld='assopy.valutazione.talk_id', 
                              from_fld='assopy.talk.id',
                              condition="$tbl.utente_id = :user_id",
                              one_one=True,
                              user_id=self.userRecord('id')
                              )
            
    def orderBase(self):
        return 'titolo'
    
    def queryBase(self):
        return dict(column='@oratore_id.nome_cognome',op='contains', val=None,runOnStart=True)
        
    def rpc_salvaVoto(self,data):
        tblobj=self.db.table('assopy.valutazione')
        tblobj.insertOrUpdate(data)
        self.db.commit()
        return 'ok'
                       
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

