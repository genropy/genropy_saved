#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='showcase.cast'
    py_requires='public:Public,standard_tables:TableHandler,public:RecordHandler'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!'
         
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def tableWriteTags(self):
        return ''
        
    def tableDeleteTags(self):
        return ''
        
    def barTitle(self):
        return '!!'
        
    def columnsBase(self,):
        return """@person_id.name,@person_id.nationality,@movie_id.title"""
                  
            
    def orderBase(self):
        return '@person_id.name'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='@person_id.name',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self,parentBC,disabled=False,**kwargs):
        pane = parentBC.contentPane(**kwargs)
        pane.field('showcase.cast.person_id')
        pane.button('Add or edit',action='FIRE aux.firedPkey = GET .person_id;')
        pane.button('Add only',action='FIRE aux.firedPkey')

        self.recordDialog(table='showcase.person',
                          firedPkey='^aux.firedPkey',
                          height='20ex',width='20em',title='!!Person',
                          formCb=self.personForm)
                                    
    def personForm(self,recordSC,disabled,table):
        pane = recordSC.contentPane(_class='roundedGroup')
        fb = pane.formbuilder(cols=1, border_spacing='6px',disabled=disabled)
        fb.field('showcase.person.name',width='10em')
        fb.field('showcase.person.year',width='10em')
        fb.field('showcase.person.nationality',width='10em')
        
    def onSaving_showcase_person(self,recordCluster,recordClusterAttr, resultAttr=None):
        pass
        
    def onLoading_showcase_person(self,record,newrecord,loadingParameters,recInfo):
        pass

############################## RPC_METHODS ###################################       

        