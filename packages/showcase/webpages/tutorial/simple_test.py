# -*- coding: UTF-8 -*-
# 
"""Simple test"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_simple(self, pane):
        """Simple Test"""
        pane.div("""We show here some features of this GnrWebPage istance""",
                    font_size='1.2em',margin_left='15px',color='teal')
        
        fb = pane.formbuilder(lbl_color='teal')
        fb.div(value=self.auto_polling,lbl='auto_polling')
        fb.div(value=self.dojo_version,lbl='dojo_version')
        fb.div(value=self.locale,lbl='locale')
        fb.div(value=self.page_id,lbl='page_id')
        fb.div(value=self.page_refresh,lbl='page_refresh')
        fb.div(value=self.page_timeout,lbl='page_timeout')
        fb.div(value=self.pagename,lbl='pagename')
        fb.div(value=self.pagepath,lbl='pagepath')
        fb.div(value=self.pagetemplate,lbl='pagetemplate')
        fb.div(value=self.parentdirpath,lbl='parentdirpath')
        fb.div(value=self.path_url,lbl='path_url')
        fb.div(value=self.siteFolder,lbl='siteFolder')
        fb.div(value=self.siteName,lbl='siteName')
        fb.div(value=self.theme,lbl='theme')
        fb.div(value=self.userFolder,lbl='userFolder')
        fb.div(value=self.user_polling,lbl='user_polling')
        fb.div(value=self.userStore,lbl='userStore')
        fb.div(value=self.userTags,lbl='userTags')
        fb.div(value=self.user_agent,lbl='user_agent')
        fb.div(value=self.user_ip,lbl='user_ip')
        fb.div(value=self.windowTitle(),lbl='windowTitle')
        fb.div(value=self.workdate,lbl='workdate')