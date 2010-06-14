#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='warh.carriera'
    py_requires='public:Public,standard_tables:TableHandlerLight,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ################ 
    def windowTitle(self):
        return '!!Carriere Personaggi'

    def barTitle(self):
        return '!!Carriere Personaggi'

    def lstBase(self,struct):
        """!!Vista base"""
        r = struct.view().rows()
        r.fieldcell('nome',width='12em')
        r.fieldcell('ac',width='5em')
        r.fieldcell('ab',width='5em')
        r.fieldcell('forza',width='5em')
        r.fieldcell('resistenza',width='6em')
        r.fieldcell('agilita',width='5em')
        r.fieldcell('intelligenza',width='6em')
        r.fieldcell('volonta',width='5em')
        r.fieldcell('simpatia',width='5em')
        r.fieldcell('attacchi',width='5em')
        r.fieldcell('ferite',width='5em')
        r.fieldcell('bonus_forza',width='4em')
        r.fieldcell('bonus_res',width='6em')
        r.fieldcell('mov',width='6em')
        r.fieldcell('magia',width='5em')
        r.fieldcell('follia',width='5em')
        r.fieldcell('fato',width='5em')
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

    def formBaseDimension(self): 
        return dict(height='250px',width='800px')

############################## FORM METHODS ##################################
        
    def formBase(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=8, border_spacing='4px', disabled=disabled)
        fb.field('nome', width='12em',colspan=8) 
        fb.field('ac',width='2em')
        fb.field('ab',width='2em')
        fb.field('forza',width='2em')
        fb.field('resistenza',width='2em')
        fb.field('agilita',width='2em')
        fb.field('intelligenza',width='2em')
        fb.field('volonta',width='2em')
        fb.field('simpatia',width='2em')
        fb.field('attacchi',width='2em')
        fb.field('ferite',width='2em')
        fb.field('bonus_forza',width='2em')
        fb.field('bonus_res',width='2em')
        fb.field('mov',width='2em')
        fb.field('magia',width='2em')
        fb.field('follia',width='2em')
        fb.field('fato',width='2em')

