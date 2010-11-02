# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

class FlibPicker(BaseComponent):
    py_requires="""gnrcomponents/htablehandler:HTableHandlerBase,foundation/includedview:IncludedView"""
    css_requires ='public'
    
    def flibPicker(self,pane,pickerId=None,datapath=None,title=None,rootpath=None,
                  centerOn=None,limit_rec_type=None,**kwargs):
        """"""
        pane = pane.floatingPane(title=title or "!!File picker",
                                height='400px',width='600px',nodeId=pickerId, showOnStart=False,
                                dockable=False,datapath=datapath,resizable=True,_class='shadow_4')
        pane.dataController("genro.wdgById(pickerId).show(); genro.dom.centerOn(pickerId,centerOn)",
                            centerOn=centerOn or "mainWindow",
                            pickerId=pickerId,**{'subscribe_%s_open'%pickerId:True})
        bc = pane.borderContainer()
        left = bc.contentPane(region='left',splitter=True,width='150px',_class='pbl_roundedGroup',margin='2px')             
        left.data('.tree.store',self.ht_treeDataStore(table='flib.category',rootpath=rootpath,rootcaption='!!Categories',rootcode='%'),
                    rootpath=rootpath)
        left.tree(storepath ='.tree.store',
                    margin='10px',isTree =False,hideValues=True,
                    labelAttribute ='caption',
                    selected_pkey='.tree.pkey',selectedPath='.tree.path',  
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_caption='.tree.caption',
                    inspect='shift',
                    selected_child_count='.tree.child_count')
                    
        center = bc.borderContainer(region='center',_class='pbl_roundedGroup',margin='2px')
        def saved_files_struct(struct):
            r = struct.view().rows()
            r.fieldcell("@item_id.title",width='10em',title='!!Title')
            r.fieldcell("@item_id.description",width='15em',title='!!Description')
            r.cell("thumb",width='5em',title='!!Thumb',calculated=True)
        pickerGridId = '%s_grid' %pickerId
        
        self.includedViewBox(center.borderContainer(region='top',height='50%'),label='!!Items',
                            datapath='.item_grid',
                             nodeId=pickerGridId,table='flib.item_category',autoWidth=True,
                             struct=saved_files_struct,hiddencolumns='$item_id,@item_id.ext AS ext,@item_id.metadata AS meta',
                             reloader='^.#parent.tree.code',
                             filterOn='@item_id.title,@item_id.description',
                             selectionPars=dict(where="@category_id.code LIKE :cat_code || '%%'",
                                                cat_code='=.#parent.tree.code',
                                                applymethod='flibUpdateThumb',apply_checked_pkeys='=.#parent.checked_pkeys',
                                                order_by='@item_id.title'))
       #center.dataController("""
       #                        
       #                        var params = %s_row_checked;
       #                        var checked = params[1];
       #                        var item_id = params[2]['item_id'];
       #                        var checked_pkeys = checked_pkeys || [];
       #                        if(checked){
       #                        
       #                            checked_pkeys.push(item_id);
       #                            console.log('adding')
       #
       #                            console.log(checked_pkeys)
       #                        }
       #                        else{
       #                            var ind = dojo.indexOf(checked_pkeys,item_id);
       #                            if(ind>=0){
       #                                checked_pkeys.splice(ind,1);
       #                                console.log('removing')
       #                                console.log(checked_pkeys)
       #                            }
       #                        }
       #                        SET .checked_pkeys =checked_pkeys;
       #                        FIRE .checked_pkeys_changed;
       #                      """ %pickerGridId,checked_pkeys='=.checked_pkeys',
       #                      
       #                    **{'subscribe_%s_row_checked' %pickerGridId:True})
                            
      # def item_struct(struct):
      #     r = struct.view().rows()
      #     r.fieldcell("title",width='10em',title='!!Title')
      #     r.fieldcell("description",width='15em',title='!!Description')
      #     r.cell("thumb",width='5em',title='!!Thumb',calculated=True)
      #     r.cell('delete',format_isbutton=True, name=' ',calculated=True,width='18px',
      #             format_buttonclass='icnBaseDelete',
      #             format_onclick='console.log(arguments);')
      #     
      # self.includedViewBox(center.borderContainer(region='center'),datapath='.picked_grid',
      #                      label='!!Picked items',
      #                      nodeId='%s_pickedgrid' %pickerId,table='flib.item',autoWidth=True,
      #                      struct=item_struct,hiddencolumns='$ext AS ext,$metadata AS meta',
      #                      reloader='^.#parent.checked_pkeys_changed',
      #                      selectionPars=dict(where="$id IN :checked_pkeys",
      #                                         checked_pkeys='=.#parent.checked_pkeys',
      #                                         applymethod='flibUpdateThumb'
      #                                         ))
      # 
                                                
    def rpc_flibUpdateThumb(self,selection,checked_pkeys=None):
        checked_pkeys = checked_pkeys or []
        def apply_thumb(row):
            _checked = False
            ext_img = self.getResourceUri('filetype_icons/%s.png'%row['ext'].lower()) \
                      or self.getResourceUri('filetype_icons/_blank.png')
            if row['meta']:
                metabag = Bag(row['meta'])
            if row['item_id'] in checked_pkeys:
                _checked = True
            return dict(thumb= '<img border=0 src="%s" height="32px" />' %(metabag['thumb32_url'] or ext_img),_checked=_checked)
        selection.apply(apply_thumb)
    
    

        
        