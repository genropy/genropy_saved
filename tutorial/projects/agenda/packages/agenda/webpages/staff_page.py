# -*- coding: UTF-8 -*-

# staff_page.py
# Created by Filippo Astolfi on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable = 'agenda.staff'
    py_requires = """public:TableHandlerMain"""
                     
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Staff'
        
    def barTitle(self):
        return '!!Staff'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def th_form(self,form,**kwargs):
        bc = form.record.borderContainer(margin='3px')
        #tc = form.center.tabContainer()
        #
        #bc = tc.borderContainer(datapath='.record', title='Profilo')
        #altro = tc.contentPane(title='Altro')
        #altro.numbertextbox(value='^.numerobusatto',default=36)
        
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
        fb.field('note',lbl='!!Notes',tag='textarea',colspan=2,width='100%')
        
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
        
    # Prova con "thIframe" ... (non funziona!)
    #def th_form(self,form,**kwargs):
    #    tc = form.center.tabContainer(margin='3px', selected='^.selected_tab')
    #    tc.contentPane(title='Companies', margin='3px').thIframe('companies')
    #    tc.contentPane(title='Staff', margin='3px').thIframe('staff')
    #    
    #def iframe_companies(self, pane, **kwargs):
    #    th = pane.dialogTableHandler(table='agenda.azienda',virtualStore=True,
    #                                 dialog_height='500px',dialog_width='700px',dialog_title='COMPANY')
    #    
    #def iframe_staff(self, pane, **kwargs):
    #    th = pane.paletteTableHandler(table='agenda.staff',virtualStore=True,
    #                                  palette_height='500px',palette_width='700px',dialog_title='STAFF')
                                      