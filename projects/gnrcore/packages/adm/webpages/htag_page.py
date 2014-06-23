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
        grid.dataRpc('dummy','addUsers',data='^.dropped_users',tag_id='=#FORM.pkey')
        
    def rpc_addUsers(self,data=None,tag_id=None,**kwargs):
        usertagtbl = self.db.table('adm.user_tag')
        users=usertagtbl.query(where="$tag_id=:tag_id",tag_id=tag_id).fetchAsDict(key='user_id')
        for row in data:
            user_id = row.get('_pkey')
            if not user_id in users:
                usertagtbl.insert(dict(user_id=user_id,tag_id=tag_id))
        self.db.commit()
        