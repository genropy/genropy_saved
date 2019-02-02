# -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.


from builtins import object
class GnrCustomWebPage(object):
    py_requires = 'services/ftp/pysftp/component:SftpClient'
    auth_main='admin'

    #FOR ALTERNATE MAIN HOOKS LOOK AT public:TableHandlerMain component
    def main(self,root,**kwargs):
        callArgs = self.getCallArgs('ftpname')  
        root.sftpClientLayout(callArgs['ftpname'],datapath='main')