#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='develop.project'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Project'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'staff,user'
        
    def tableWriteTags(self):
        return 'staff,user'
        
    def tableDeleteTags(self):
        return 'staff'
        
    def barTitle(self):
        return '!!Project Management'
        
    def columnsBase(self,):
        return """name,company,description"""
                  
    def orderBase(self):
        return '$name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        tc = parentBC.tabContainer(margin='2px',**kwargs)
        tab1 = tc.borderContainer(title='Project')
        tab2 = tc.borderContainer(title='Tickets')
        self.tabProject(tab1,disabled)
        self.tabTickets(tab2)
    
    def tabProject(self,bc,disabled):
        top = bc.contentPane(region='top',height='30ex',margin='2px',_class='pbl_roundedGroup')
        fb = top.formbuilder(cols=1, border_spacing='6px',disabled=disabled)
        fb.field('develop.project.name',width='12em')
        fb.field('develop.project.client_id',width='12em',auxColumns='address')
        fb.div(innerHTML='==dataTemplate(tpl, dbag);',
                tpl='$address <br/> $email <br/> $phones',
                dbag='^.@client_id',_class='infoBox')
        fb.field('develop.project.description',width='12em',height='8ex',tag='simpleTextArea',
                lbl_vertical_align='top')
        center = bc.borderContainer(region='center',margin='2px')
        self.editProjectNotes(center)
        
    def editProjectNotes(self,bc):
        """ Griglia che rappresenta una bag dove le note sul progetto sono messe in maniera strutturata """
        pass

    def tabTickets(self,bc):
        top = bc.borderContainer(region='top',margin='2px',height='50%')
        center = bc.borderContainer(region='center',margin='2px')
        self.ticketView(top)
        self.actionsView(center)
        
    def ticketView(self,bc):
        """ visualizzo tutti i ticket del project. con un doppio click edito la form all'interno del dialog. 
            posso aggiungere ed eliminare se sono dello staff. """
        pass
    def actionsView(self,bc):
        """visualizzo tutti i le actions del ticket selezionato tramite un path variabile. 
            con un doppio click edito la form all'interno del dialog. 
            posso aggiungere ed eliminare se sono dello staff. """
        pass
    
############################## RPC_METHODS ###################################       

# --------------------------- GnrWebPage Standard footer ---------------------------
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
        