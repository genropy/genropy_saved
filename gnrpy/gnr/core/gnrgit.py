#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gnrgit.py
#
#  Created by Francesco Porcari
#  Copyright (c) 2018 Softwell. All rights reserved.

#from builtins import object
from dulwich.client import HttpGitClient
from dulwich.repo import Repo
from gnr.core.gnrbag import  Bag


class GnrGit(object):
    def __init__(self,repo_path,remote_origin=None,remote_user=None,remote_password=None):
        self.repo = Repo(repo_path)
        self.config = Bag(self.repo.get_config())
        self.remote_origin = remote_origin
        self.remote_user = remote_user
        self.remote_password = remote_password
        if self.remote_origin:
            self.remote_url = self.config['remote.%s.url' %self.remote_origin]
            self.remote_client = HttpGitClient(self.remote_url,username=remote_user,password=remote_password)

    def get_refs(self,path):
        self.remote_client.get_refs(path)
    
    
