# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class MoverPlugin(BaseComponent):
    def __moverdialog(self,pane):
        dialog=pane.dialog(title='!!Save Mover',connect_onShowing='this.setRelativeData(".dlg.movername",this.getRelativeData(".movername"))')
        box = dialog.div(width='20em')
        dlgwdg = dialog.js_widget
        fb = box.div(padding_right='10px',padding_top='30px',padding_bottom='30px').formbuilder(cols=1, border_spacing='4px',datapath='.dlg',width='100%')
        fb.textbox(value='^.movername',lbl='!!Name',width='100%')
        bar = box.slotBar('*,cancbtn,savebtn',padding_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancbtn.slotButton("!!Cancel",action='dlg.hide();',dlg=dlgwdg)
        bar.savebtn.slotButton("!!Save",
            action="""var that = this;
                      genro.serverCall('developer.saveMover',{'_sourceNode':this,movername:'=.dlg.movername',data:'=.tablesgrid.data'},
                                        function(){
                                            dlg.hide();
                                            that.setRelativeData('.movername',that.getRelativeData('.dlg.movername'));
                                        });
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
        r.cell('_pkey', name='!!Pkey',width='6em',hidden=True)
        r.cell('db_caption',name='!!Db',width='50%')
        r.cell('xml_caption',name='!!Mover',width='50%')
        
    def mainLeft_datamover(self, pane):
        """!!Mover"""
        frame = pane.framePane(datapath='gnr.datamover')
        bar = frame.bottom.slotToolbar('*,trashlines')
        bar.trashlines.div(_class='iconbox trash',dropTarget=True,
                    onDrop_moverlines="FIRE .drop_moverlines = data.rows;",
                    onDrop_recordlines="FIRE .drop_recordlines = data.rows;")
        bar = frame.top.slotToolbar('3,currmover,*,btnload,btnsave,btndl')
        bar.currmover.div('==_movername||"New Mover"',_movername='^.movername')
        bar.btnload.div(_class='iconbox folder').menu(_class='smallmenu',modifiers='*',action='SET .movername=$1.mover;FIRE .loadMover;',
                                                    storepath='.movers')
        bar.dataRemote('.movers','developer.listMovers',cacheTime=5)
        bar.btnsave.slotButton("!!Save",iconClass='iconbox save',action="dlg.show();",dlg=self.__moverdialog(frame))
        bar.btndl.slotButton("!!Download",iconClass='iconbox inbox',
                                action="""genro.serverCall('developer.downloadMover',{movername:'=.movername',_sourceNode:this},
                                                            function(result){
                                                                genro.download(result);
                                                            });""",disabled='^.movername?=!#v')
        bc = frame.center.borderContainer()
        top = bc.contentPane(region='top',height='30%',splitter=True,overflow='hidden')
        gridmover = top.includedview(datapath='.tablesgrid',storepath='.data',relativeWorkspace=True,struct=self.__tablesgrid_struct,
                        draggable_row=True,onDrag="""if(dragInfo.dragmode == 'row') {dragValues["moverlines"] = {rows:dragValues.gridrow.rowset}};""",
                        drop_ext='gnrz',
                        dropTarget_grid='dbrecords,Files',dropTarget=True,dropTypes='dbrecords,Files',
                        
                        onDrop="""var f = files[0];
                                    genro.rpc.uploadMultipart_oneFile(f,null,{uploadPath:'site:temp',filename:f.name,
                                                                        onResult:function(){},
                                                                        uploaderId:'datamover'});
                        """,
                        onDrop_dbrecords="""var table = data.table;
                                            var objtype = data.objtype;
                                            var reftable = data.reftable || table;  
                                            var movercode = reftable.replace('.','_')+'_'+objtype;    
                                            var griddata = this.getRelativeData('.data') || new gnr.GnrBag();
                                            var currow = griddata.getNode(movercode);
                                            currow = currow? currow.attr:{};
                                            var currpkeys = currow['pkeys'] || {};
                                            dojo.forEach(data.pkeys,function(pkey){currpkeys[pkey]=true;});
                                            currow['table'] = table;
                                            currow['reftable'] = reftable;
                                            currow['objtype'] = objtype;
                                            currow['pkeys'] = currpkeys
                                            currow['count'] = objectSize(currpkeys);
                                            griddata.setItem(movercode,null,currow);""",selectedLabel='.currLabel')
        frame.dataRpc('.tablesgrid.data','developer.loadMover',movername='=.movername',_if='movername',_else='return new gnr.GnrBag();',_fired='^.loadMover')
        
        center = bc.contentPane(region='center',margin_top='5px')
        gridrecords= center.includedview(datapath='.recordsgrid',storepath='.data',
                                    draggable_row=True,onDrag="""if(dragInfo.dragmode == 'row') {dragValues["recordlines"] = {rows:dragValues.gridrow.rowset}};""",
                                    relativeWorkspace=True,struct=self.__recordsgrid_struct)
        frame.dataRpc('.recordsgrid.data','developer.getMoverTableRows',movercode='^.tablesgrid.currLabel',
                        tablerow='==this.getRelativeData(".tablesgrid.data").getNode(movercode).attr;',
                        movername='=.movername',_if='movercode',_else='return new gnr.GnrBag();')
        
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
        
        
        
        
                        