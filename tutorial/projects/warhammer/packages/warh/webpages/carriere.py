#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2010-05-15.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'warh.carriera'
    py_requires = 'public:Public,standard_tables:TableHandlerLight,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ################
    def windowTitle(self):
        return '!!Carriere personaggi'

    def barTitle(self):
        return '!!Carriere personaggi'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='11em')
        r.fieldcell('ac', width='5em')
        r.fieldcell('ab', width='5em')
        r.fieldcell('forza', width='3em')
        r.fieldcell('resistenza', width='5em')
        r.fieldcell('agilita', width='3em')
        r.fieldcell('intelligenza', width='5em')
        r.fieldcell('volonta', width='4em')
        r.fieldcell('simpatia', width='4em')
        r.fieldcell('attacchi', width='4em')
        r.fieldcell('ferite', width='3em')
        r.fieldcell('bonus_forza', width='3em')
        r.fieldcell('bonus_res', width='5em')
        r.fieldcell('mov', width='5em')
        r.fieldcell('magia', width='3em')
        r.fieldcell('follia', width='5em')
        r.fieldcell('fato', width='5em')
        return struct

    def printActionBase(self):
        return True

    def exportActionBase(self):
        return True

    def orderBase(self):
        return 'nome'

    def queryBase(self):
        return dict(column='nome', op='contains', val='')

    def userCanWrite(self):
        return True

    def userCanDelete(self):
        return True

    ############################## FORM METHODS ##################################

    def formBaseDimension(self):
        return dict(height='220px', width='800px')

    def formBase(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=8, border_spacing='4px', fld_width='2em')
        fb.field('nome', width='12em', colspan=8)
        fb.field('ac')
        fb.field('ab')
        fb.field('forza')
        fb.field('resistenza')
        fb.field('agilita')
        fb.field('intelligenza')
        fb.field('volonta')
        fb.field('simpatia')
        fb.field('attacchi')
        fb.field('ferite')
        fb.field('bonus_forza')
        fb.field('bonus_res')
        fb.field('mov')
        fb.field('magia')
        fb.field('follia')
        fb.field('fato')