#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
from gnr.core.gnrhtml_n import GnrHtmlBuilder

class GnrCustomWebPage(object):
    py_requires='public:IncludedView'
    def windowTitle(self):
         return '!!Template editor'

    def main(self, root, **kwargs):
        root.dataRemote('tplbag','getHtmlSrc')
        bc = root.borderContainer()
        self.left_editor(bc.borderContainer(region='left',width='40%',background='silver',splitter=True))
        bc.contentPane(region='center',overflow='hidden') #.iframe(height='100%',width='100%',border=0,src='^iframe_url')
        #bc.dataFormula('iframe_url',"genro.remoteUrl('xyz',{mode:'text',bag:bag})",_onStart=True,bag='=tplbag',_fired='^loadiframe')
        
    def left_editor(self,bc):

        bc.dataController("""
                          //UPDATE CHANGES
                          var modified_path = GET current_path;
                          if (modified_path){
                              var modified_node = GET current_node;
                              var attributesList = modified_node.getNodes();
                              var attrToUpd = {};
                              for (var i=0; i<attributesList.length;i++ ){
                                    var val = attributesList[i].getValue();
                                    attrToUpd[val.getItem('key')] = val.getItem('value');
                               }
                               genro._data.setAttr(modified_path,attrToUpd);
                          }""",_fired='^update_tree')
                          
        bc.dataController("""
                          //PREPARE THE GRID
                          FIRE update_tree;
                          var current_path = fullpath.slice(5)
                          SET current_path = current_path;
                          var current = genro._data.getNode(current_path);
                          var attrs = current.attr;
                          var gridcontent = new gnr.GnrBag();
                          var count = 1;
                          for (var attr in attrs){
                                var nodecontent = new gnr.GnrBag();
                                nodecontent.setItem('key',attr);
                                nodecontent.setItem('value',attrs[attr]);
                                gridcontent.setItem('r_'+count,nodecontent);
                                count++;
                          }
                          SET current_node = gridcontent;
                          """,fullpath="^tplbag_nodepath",_fired='=append_node')
        bc.dataController("""
                            FIRE update_tree;
                            selected_nodepath = selected_nodepath.slice(5);
                            var newpath= selected_nodepath+'.'+node_type;
                            genro._data.addItem(newpath,new gnr.GnrBag());
                            """,node_type="^append_node",
                            selected_nodepath='=tplbag_nodepath')
        top = bc.contentPane(region='top',height='70%',splitter=True)
        top.dropDownButton("Newnode",disabled='^disabled_menu').menu(storepath='nodetypes',
                                          action='FIRE append_node=this.attr.elemtype;')
        top.button('load iframe',fire='loadiframe')
        
        top.dataFormula("disabled_menu", "(nodepath==null)",nodepath='^tplbag_nodepath',_onStart=True)
        nodetypes = Bag()
        nodetypes.setItem('layout',None,caption='Layout',elemtype='layout')
        nodetypes.setItem('row',None,caption='Row',elemtype='row')
        nodetypes.setItem('cell',None,caption='Cell',elemtype='cell')
  
        top.data('nodetypes',nodetypes)
        top.tree(storepath='tplbag',margin='10px',
                inspect='shift',selectedPath='tplbag_nodepath')
   
        center = bc.borderContainer(region='center',margin='5px')
        iv = self.includedViewBox(center,label='!!Edit node',datamode='bag',
                                 storepath='current_node', struct=self.element_struct(),
                                 autoWidth=True,add_action=True,del_action=True,
                                 editorEnabled=True)
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='key')
        gridEditor.textbox(gridcell='value')

    def mytest(self):
        builder = GnrHtmlBuilder() 
        self.htmltest(builder.body)
        return html
        
    def rpc_xyz(self,bag=None,**kwargs):
        print bag
        return self.mytest()
        
    def rpc_getHtmlSrc(self,**kwargs):
        builder = GnrHtmlBuilder() 
        self.htmltest(builder.body)
        return builder.html
        
    def htmltest(self,pane):
        d=180
        layout = pane.layout(width=d,height=d,um='mm',top=10,left=10,border_width=.3,
                            lbl_height=4,lbl_class='z1',content_class='content',_class='mmm')

        layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
        layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
        layout.style(".content{font-size:12pt;text-align:center;}")
        layout.style(".myclass{font-size:18pt;text-align:center;background-color:yellow;}")
        layout.style(".uuu{color:red;}")
        layout.style(".mmm{font-family:courier;}")

        x=d/3.
        r = layout.row(_class='uuu')
        r.cell('foo',lbl='name',_class='myclass')
        r.cell('bar',width=x,lbl='weight')
        
        r.cell('baz',lbl='time')
        r = layout.row(height=x)
        r.cell('foo',lbl='cc')
        subtable=r.cell(width=x)
        r.cell('baz',lbl='dd')
        r = layout.row()
        r.cell('foo',lbl='alfa')
        r.cell('bar',width=x,lbl='beta')
        r.cell('baz',lbl='gamma')
        layout=subtable.layout(name='inner',um='mm',border_width=.3,top=0,left=0,right=0,bottom=0,
                            border_color='green',
                            lbl_height=4,lbl_class='z1',content_class='content')
        x=x/2.
        r = layout.row()
        r.cell('foo')
        r.cell('bar',width=x)
        r.cell('baz')
        r = layout.row(height=x)
        r.cell('foo')
        r.cell('bar',width=x)
        r.cell('baz')
        r = layout.row()
        r.cell('foo')
        r.cell('bar',width=x)
        r.cell('baz')

    def element_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('key', name='Key', width='10em')
        r.cell('value', name='Value', width='10em')
        return struct
        
