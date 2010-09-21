# -*- coding: UTF-8 -*-
# 
"""Registered users tester"""
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme='tundra'
    dojo_version='11'
    def test_1_registered_users(self,pane):
        """Users tree"""
        bc = pane.borderContainer(height='340px',datapath='test1')
        left = bc.contentPane(region='left',width='250px',splitter=True)
        left.dataRemote('.curr_users.users','curr_users',cacheTime=2)
        left.tree(storepath='.curr_users',selected_page_id='.selected_page_id',_fired='^redraw')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='4px')
        fb.div('^.selected_page_id',lbl='Selected page')
        fb.textbox(value='^.path',lbl='Path')
        fb.textbox(value='^.value',lbl='Value')
        fb.button('Send',fire='.send')
        center.dataRpc('dummy','send_data_to_page',
                        v='=.value',p='=.path',_fired='^.send',
                        selected_page_id='=.selected_page_id',answer_path='test.answer')
        fb.div('^test.answer',lbl='Answer')
        
    
    def test_2_cleanup(self,pane):
        """Cleanup"""
        fb = pane.formbuilder(cols=1, border_spacing='4px',datapath='test2')
        fb.numbertextbox(value='^.age',lbl='Age',default_value=120)
        fb.button('cleanup',fire='.run_cleanup')
        fb.checkbox(value='^.cascade',label='cascade')
        fb.dataRpc('dummy','cleanup_pages',age='=.age',cascade='=.cascade',_fired='^.run_cleanup',_onResult='FIRE redraw;')
        
    def rpc_cleanup_pages(self,age=None,cascade=None):
        self.site.register.cleanup(max_age=age,cascade=cascade)
        

    def rpc_send_data_to_page(self,v=None,p=None,selected_page_id=None,answer_path=None):
        self.setInClientData( p, value=v,  page_id=selected_page_id,attributes=dict(from_page_id=self.page_id, answer_path=answer_path))
            
        
    def rpc_curr_users(self):
        return self.site.register.tree()