#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

from builtins import str
import os
import tempfile
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrlang import  GnrException
from gnr.core.gnrbag import Bag
from gnr.lib.services import GnrBaseService,BaseServiceType
from gnr.lib.services.storage import StorageNode
from collections import defaultdict
from pygit2 import Repository,GIT_MERGE_ANALYSIS_UP_TO_DATE,GIT_MERGE_ANALYSIS_FASTFORWARD
from pygit2 import GIT_MERGE_ANALYSIS_NORMAL

from gnr.lib.services.git import GitService


def find_dotgit(path, parent_path=None):
    if path==parent_path:
        return None,None
    if os.path.isdir(os.path.join(path,'.git')):
        return os.path.basename(path),path
    return find_dotgit(os.path.dirname(path),path)


class Service(GitService):
    
    def find_repos(self):
        folders = dict()
        folders['instance'] = self.parent.getInstanceFolder()
        folders['site'] = self.parent.site_path
        folders['genropy'] = self.parent.gnrapp.config['gnr.environment_xml.environment.gnrhome?value']
        for pkg in self.parent.gnrapp.packages.values():
            folders['pkg_%s'%pkg.id]= pkg.packageFolder
        repos = defaultdict(list)
        repos_bag = Bag()
        self.data = Bag()
        self.data['folders'] = Bag(folders)

        for element in folders:
            repo_name, repo_path = find_dotgit(folders[element])
            repos[(repo_name, repo_path)].append(element)
        for (repo_name, repo_path), elements in repos.items():
            if not repo_path:
                continue
            repos_bag.addItem(repo_name,repo_path,dict(name=repo_name,
                path=repo_path,elements=','.join(elements)))
        self.data['repositories'] = repos_bag

    def get_repo_path(self, repo_name):
        return self.data['repositories'][repo_name]

    def get_repo_attrs(self, repo_name):
        return self.data['repositories'].getAttr(repo_name)

    def get_repository(self, repo_name):
        return Repository(self.get_repo_path(repo_name))
        

    def _get_repo_info(self, repo_name):
        repo = self.get_repository(repo_name)
        branch = repo.branches[repo.head.shorthand]
        upstream = repo.lookup_reference(branch.upstream.name).target
        local = repo.head.target
        ahead, behind = repo.ahead_behind(local, upstream)
        changes = len(repo.diff())
        self.data.setAttr('repositories.%s'%repo_name, changes=changes, 
            ahead=ahead, behind=behind, branch=branch.shorthand)

    def update_repos_info(self):
        for repo_name in self.data['repositories'].keys():
            self._get_repo_info(repo_name)

    def look_repos(self):
        self.find_repos()
        self.update_repos_info()

    
    def pull(self, repo, repo_name):
        self._get_repo_info(repo_name)
        if self.data['repositories.%s?changes'%repo_name] or \
            not self.data['repositories.%s?behind'%repo_name]:
            return
        repo = self.get_repository(repo_name)
        branch = repo.branches[repo.head.shorthand]
        remote = repo.remotes[branch.upstream.remote_name]
        remote.fetch()
        local = repo.head.target
        upstream = repo.lookup_reference(branch.upstream.name).target
        merge_result, _ = repo.merge_analysis(upstream)
        if merge_result & GIT_MERGE_ANALYSIS_UP_TO_DATE:
            return
        elif merge_result & GIT_MERGE_ANALYSIS_FASTFORWARD:
            repo.checkout_tree(repo.get(upstream))
            try:
                master_ref = repo.lookup_reference(branch.name)
                master_ref.set_target(upstream)
            except KeyError:
                repo.create_branch(branch, repo.get(upstream))
            repo.head.set_target(upstream)
        else:
            raise AssertionError('Unknown merge analysis result')


