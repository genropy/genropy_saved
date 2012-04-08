# -*- coding: UTF-8 -*-

# Created by FPorcari on 2011-03-25.
# Copyright (c) 2011 Softwell sas. All rights reserved.

class GnrCustomWebPage(object):
    maintable='email.mailbox'
    py_requires="""public:Public,gnrcomponents/htablehandler:HTableHandler,th/th:TableHandler"""  
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Email Dashboard'
    
    def main(self, root, **kwargs):
        framebc = root.rootBorderContainer(datapath='main',_class='hideSplitter')
        self.mailbox_tree(framebc.framePane(region='left',width='300px',margin='2px',_class='pbl_roundedGroup',datapath='.mailboxe_manager'))
        self.messages_handler(framebc.framePane(region='center',margin='2px'))

    def messages_handler(self,bc):
        return
        center = bc.contentPane(region='center',datapath='#FORM',margin='2px')
        th = center.dialogTableHandler(table='email.message',
                                condition='$mailbox_id=:m_id',
                                condition_m_id='^#FORM.pkey',
                                viewResource=':ViewFromMailbox',
                                formResource=':FormFromMailbox')
        # grid = th.view.grid
       # grid.dataController("grid._classificazione_id=classificazione_id",classificazione_id="^main.tree.pkey",grid=grid.js_widget)
       # grid.attributes.update(dragTags='riga_frase',
       #                         onDrag="""dragValues['riga_frase'] = dragValues.gridrow.rowset;""",
       #                         rowCustomClassesCb="""function(row){
       #                                                 return row['_righe_alias_classificazione_id']==this._classificazione_id? 'riga_alias':null;
       #                                               }""")
       # th.form.store.handler('load',default_classificazione_id='=#FORM/parent/#FORM.record.id')


        
    def mailbox_tree(self,frame):
        bar = frame.bottom.slotToolbar('3,addbtn,*')
        bar.addbtn.slotButton('!!New Mailbox',iconClass='iconbox add_row',
                            action="""genro.formById("mailbox_form").newrecord({parent_code:curr_parent_code});""",
                            curr_parent_code='=.tree.code')
        frame.thFormHandler(table='email.mailbox',formResource=':Form',modal=True,
                                        dialog_height='450px',dialog_width='800px',dialog_title='^.form.controller.title',
                                        formId='mailbox_form',
                                        datapath='.mailbox')  
        tree = frame.hTableTree(table=self.maintable,storepath='.store',
                        connect_ondblclick="""function(evt){
                                                var n = dijit.getEnclosingWidget(evt.target);
                                                genro.formById("mailbox_form").load({destPkey:n.item.attr.pkey});
                                             }""")
        tree.htableStore(table=self.maintable,storepath='.store')

    def email_mailbox_form(self,pane,table=None,disabled=None,**kwargs):
        bc = pane.borderContainer(**kwargs)
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px',disabled=disabled, table=table,width='600px')
        fb.field('child_code',width='8em')
        fb.field('account_id',width='100%',lbl='Account',readOnly='^.parent_code',hasDownArrow=True)
        fb.field('description',colspan=2,width='100%')
    


