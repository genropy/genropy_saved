# -*- coding: UTF-8 -*-

# staff_page.py
# Created by Niso on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable = 'agenda.staff'
    py_requires = """public:TableHandlerMain,
                     """
                     
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
        top.div('!!Record di anagrafica',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(dbtable='sw_base.anagrafica',margin_left='10px',margin_top='1em',
                             width='370px',datapath='.@anagrafica_id',cols=2)
        fb.field('nome')
        fb.field('cognome')
        fb.field('email',
                  validate_email=True,validate_email_error='!!Formato email non corretto')
        fb.field('telefono', ghost='esempio: 347/1212123')
        fb.field('codice_fiscale',
                  validate_case='u')
        fb.field('partita_iva')
        fb.field('fax',colspan=2)
        fb.field('note',tag='textarea',colspan=2,width='100%')
        
        left = bc.contentPane(region='left',_class='pbl_roundedGroup',margin='1px',width='50%')
        left.div('!!Record di staff',_class='pbl_roundedGroupLabel')
        fb = left.formbuilder(margin_left='10px',margin_top='1em',
                             width='370px',cols=1) # è implicito grazie al maintable: dbtable='agenda.staff'
        fb.field('interno',ghost='esempio: 202')
        fb.field('ruolo',tag='combobox',lbl='Ruolo nell\'azienda',
                  values='dipendente, libero professionista, manager')
                  
        right = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='1px',width='50%')
        right.div('!!Record di user',_class='pbl_roundedGroupLabel')
        fb = right.formbuilder(dbtable='adm.user',cols=1,margin_left='10px',margin_top='1em',
                               width='370px',datapath='.@user_id')
        fb.field('username')
        fb.field('md5pwd')
        fb.field('auth_tags')
        fb.field('avatar_rootpage')
