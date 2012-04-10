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
        self.maildashboard_center(framebc.borderContainer(region='center',margin='2px',datapath='.messages'))

    def maildashboard_center(self,bc):
        bottom = bc.contentPane(region='bottom',height='50%',margin='2px',
                                nodeId='messageBodyBox',splitter=True,datapath='.current').div('^.body')
        center = bc.contentPane(region='center',margin='2px')
        th = center.plainTableHandler(table='email.message',
                                condition='$mailbox_id=:m_id OR @message_mailboxes.mailbox_id=:m_id',
                                condition_m_id='=#mailBoxTree.tree.mailbox_id',
                                viewResource=':ViewFromDashboard',
                                grid_selected_body='#messageBodyBox.body',
                                #formResource=':FormFromDashboard',
                                grid_autoSelect=True,
                                virtualStore=True,extendedQuery=True,
                                grid_dragTags='message_row',
                                grid_rowCustomClassesCb="""function(row){
                                                        return (this._curr_mailbox_id && row['mailbox_id']!=this._curr_mailbox_id)? 'email_message_alias':null;
                                                    }""",
                                grid_subscribe_curr_mailbox_id='this.widget._curr_mailbox_id=$1')
        bar = th.view.top.bar.replaceSlots('#','5,queryfb,runbtn,queryMenu,*,receivebtn')
        bar.receivebtn.slotButton('Check',action='PUBLISH check_email;',disabled='^#mailBoxTree.tree.account_id?=!#v')
        
        th.view.dataController("PUBLISH curr_mailbox_id=curr_mailbox_id;",curr_mailbox_id="^#mailBoxTree.tree.mailbox_id")

        center.dataController("""grid.publish('runbtn',{"modifiers":null});""",
                        _fired="^#mailBoxTree.tree.mailbox_id",grid=th.view.grid)
        center.dataRpc('dummy', self.db.table('email.message').receive_imap, subscribe_check_email=True, 
                            account='=#mailBoxTree.tree.account_id')


    def maildashboard_left(self,frame):
        footer = frame.bottom.slotToolbar('*,addmailbox')
        footer.addmailbox.slotButton('!!Add mailbox',iconClass='iconbox add_record')
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
                            onDrop_gridrow="""
                                var pkeys = [];
                                var rowset = data.rowset;
                                if(!rowset || rowset.length==0){
                                    return false;
                                }
                                
                                dojo.forEach(rowset,function(r){pkeys.push(r['_pkey'])});
                                var kwargs = {'pkeys':pkeys,mailbox_id:dropInfo.treeItem.attr.pkey};
                                kwargs.alias = dropInfo.event.shiftKey || (rowset[0]['account_id'] != dropInfo.treeItem.attr.account_id);
                                if(kwargs.mailbox_id && kwargs.pkeys && kwargs.pkeys.length>0){
                                    genro.serverCall('_table.email.message.changeMailbox',kwargs,function(){});
                                }
                            """,
                            selectedLabelClass='selectedTreeNode',#autoCollapse=True,
                            selected_pkey='.tree.mailbox_id',
                            selected_account_id='.tree.account_id',
                            labelAttribute='caption',isTree=False,showRoot=False,
                            dropTags='message_row',
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


