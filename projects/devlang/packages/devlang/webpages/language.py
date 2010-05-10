#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='devlang.language'
    py_requires='public:Public,standard_tables:TableHandler,gnrcomponents/selectionhandler'

    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('name', name='Name', width='20em')
        r.fieldcell('url', width='20em')
        return struct
        
    def formBase(self, parentBC,disabled=False, **kwargs):
        parentBC.data('gnr.polling',3)
        layout = parentBC.borderContainer(**kwargs)
        left = layout.contentPane(region='left',_class='pbl_roundedGroup',margin='10px',width='40%')
        left.div('!!Languages',_class='pbl_roundedGroupLabel')
        fb = left.formbuilder(cols=1, border_spacing='6px',width='300px')
        fb.field('name',autospan=1)
        fb.field('url',autospan=1)
        center = layout.borderContainer(region='center',margin='10px',margin_left=0)
        self.includedViewBox(center,label='!!Developers',datapath='developers',
                             nodeId='developers',table='devlang.dev_lang',autoWidth=True,
                             struct=self.language_developer_struct,
                             reloader='^form.record.id',
                             selectionPars=dict(where='$language_id=:l_id', l_id='=form.record.id',_if='l_id'))

    def language_developer_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@developer_id.first_name',width='20em',zoom=True)
        r.fieldcell('@developer_id.last_name',width='20em')
        r.fieldcell('level',width='10em')
        return struct
        

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Language'
        
    def barTitle(self):
        return '!!Language'
                  
    def orderBase(self):
        return 'name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%')
        
    def tableWriteTags(self):
        return None
        
    def tableDeleteTags(self):
        return None
        

############################## FORM METHODS ##################################