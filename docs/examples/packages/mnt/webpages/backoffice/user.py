#!/usr/bin/env python
# encoding: utf-8
"""
etcf.py

Created by Jeff B. Edwards on 2008-11-07.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='mnt.jos_users'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'


    def windowTitle(self):
        return '!!Utenti'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Utenti'
        
    def columnsBase(self,):
        return """
                  id/Id:4,
                  name/Nome:14,
                  username/Nome Utente:14,
                  email/Mail:14,
                  usertype/Tipo:10,
                  block/Block:4,
                  sendEmail/I.Mail:4,
                  gid/Gruppo:4,
                  registerDate/Data Reg:10,
                  lastvisitDate/Ultima Visita:10,
               """
       
    def formBase(self, parentBC,  disabled=False, **kwargs):
        tc = parentBC.tabContainer(margin='2px',**kwargs)
        self.mainPane(tc.borderContainer(title='Dati base',margin='2px'),disabled=disabled)
        self.statsPane(tc.borderContainer(title='Statistiche',margin='2px'),disabled=disabled)
        self.contPane(tc.borderContainer(title='Contenuti',margin='2px'),disabled=disabled)
        
    def mainPane(self,bc,disabled):
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        right= bc.borderContainer(region='right', _class='pbl_roundedGroup',margin='5px',width='50%')
        base.div('!!Utente',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('mnt.jos_users.id',width='5em')
        fb.field('mnt.jos_users.name',width='16em')
        fb.field('mnt.jos_users.username',width='16em')
        fb.field('mnt.jos_users.email',width='16em')
        fb.field('mnt.jos_users.usertype',width='16em')
        fb.field('mnt.jos_users.block',width='4em')
        fb.field('mnt.jos_users.sendEmail',width='4em')
        fb.field('mnt.jos_users.gid',width='16em')
        fb.field('mnt.jos_users.registerDate',width='16m')
        fb.field('mnt.jos_users.lastvisitDate',width='16em')
        fb.field('mnt.jos_users.activation',width='16em')
        self.includedViewBox(right,label='!!Campi aggiuntivi',nodeId='extraFields',
                          storepath='.@mnt_jos_community_fields_values_user_id', 
                          add_action=True,
                          del_action=True,
                          table='mnt.jos_community_fields_values',
                          columns='@field_id.name/Campo:14,value/Valore:24')
        

    def statsPane(self,bc,disabled):
        self.includedViewBox(bc,label='!!Accessi',nodeId='accessGrid',
                            storepath='.@mnt_jos_usertrace_username', 
                            table='mnt.jos_usertrace',
                            columns="userip/IP:14,useragent:14,userurl:14,userreferer:12,date:8,time:7")
     
    def contPane(self,bc,disabled):
        pass
       #self.includedViewBox(bc,label='!!Contenuti',nodeId='contGrid',
       #                     storepath='.@uwaext_venue_schedule_unit_class_id', 
       #                     add_action='FIRE aux.dlgSchedNew.show;',
       #                     del_action=True,table='uwaext.venue_schedule',
       #                   struct=self._structSchedGrid(),formPars=formPars)
    def orderBase(self):
        return 'name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%', runOnStart=False)

                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
