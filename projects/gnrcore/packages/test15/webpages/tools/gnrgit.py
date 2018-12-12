# -*- coding: utf-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.


from gnr.core.gnrbag import  Bag
from gnr.core.gnrgit import GnrGit
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull"""

    def test_0_config_tree(self,pane):
        fb = pane.formbuilder()
        fb.textbox(value='^.repo_path',lbl='Repository path',width='40em')
        fb.textbox(value='^.remote_origin',lbl='Origin',width='40em')
        fb.textbox(value='^.remote_user',lbl='Username',width='40em')
        fb.textbox(value='^.remote_password',lbl='Username',width='40em')

        fb.tree(storepath='.repo_config',lbl='Config')
        fb.dataRpc('.repo_config',self.getRepoConfig,repopath='^.repo_path',_if='repopath',_else='return gnr.GnrBag()')

    @public_method
    def getRepoConfig(self,repopath=None):
        return GnrGit(repopath).config

    def test_2_config_tree(self,pane):
        pass