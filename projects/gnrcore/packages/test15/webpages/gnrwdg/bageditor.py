# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    css_requires='public'
    
    def windowTitle(self):
        return 'bageditor'
         
    def test_0_firsttest(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px',background='lime')
        bc.contentPane(region='top').button('load node',action='genro.publish("test_editnode","")')
        bc.contentPane(region='center').bagNodeEditor(bagpath='gnr',nodeId='test')
    
    def test_1_firsttest(self,pane):
        bc = pane.borderContainer(height='600px')
        b = Bag('/Users/fporcari/sviluppo/goodsoftware/projects/mbe/instances/western/xmenu.xml')
        bc.data('.treestore.root', b,label='Root')
        bc.contentPane(region='left',width='200px').tree(storepath='.treestore', labelAttribute='label',selectedPath='.selectedPath',hideValues=True)
        bc.dataController("""
            var rows = treestore.getItem(selectedpath);
            var struct = new gnr.GnrBag();
            var header = new gnr.GnrBag();
            struct.setItem('view_0.rows_0',header);
            var store = new gnr.GnrBag();
            var i = 0;
            header.setItem('cell_0',null,{field:'nodelabel',width:'12em',name:'Node Label'});
            if(rows && rows.len && rows.len()){
                rows.forEach(function(n){
                        var attr = objectUpdate({},n.attr);
                        for(var k in attr){
                            if(!header.getNodeByAttr('field',k)){
                                header.setItem('cell_'+genro.getCounter(),null,{field:k,width:'10em',name:k,dtype:guessDtype(attr[k]),edit:true});
                            }
                        }
                        attr.nodelabel = n.label;
                        store.setItem(n.label,new gnr.GnrBag(attr));
                        i++;
                    },'static');
            }
            SET .bageditor.grid.struct = struct;
            SET .bageditor.store = store;
            """,selectedpath='^.selectedPath',treestore='=.treestore')
        
        frame = bc.contentPane(region='center').bagGrid(storepath='.store',datapath='.bageditor',structpath='.struct',
                                            grid_selfDragRows=True,grid_selfsubscribe_addrow="""
                                                var that = this;
                                                genro.dlg.prompt('Add row',{lbl:'Nodelabel',action:function(result){
                                                        var b = that.widget.storebag();
                                                        b.setItem(result,new gnr.GnrBag({nodelabel:result}));
                                                    }});
                                            """,grid_selfsubscribe_addcol="""
                                                var that = this;
                                                genro.dlg.prompt('Add col',{'widget':[{lbl:'name',value:'^.field'},
                                                                                 {lbl:'dtype',value:'^.dtype',wdg:'filteringSelect',values:'T:Text,N:Number,B:Boolean'}],
                                                                            action:function(result){
                                                                                        var b = genro.getData(that.attrDatapath('structpath'));
                                                                                        var kw = result.asDict();
                                                                                        kw.name = kw.field;
                                                                                        kw.edit = true;
                                                                                        b.setItem('#0.#0.cell_'+genro.getCounter(),null,kw);
                                                                                    }
                                                                            });

                                            """)
        frame.top.bar.replaceSlots('addrow','addrow,addcol').addcol.slotButton('Add col',publish='addcol')

        bc.dataController("""
            var b = treestore.getItem(selectedPath);
            var nv = _node.getValue();
            if(_reason=='child'){
                if(_triggerpars.kw.updvalue){
                    var nl = _node.getParentNode().label;
                    var kw = {};
                    kw[_node.label] = _triggerpars.kw.value;
                    b.getNode(nl).updAttributes(kw);
                }else if(_triggerpars.kw.evt=='ins' && nv instanceof gnr.GnrBag){
                    var pos = branch.index(_node.label);
                    b.setItem(_node.label,null,_node.getValue().asDict(),{_position:pos>=0?pos:null});
                }else if(_triggerpars.kw.evt=='del' && nv instanceof gnr.GnrBag){
                    b.popNode(_node.label);
                }
            }
        """,branch='^.bageditor.store',selectedPath='=.selectedPath',treestore='=.treestore')

    def test_2_component(self,pane):
        b = Bag('/Users/fporcari/sviluppo/goodsoftware/projects/mbe/instances/western/xmenu.xml')
        pane.data('.treestore.root', b,label='Root')
        pane.borderContainer(height='600px').contentPane(region='center').bagEditor(storepath='.treestore.root',labelAttribute='label',addrow=True,delrow=True,addcol=True)
