# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class MoverPlugin(BaseComponent):
    def __moverdialog(self,pane):
        dialog=pane.dialog(title='!!Save Mover',connect_onShowing='this.setRelativeData(".movername","");')
        box = dialog.div(width='20em')
        dlgwdg = dialog.js_widget
        fb = box.div(padding_right='10px',padding_top='30px',padding_bottom='30px').formbuilder(cols=1, border_spacing='4px',width='100%')
        fb.textbox(value='^.movername',lbl='!!Name',width='100%')
        bar = box.slotBar('*,cancbtn,savebtn',padding_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancbtn.slotButton("!!Cancel",action='dlg.hide();',dlg=dlgwdg)
        bar.savebtn.slotButton("!!Save",
            action="""var movername= GET .movername;
                      var data = GET .tablesgrid.data;
                      genro.rpcDownload('developer.downloadMover',{data:data,_download_name_:movername+'.gnrz',movername:movername});
        """,dlg=dlgwdg)
        return dlgwdg
    
    def __tablesgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('objtype', name='!!Type', width='5em')
        r.cell('reftable', name='!!Table', width='100%')
        r.cell('count', name='!!N', width='2em')
        r.cell('pkeys', hidden=True)
        r.cell('table', hidden=True)
    
    def __recordsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('_pkey',hidden=True)
        r.cell('objtype',hidden=True)
        r.cell('db_caption',name='!!Db',width='50%')
        r.cell('xml_caption',name='!!Mover',width='50%')
        
    @public_method
    def mover_getHPkeys(self,table=None,code=None):
        where = "$code ILIKE :code || '%%'"
        if code=='*':
            where = None
        return self.db.table(table).query(where=where,code=code).selection().output('pkeylist')
       

    def btn_datamover(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='case',tip='!!Mover plug-in',
                    connect_onclick="""SET left.selected='datamover';PUBLISH gnrdatamover_loadCurrent;genro.getFrameNode('standard_index').publish('showLeft');""",
                    nodeId='plugin_block_datamover')
                     
    def mainLeft_datamover(self, pane):
        """!!Mover"""
        frame = pane.framePane(datapath='gnr.datamover')
        frame.dataRpc('.tablesgrid.data','developer.loadCurrentMover',subscribe_gnrdatamover_loadCurrent=True)
        
        bar = frame.bottom.slotToolbar('*,trashlines')
        bar.trashlines.div(_class='iconbox trash',dropTarget=True,
                    onDrop_moverlines="FIRE .drop_moverlines = data;",
                    onDrop_recordlines="FIRE .drop_recordlines = data;",
                    connect_ondblclick='FIRE .drop_allmovers')
        bar = frame.top.slotToolbar('3,mvtitle,*,btnsave,btndl',mvtitle='!!Data Mover',mvtitle_font_weight='bold')
        bar.btnsave.slotButton("!!Save",iconClass='iconbox save',action="genro.serverCall('developer.saveCurrentMover',{data:data});",data='=.tablesgrid.data')
        bar.btndl.slotButton("!!Download",iconClass='iconbox inbox',
                                action="dlg.show();",dlg=self.__moverdialog(frame))
        bc = frame.center.borderContainer()
        top = bc.contentPane(region='top',height='30%',splitter=True,overflow='hidden')
        gridmover = top.includedview(datapath='.tablesgrid',storepath='.data',relativeWorkspace=True,struct=self.__tablesgrid_struct,
                        draggable_row=True,
                        onDrag="""if(dragInfo.dragmode == 'row') {
                            var rowset = dragValues.gridrow.rowset;
                            if(rowset.length>1){
                                return false;
                            }
                            var table = rowset[0].reftable;
                            dragValues['mover_'+table.replace('.','_')] =  {table:table,pkeys:rowset[0].pkeys,objtype:rowset[0].objtype};
                            dragValues['moverlines'] = rowset;
                        };""",
                        drop_ext='gnrz',
                        dropTarget_grid='dbrecords,nodeattr,dbselection,Files',dropTarget=True,dropTypes='dbrecords,nodeattr,Files',
                        autoSelect=True,
                        onDrop="""  if(!($2 instanceof Array)){
                                        return;
                                    }
                                    var f = files[0];
                                    var movername = f.name;
                                    setTimeout(function(){
                                    genro.rpc.uploadMultipart_oneFile(f,null,{uploadPath:'site:temp',filename:f.name,
                                                                        onResult:function(){
                                                                            genro.publish('gnrdatamover_loadCurrent');
                                                                        },
                                                                        uploaderId:'datamover'});
                                    },1)
                                    
                        """,
                        onDrop_dbrecords="""
                                            var table = data.table;
                                            var objtype = data.objtype;
                                            var reftable = data.reftable || table;  
                                            var movercode = reftable.replace('.','_')+'_'+objtype;  
                                            var griddata = this.getRelativeData('.data') || new gnr.GnrBag();
                                            var currow = griddata.getNode(movercode);
                                            currow = currow? currow.attr:{};
                                            var finalize = function(pkeys){
                                                var currpkeys = currow['pkeys'] || {};
                                                dojo.forEach(pkeys,function(pkey){currpkeys[pkey]=true;});
                                                currow['table'] = table;
                                                currow['reftable'] = reftable;
                                                currow['objtype'] = objtype;
                                                currow['pkeys'] = currpkeys
                                                currow['count'] = objectSize(currpkeys);
                                                griddata.setItem(movercode,null,currow);
                                            }           
                                            if (data.selectionName){
                                                genro.serverCall("getUserSelection",{selectionName:data.selectionName,sourcepage_id:dropInfo.dragSourceInfo.page_id,table:table,columns:'pkey'},
                                                                function(result){
                                                                    finalize(result);
                                                                });
                                            }else if(data.code){
                                                genro.serverCall("mover_getHPkeys",{code:data.code,table:table},
                                                    function(result){
                                                        finalize(result);
                                                    });
                                            }
                                            else if(data.pkeys){
                                                finalize(data.pkeys);
                                            }         
                                            """,
                                            selectedLabel='.currLabel')        
        center = bc.contentPane(region='center',margin_top='5px')
        gridrecords= center.includedview(datapath='.recordsgrid',storepath='.data',
                                    draggable_row=True,dragTags='mover',
                                    onDrag="""if(dragInfo.dragmode == 'row') {
                                                var rowset = dragValues.gridrow.rowset;
                                                var table = rowset[0].table;
                                                var pkeys = {};
                                                dojo.forEach(rowset,function(r){pkeys[r['_pkey']]=true});
                                                dragValues['mover_'+table.replace('.','_')] =  {table:table,pkeys:pkeys,objtype:rowset[0].objtype};
                                                dragValues['recordlines'] = rowset;

                                            };""",
                                    relativeWorkspace=True,struct=self.__recordsgrid_struct)
                                    
        frame.dataRpc('.recordsgrid.data','developer.getMoverTableRows',movercode='^.tablesgrid.currLabel',
                        tablerow='==this.getRelativeData(".tablesgrid.data").getNode(movercode).attr;',
                        _if='movercode',_else='return new gnr.GnrBag();')
        
        frame.dataController("""
        if(moverlines){
            console.log(moverlines);
        }
        if(recordlines){
            console.log(recordlines);
        }
        """,moverlines="^.drop_moverlines",recordlines="^.drop_recordlines",
            gridmover=gridmover,gridrecords=gridrecords)
    
    def onUploading_datamover(self, file_url=None, file_path=None,
                                 description=None, titolo=None, **kwargs):
        self.developer.onDroppedMover(file_path=file_path)
        
        
        
        
                        