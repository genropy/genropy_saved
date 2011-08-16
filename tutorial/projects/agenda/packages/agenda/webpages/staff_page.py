# -*- coding: UTF-8 -*-

# staff_page.py
# Created by Filippo Astolfi on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

import datetime

class GnrCustomWebPage(object):
    maintable = 'agenda.staff'
    py_requires = """public:TableHandlerMain"""
    
    def th_form(self, form, **kwargs):
        tc = form.center.tabContainer(margin='3px',selected='^.selected_tab')
        self.staffInfo(tc.borderContainer(title='Profilo', design='sidebar', margin='3px', datapath='.record', nodeId='staffId'))
        self.phoneInfo(tc.contentPane(title='Phone call', margin='3px'))
        
    def staffInfo(self, bc):
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
        top.div('!!Registry records',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(dbtable='sw_base.anagrafica',margin_left='10px',margin_top='1em',
                             width='370px',datapath='.@anagrafica_id',cols=2)
        fb.field('nome',lbl='!!Name')
        fb.field('cognome',lbl='!!Surname')
        fb.field('email',lbl='!!Email',
                  validate_email=True,validate_email_error='!!Uncorrected email format')
        fb.field('telefono',ghost='example: 347/1212123')#,validate_remote='checkTel')
        fb.field('codice_fiscale',lbl='!!Tax code',
                  validate_case='u')
        fb.field('partita_iva',lbl='!!VAT')
        fb.field('fax',lbl='!!Fax',colspan=2)
        fb.field('note',lbl='!!Notes',tag='simpletextarea',colspan=2,width='100%')
        
        left = bc.contentPane(region='left',_class='pbl_roundedGroup',margin='1px',width='50%')
        left.div('!!Staff records',_class='pbl_roundedGroupLabel')
        fb = left.formbuilder(margin_left='10px',margin_top='1em',
                             width='370px',cols=1) # è implicito grazie al maintable: dbtable='agenda.staff'
        fb.field('interno',ghost='example: 202')
        fb.field('ruolo',tag='combobox',lbl='Company role',
                  values='emplyee, freelance, manager, owner')
                  
        right = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='1px',width='50%')
        right.div('!User records',_class='pbl_roundedGroupLabel')
        fb = right.formbuilder(dbtable='adm.user',cols=1,margin_left='10px',margin_top='1em',
                               width='370px',datapath='.@user_id')
        fb.field('username',lbl='!!Username')
        fb.field('md5pwd',lbl='!!md5pwd')
        fb.field('auth_tags',lbl='!!Auth tags')
        fb.field('avatar_rootpage',lbl='!!Avatar rootpage')
        
    def phoneInfo(self, pane, **kwargs):
        pane.dialogTableHandler(relation='@phone_calls',
                                formResource=':FormFromReceiver',viewResource=':ViewFromReceiver',
                                dialog_height='400px',dialog_width='700px',dialog_title='Phone calls')
                                
    def onSaving_agenda_telefonata(self, recordCluster, recordClusterAttr, resultAttr=None):
        call_checked = recordCluster.pop('call_checked')
        if call_checked:
            recordCluster['vista_il'] = datetime.datetime.now()
            