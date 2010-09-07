# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag

class DynamicForm(BaseComponent):
    def dynamicForm(self,parent,storepath=None,nodeId=None,row_types=None,type_field=None,label=None,
                    defaultstore=None,disabled=None,reloader=None,addRemove=True,**kwargs):
        """params:
           parent:where you append DynamicForm
           storepath:where the DynamicForm set/get the values
           nodeId: the id of the DynamicForm: eg: FIRE #myform.add_row, FIRE #myform.del_row = 2;
           row_types: a dict {'fax':'Fax'} that create the menu for adding row
           type_field: 'contact_type'
           defaultstore : a bag of defaults row
           reloader: 
           """
        menu = None
        controllerPath = '_wks.%s' %nodeId
        if isinstance(row_types,dict):
            menu = Bag()
            for k,v in row_types.items():
                menu.setItem(k,None,label=v)
        containerId ='%s_box' %nodeId 
        defaultstore = defaultstore or Bag()
        controller = parent.dataController(datapath=controllerPath,nodeId=nodeId)
        controller.data('.menu',menu)
        controller.data('.defaultstore',defaultstore)
        controller.dataFormula(".locked", "locked",locked=disabled)
        controller.dataController("""
                            var box = genro.nodeById(boxId);
                            box.clearValue();
                            if(del_row){
                                var nodeToDel = genro._firingNode;
                                var del_path = nodeToDel.absDatapath();
                                genro._data.popNode(del_path);
                                
                            }
                            var storebag = this.getRelativeData(storepath);
                            if(!storebag){
                                storebag = defaultstore;
                                this.setRelativeData(storepath,storebag);
                            }
                           
                            box._('div',{remote:{method:'df_initialize',storebag:storebag,dfId:dfId,
                                               type_field:type_field,menu:menu}});
                                               
                            """,boxId=containerId,_fired=reloader,storepath=storepath,del_row='^.del_row',
                            dfId=nodeId,defaultstore='=.defaultstore',type_field=type_field,menu='=.menu')
        controller.dataController("""
                               var box = genro.nodeById(boxId);
                               var newRow = new gnr.GnrBagNode(null,'label');
                               var row_datapath = '.r_'+newRow._id;
                               this.setRelativeData(storepath+row_datapath,newRow);
                               var remotePars ={'method':'df_row',row_type:add_row,dfId:dfId,menu:menu};
                               box._('div',{datapath:row_datapath,remote:remotePars});
                                """,
                                add_row="^.add_row",dfId=nodeId,storepath=storepath,
                                boxId=containerId,type_field=type_field,menu='=.menu')
                                
        bc = parent.borderContainer(_class='pbl_roundedGroup',**kwargs)
        top = bc.contentPane(_class='pbl_roundedGroupLabel')
        top.div(label,float='left')
        top.dropDownButton('Add',baseClass='no_background',iconClass='buttonIcon icnBaseAdd',float='right',showLabel=False).menu(storepath='.menu',
                                    action='FIRE .add_row=$1.fullpath;',_class='smallmenu',
                                    datapath=controllerPath)
        bc.div(nodeId=containerId,datapath=storepath)
    
    def remote_df_initialize(self,pane,storebag=None,dfId=None,type_field=None,menu=None):
        for i,node in enumerate(storebag):
            row = node.value
            self.remote_df_row(pane.div(datapath='.%s' %node.label),row_type=row[type_field],dfId=dfId,menu=menu)
            
    def remote_df_row(self,pane,row_type=None,dfId=None,menu=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        disabled='^#%s.locked' %dfId
        if hasattr(self,'%s_%s_row' %(dfId,row_type)):
            cb = getattr(self,'%s_%s_row' %(dfId,row_type))
        else:
            cb = getattr(self,'%s_row' %(dfId))
        cb(fb.div(lbl=menu['%s?label' %row_type],disabled=disabled))
        fb.button(baseClass='no_background',_class='icnBaseTrash',action='FIRE #%s.del_row;' %dfId,disabled=None)