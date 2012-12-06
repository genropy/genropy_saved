# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('hierarchical_description')
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='code',op='contains', val='%')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        top = bc.contentPane(region='top')
        fb = top.div(margin='5px').formbuilder(cols=2, border_spacing='2px',width='100%',fld_width='100%')
        fb.field('code')
        fb.field('description')
        fb.field('isreserved', lbl='',label='Is reserved')
        fb.field('note')
        self.usersPane(bc.contentPane(region='center',margin='2px',datapath='#FORM'))

    def usersPane(self,pane):
        def user_struct(struct):
            r = struct.view().rows()
            r.cell('username', name='username', width='8em')
            r.cell('fullname', name='fullname', width='100%')
            
        th = pane.plainTableHandler(relation='@users',viewResource=':ViewFromTag')
        bar = th.view.top.bar    
        bar.replaceSlots('#','#,delrow,addusers')
        bar.addusers.paletteGrid('users', title='!!Users',searchOn=True, struct=user_struct,
                                  grid_filteringGrid=th.view.grid,
                                  grid_filteringColumn='username:user',
                                  dockButton_iconClass='icnOpenPalette').selectionStore(table='adm.user')
        
        grid = th.view.grid
        grid.dragAndDrop(dropCodes='users')
        grid.dataRpc('dummy',self.addUsers,data='^.dropped_users',tag_id='=#FORM.pkey')
        
    @public_method
    def addUsers(self,data=None,tag_id=None,**kwargs):
        usertagtbl = self.db.table('adm.user_tag')
        users=usertagtbl.query(where="$tag_id=:tag_id",tag_id=tag_id).fetchAsDict(key='user_id')
        for row in data:
            user_id = row.get('_pkey')
            if not user_id in users:
                usertagtbl.insert(dict(user_id=user_id,tag_id=tag_id))
        self.db.commit()       

    def th_options(self):
        return dict(hierarchical=True)