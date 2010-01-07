#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
import time
import os
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def windowTitle(self):
         return '!!Assopy gestione orario'
         
    def pageAuthTags(self, method=None, **kwargs):
         return 'superadmin'
        
    def main(self, root, userid=None,**kwargs):
        schedule=self.createSchedule()
        root.data('schedule',schedule)
        root.dataRpc('schedule','loadSchedule',scname='=schedulename',_fired='^loadschedule')
        root.dataRpc('dummy','saveSchedule',schedule='=schedule',scname='=schedulename',_fired='^saveschedule',_POST=True, _onResult='alert("Shedule salvato")')
        lc,top = self.publicRoot(root)
        top.div('!!Schedule Pycon2')
        top=lc.contentPane(layoutAlign='top',height='34px',border_bottom='1px solid silver',
                                                           border_left='1px solid silver',
                                                           border_right='1px solid silver')
        fb=top.formbuilder(cols=4,border_spacing='2px',margin_lef='5px')
        fb.textBox(lbl='Schedule',value='^schedulename')
        fb.button('Carica',fire='loadschedule')
        fb.button('Salva',fire='saveschedule')
        tc = lc.tabContainer(layoutAlign='client', selected='^selectedPage')
        self.conferenceManager(tc,u'Sabato',datapath='schedule.SAB',blocco=schedule.getItem('SAB'))
        self.conferenceManager(tc,u'Domenica',datapath='schedule.DOM',blocco=schedule.getItem('DOM'))
        
    def conferenceManager(self,tc,title,datapath,blocco):
        """docstring for conferenceManager"""
        ac = tc.accordionContainer(title=title,datapath=datapath)
        self.dayManager(ac,'Mattino',datapath='.M',blocco=blocco.getItem('M'))
        self.dayManager(ac,'Pomeriggio',datapath='.P',blocco=blocco.getItem('P'))
           
    def dayManager(self,ac,title,datapath,blocco):
        """docstring for dayManager"""    
        pane = ac.accordionPane(title=title,datapath=datapath)
        self.trackManager(pane,code='DP',background_color='#fdffca',blocco=blocco.getItem('DP'))
        self.trackManager(pane,code='SP',background_color='#c1d5ff',blocco=blocco.getItem('SP'))
        self.trackManager(pane,code='IP',background_color='#bcffbb',blocco=blocco.getItem('IP'))

        
    def trackManager(self,pane,code,background_color,blocco):
        """docstring for trackManager"""
        track = pane.div(_class='track', background_color=background_color,border='1px solid silver',margin_left='2px',
                                    float='left',width='32%',datapath='.%s'%code)
        for slotname,start,end,talk in blocco.digest('#k,#a.start,#a.end,#a.talk'):
            dp='^.%s'%slotname
            if talk=='CB':
                slot=track.div(border_bottom='1px solid gray',height='45px',padding='3px',background_color='gray')
                slot.div('%s?start'%dp,float='left',font_size='.8em',font_weight='bold',color='white',margin_right='5px')
                slot.div('%s?end'%dp,font_size='.8em',font_weight='bold',color='white')
                slot.div('Coffe Break',text_align='center',font_size='1.2em',color='white')
            else:
                slot=track.div(border_bottom='1px solid gray',height='45px',padding='3px')
                slot.div('%s?start'%dp,float='left',font_size='.8em',font_weight='bold',margin_right='5px')
                slot.div('%s?end'%dp,float='left',font_size='.8em',font_weight='bold')
                slot.div('?',float='right',font_size='.8em',font_weight='bold',background_color='gray',color='white',
                               cursor='pointer',connect_onclick='alert("assegna slot")',padding='3px')

        
    def talkManager(self,pane,start,i):
        datapath='.B%i'%i
        cnt=pane.div(height='^.height',border_bottom='1px solid gray',datapath=datapath)

            
        
        cnt.dataScript('.start','return durata + "px"',startprev='^.#parent',_if='durata',_else='return "30px"')
        cnt.dataScript('.height','return durata + "px"',durata='^.durata',_if='durata',_else='return "30px"')
        cnt.dbSelect(value='^.talk_id',dbtable='assopy.talk',columns='codice',selected_durata='.durata')
        
    def rpc_saveSchedule(self,schedule=None,scname='',**kwargs):
        schedulepath=os.path.join(self.siteFolder, 'data', 'schedule',scname+'.xml')
        schedule.toXml(schedulepath,autocreate=True)
        return 'ok'
        
    def rpc_loadSchedule(self,scname='',**kwargs):
        schedulepath=os.path.join(self.siteFolder, 'data', 'schedule',scname+'.xml')
        if os.path.isfile(schedulepath):
            schedule=Bag(schedulepath)
        else:
            schedule=self.createSchedule()
        return schedule
        
    def createSchedule(self):
        b=Bag()
        b.setItem('SAB.M',self._scheduleMattino())
        b.setItem('SAB.P',self._schedulePomeriggio())
        b.setItem('DOM.M',self._scheduleMattino())
        b.setItem('DOM.P',self._schedulePomeriggio())
        return b
        
    def _scheduleMattino(self):
        b=Bag()
        for k in ('DP','SP','IP'):
            b.setItem('%s.S_09_30' % k,None,dict(start='09:30',end='10:00'))
            b.setItem('%s.S_10_00' % k,None,dict(start='10:00',end='10:30'))
            b.setItem('%s.S_10_30' % k,None,dict(start='10:30',end='11:00'))
            b.setItem('%s.S_11_00' % k,None,dict(start='11:00',end='11:30',talk='CB'))
            b.setItem('%s.S_11_30' % k,None,dict(start='11:30',end='12:00'))
            b.setItem('%s.S_12_00' % k,None,dict(start='12:00',end='12:30'))
            b.setItem('%s.S_12_30' % k,None,dict(start='12:30',end='13:00'))
        return b
    
    def _schedulePomeriggio(self):
        b=Bag()
        for k in ('DP','SP','IP'):
            b.setItem('%s.S_14_30' % k,None,dict(start='14:30',end='15:00'))
            b.setItem('%s.S_15_00' % k,None,dict(start='15:00',end='15:30'))
            b.setItem('%s.S_15_30' % k,None,dict(start='15:30',end='16:00'))
            b.setItem('%s.S_16_00' % k,None,dict(start='16:00',end='16:30'))
            b.setItem('%s.S_16_30' % k,None,dict(start='16:30',end='17:00',talk='CB'))
            b.setItem('%s.S_17_00' % k,None,dict(start='17:00',end='17:30'))
            b.setItem('%s.S_17_30' % k,None,dict(start='17:30',end='18:00'))
            b.setItem('%s.S_18_00' % k,None,dict(start='18:00',end='18:30'))
        return b

