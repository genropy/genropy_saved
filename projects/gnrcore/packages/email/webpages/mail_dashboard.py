# -*- coding: UTF-8 -*-

# Created by FPorcari on 2011-03-25.
# Copyright (c) 2011 Softwell sas. All rights reserved.

from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    maintable='email.mailbox'
    css_requires='emailstyles'
    py_requires="""public:Public,th/th:TableHandler,th/th_tree:TableHandlerTree"""  
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Email Dashboard'
    
    def main(self, root, **kwargs):
        framebc = root.rootBorderContainer(datapath='main',_class='hideSplitter')
        self.maildashboard_left(framebc.framePane(region='left',width='220px',margin='2px',datapath='.configuration',_class='pbl_roundedGroup',splitter=True))
        self.maildashboard_center(framebc.framePane(region='center',margin='2px',datapath='.messages'))

    def maildashboard_center(self,bc):
        center = bc.contentPane(region='center',margin='2px')
        th = center.borderTableHandler(table='email.message',
                                condition='$mailbox_id=:m_id',
                                condition_m_id='=#mailBoxTree.tree.mailbox_id',
                                viewResource=':ViewFromDashboard',
                                formResource=':FormFromDashboard',
                                grid_autoSelect=True,
                                virtualStore=True,extendedQuery=True)
        bar = th.view.top.bar.replaceSlots('#','5,queryfb,runbtn,queryMenu,*,receivebtn')
        bar.receivebtn.slotButton('Check',action='PUBLISH check_email;',disabled='^#mailBoxTree.tree.account_id?=!#v')
        center.dataController("""grid.publish('runbtn',{"modifiers":null});""",
                        _fired="^#mailBoxTree.tree.mailbox_id",grid=th.view.grid)
        center.dataRpc('dummy', self.db.table('email.message').receive_imap, subscribe_check_email=True, 
                            account='=#mailBoxTree.tree.account_id')

        
        # grid = th.view.grid
       # grid.dataController("grid._classificazione_id=classificazione_id",classificazione_id="^main.tree.pkey",grid=grid.js_widget)
       # grid.attributes.update(dragTags='riga_frase',
       #                         onDrag="""dragValues['riga_frase'] = dragValues.gridrow.rowset;""",
       #                         rowCustomClassesCb="""function(row){
       #                                                 return row['_righe_alias_classificazione_id']==this._classificazione_id? 'riga_alias':null;
       #                                               }""")
       # th.form.store.handler('load',default_classificazione_id='=#FORM/parent/#FORM.record.id')


        
    def maildashboard_left(self,frame):
        frame.tree(storepath='.store.root',_class='mailBoxTree',nodeId='mailBoxTree', hideValues=True,
                            getLabel="""if(node.attr._counter){
                                            return 'innerHTML:<div class="dijitTreeLabel mb_treecaption">'+node.attr.caption+'</div><div class="mb_treecounter">'+node.attr._counter+'</div>'
                                        }else{
                                            return 'innerHTML:<div class="dijitTreeLabel mb_treecaption">'+node.attr.caption+'</div>';
                                        }""",
                            margin='6px',draggable=True,
                            getLabelClass="""
                                            var cls = (this.currentSelectedNode && this.currentSelectedNode.item == node)?['selectedTreeNode']:[];
                                            if(node.attr.labelClass){
                                                cls.push(node.attr.labelClass);
                                            }
                                            return cls.join(' ');""",
                            getIconClass="""if(!node.attr.pkey){
                                return 'iconbox folder'
                            }
                            if(node.attr.system_code=='01'){
                                return 'iconbox tray_mail'
                            }else if(node.attr.system_code=='02'){
                                return 'iconbox paper_plane'
                            }else if(node.attr.system_code=='03'){
                                return 'iconbox folder';
                            }else if(node.attr.system_code=='04'){
                                return 'iconbox trash';
                            }else{
                                return 'iconbox folder';
                            }""",
                            selectedLabelClass='selectedTreeNode',autoCollapse=True,
                            selected_pkey='.tree.mailbox_id',
                            selected_account_id='.tree.account_id',
                            labelAttribute='caption',isTree=False,showRoot=False,
                            dropTarget=True)
        
        mboxtbl = self.db.table('email.mailbox')
        b = Bag()
        user_id = self.avatar.user_id
        root = Bag()
        b.setItem('root',root,caption='!!Mailboxes',child_count=1)
        accounts = self.db.table('email.account').query(where='@account_users.user_id=:user_id',user_id=user_id,columns='$account_name').fetch()
        for acc in accounts:
            root.setItem(acc['pkey'],mboxtbl.getMailboxResolver(account_id=acc['pkey']),caption=acc['account_name'],
                        labelClass='mb_account',account_id=acc['pkey'])
        root.setItem('common',mboxtbl.getMailboxResolver(),caption='!!Common',labelClass='mb_account')
        root.setItem('curr_user',mboxtbl.getMailboxResolver(user_id=user_id),caption='!!User',labelClass='mb_account')
        frame.data('.store',b) 


