# -*- coding: UTF-8 -*-

# validate_password.py
# Created by Francesco Porcari on 2011-03-16.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.textbox(value='^.testpwd')
        pane.button('test',fire='.run')
        pane.dataRpc('dummy','checkPwd',value='=.testpwd',_onResult='console.log(result);',_fired='^.run')
        
    
    def rpc_checkPwd(self, value=None,**kwargs):
        user = self.db.table('adm.user').record(username=self.user).output('bag')
        return self.application.validatePassword(value, user=user)