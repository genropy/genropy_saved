# -*- coding: UTF-8 -*-

# tags_page.py
# Created by Francesco Porcari on 2011-05-15.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires="""public:Public,
                   gnrcomponents/htablehandler:HTableHandler,
                   public:TableHandlerMain"""
    maintable = 'adm.htag'
    def main(self, rootBC, **kwargs):
        frame = rootBC.rootBorderContainer(title='!!Tags manager')
        
        self.htableHandler(frame,table='adm.htag',nodeId='tags',
                            datapath='adm_tag',editMode='bc')
        
    def tags_form(self,parentBC,table=None,**kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        top.div('!!Tags info',_class='pbl_roundedGroupLabel')
        fb = top.div(margin='5px').formbuilder(cols=2, border_spacing='2px',width='100%',fld_width='100%')
        fb.field('child_code')
        fb.field('description')
        fb.field('isreserved', lbl='',label='Is reserved')
        fb.field('note')
        self.usersPane(bc.contentPane(region='center',margin='2px',datapath='#FORM'))

    def usersPane(self,pane):
        pane.plainTableHandler(relation='@users',viewResource=':ViewFromTag',picker='user_id')

        
        
