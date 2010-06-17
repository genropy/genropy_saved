#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='hosting.client'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView,hosted:HostedClient,hosted:HostedInstance'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Client'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'owner'
        
    def tableWriteTags(self):
        return 'owner'
        
    def tableDeleteTags(self):
        return 'owner'
        
    def barTitle(self):
        return '!!Client'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='10em')
        r.fieldcell('@anagrafica_id.ragione_sociale',name='!!Ragione sociale',width='15em')
        r.fieldcell('@user_id.username',name='User',width='10em')
        return struct
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='code',op='contains', val='%')
    def orderBase(self):
        return 'code'

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        tc = parentBC.tabContainer(**kwargs)
        self.infoform(tc.contentPane(title='Info'),disabled)
        for pkgname,handler in [(c.split('_')[1],getattr(self,c)) for c in dir(self) if c.startswith('hostedclient_')]:
            handler(tc.contentPane(datapath='.hosted_data.%s' %pkgname,title=self.db.packages[pkgname].name_long))
        
    
    def infoform(self,pane,disabled):
        fb = pane.formbuilder(cols=2, border_spacing='3px',fld_width='100%',width='350px',disabled=disabled)
        fb.field('code')
        fb.field('user_id')
        fb.field('anagrafica_id',colspan=2)

        
