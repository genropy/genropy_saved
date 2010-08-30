# -*- coding: UTF-8 -*-
# 
"""Registered users tester"""
class GnrCustomWebPage(object):
    py_requires="testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme='claro'
    
    def test_1_registered_users(self,pane):
        """Users tree"""
        bc = pane.borderContainer(height='500px',datapath='test1')
        left = bc.contentPane(region='left',width='250px',splitter=True)
        left.dataRemote('.curr_users.users','curr_users',cacheTime=2)
        left.tree(storepath='.curr_users',selected_user='^.user')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='4px')
        fb.div('^.user',lbl='Selected user')
        fb.textbox(value='^.path',lbl='Path')
        fb.textbox(value='^.value',lbl='Value')
        fb.button('Send',fire='.send')
        center.dataRpc('dummy','send_data_to_user',
                        v='=.value',p='=.path',_fired='^.send',
                        user='=.user')
        

    def rpc_send_data_to_user(self,v=None,p=None,user=None):
        user = user or self.user
        with self.userStore(user=user) as store:
            store.setItem(p,v)
            
        
    def rpc_curr_users(self):
        return self.site.register_user.user_tree()