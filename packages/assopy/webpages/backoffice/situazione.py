#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
import datetime
import os
import hashlib

from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def windowTitle(self):
         return '!!Assopy Situazione economica'
         
    def pageAuthTags(self, method=None, **kwargs):
         return 'superadmin'
        
    def main(self, root, userid=None,**kwargs):

        top,client,bottom=self.publicPane(root,'!!Situazione Economica')
        lc=client.layoutContainer(height='100%')
        lcleft=lc.layoutContainer(layoutAlign='left',width='270px',border_right='1px solid silver')
        self.sponsor(lcleft.contentPane(layoutAlign='top',height='170px',datapath='sponsor'))
        self.tickets(lcleft.contentPane(layoutAlign='top',height='170px',datapath='tickets'))
        x=lcleft.contentPane(layoutAlign='client',datapath='totale')
        x.dataFormula('totricavi','sponsor+tickets',sponsor='^sponsor.totale.valore',tickets='^tickets.totale.valore',init=True)
        x.div('Totale Ricavi',background_color='#3272a6',color='white',font_size='1.2em',text_align='center',padding='1px')
        x.div('^totricavi',font_size='1.2em',text_align='center',_class='pbl_largemessage',margin_top='4px')
        #self.tickets(lc.contentPane(layoutAlign='top',height='90px',border_bottom='1px solid silver',datapath='tickets'))
        
        ricavi=lc.contentPane(layoutAlign='client')
        
    def sponsor(self,pane):
        pane.div('Sponsor',background_color='#3272a6',color='white',font_size='1.2em',text_align='center',padding='1px')
        pane.data('.v',dict(bronze=500,silver=1000,gold=1500,platinum=3000,diamond=5000))
        pane.data('.n',dict(bronze=4,silver=2,gold=2,platinum=1,diamond=1))
        for x in ['bronze','silver','gold','platinum','diamond']:
            pane.dataFormula('.t.%s'%x,'v*q',v='^.v.%s'%x,q='^.n.%s'%x,_init=True)
        pane.dataFormula('.totale.valore','tot.sum()',tot='^.t',_init=True)
        fb=pane.formbuilder(cols=4,border_spacing='2px',lblpos='T')
        fb.div('Bronze',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='Importo',value='^.v.bronze',width='5em',text_align='right',lbl_text_align='center',disabled=True)
        fb.numberTextBox(lbl='Num.',value='^.n.bronze',width='4em',text_align='right',lbl_text_align='center')
        fb.numberTextBox(lbl='Valore',value='^.t.bronze',width='6em',text_align='right',lbl_text_align='center',disabled=True)
        fb.div('Silver',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.silver',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.silver',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.silver',width='6em',text_align='right',disabled=True)
        fb.div('Gold',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.gold',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.gold',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.gold',width='6em',text_align='right',disabled=True)
        fb.div('Platinum',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.platinum',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.platinum',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.platinum',width='6em',text_align='right',disabled=True)
        fb.div('Diamond',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.diamond',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.diamond',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.diamond',width='6em',text_align='right',disabled=True)
        fb.div(width='5em')
        fb.div()
        fb.div('Totale',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.totale.valore',width='6em',text_align='right',disabled=True)
    
    def tickets(self,pane):
        pane.div('Ingressi',background_color='#3272a6',color='white',font_size='1.2em',text_align='center',padding='1px')
        pane.data('.v',dict(es=35,ep=50,ls=50,lp=80,od=120))
        pane.data('.n',dict(es=60,ep=80,ls=20,lp=50,od=4))
        for x in ['es','ep','ls','lp','od']:
            pane.dataFormula('.t.%s'%x,'v*q',v='^.v.%s'%x,q='^.n.%s'%x,_init=True)
        pane.dataFormula('.totale.valore','tot.sum()',tot='^.t',_init=True)
        pane.dataFormula('.totale.persone','tot.sum()',tot='^.n',_init=True)
        fb=pane.formbuilder(cols=4,border_spacing='2px',lblpos='T')
        fb.div('EarlyStu',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='Importo',value='^.v.es',width='5em',text_align='right',lbl_text_align='center',disabled=True)
        fb.numberTextBox(lbl='Num.',value='^.n.es',width='4em',text_align='right',lbl_text_align='center')
        fb.numberTextBox(lbl='Valore',value='^.t.es',width='6em',text_align='right',lbl_text_align='center',disabled=True)
        fb.div('EarlyPro',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.ep',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.ep',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.ep',width='6em',text_align='right',disabled=True)
        fb.div('LateStu',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.ls',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.ls',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.ls',width='6em',text_align='right',disabled=True)
        fb.div('LatePro',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.lp',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.lp',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.lp',width='6em',text_align='right',disabled=True)
        fb.div('OnDesk',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.v.od',width='5em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.n.od',width='4em',text_align='right')
        fb.numberTextBox(lbl='',value='^.t.od',width='6em',text_align='right',disabled=True)
        fb.div(width='5em')
        fb.div('Totale',lbl='',text_align='right',color='#3272a6')
        fb.numberTextBox(lbl='',value='^.totale.persone',width='4em',text_align='right',disabled=True)
        fb.numberTextBox(lbl='',value='^.totale.valore',width='6em',text_align='right',disabled=True)
    

    def rpc_saveUser(self, recordBag, **kwargs):
        try:
            recordBag['data_registrazione'] = datetime.date.today()
            recordBag['stato'] = 'provvisorio'
            recordBag['pwd'] = hashlib.md5(recordBag.pop('password')).hexdigest()
            recordBag['id'] = self.db.table('assopy.utente').newPkeyValue()
            self.db.table('assopy.utente').insert(recordBag)
            self.db.commit()
            try:
                self.sendConfirmationMail(recordBag)
                return 'ok'
            except Exception, err:
                return 'Record saved. Email error %s' %err
        except Exception, err:
            return 'Record not saved. Error %s' %err

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
