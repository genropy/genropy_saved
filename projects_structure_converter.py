# -*- coding: UTF-8 -*-
import sys
import os
import shutil
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.app.gnrdeploy import PathResolver
from gnr.app.gnrconfig import gnrConfigPath

class ProjectConverter(object):
    def __init__(self):
        self.environment = Bag(os.path.join(gnrConfigPath(),'environment.xml'))
        self.projects_paths = self.environment['projects'].digest('#a.path')
    
    def run(self):
        for prpath in self.projects_paths:
            print 'prpath',prpath
            for prjname,prgval in DirectoryResolver(os.path.expanduser(prpath))().items():
                print 'project',prjname
                self.convertProjectOne(prjname,prgval)
    
    def relpath(self,path):
        userpath = os.path.expanduser('~')
        path = os.path.expanduser(path)
        userpath = userpath.split(os.sep)
        path = path.split(os.sep)
        if userpath[0]=='':
            userpath.pop(0)
        if path[0]=='':
            path.pop(0)
        while userpath and userpath[0] == path[0]:
            userpath.pop(0)
            path.pop(0)
        return os.path.join(*path)
 
    def getDestPath(self,sourcepath):
        sourcepath = self.relpath(sourcepath)
        pathlist = sourcepath.split(os.sep)
        destpath = ['~']+os.path.join(['%s_new' %pathlist[0]]+pathlist[1:])
        return os.path.expanduser(os.path.join(*destpath))

    def convertProjectOne(self,prgname,prgcontent):
        for elemNode in prgcontent.nodes:
            if elemNode.label not in ['instances','sites']:
                elem_path = elemNode.attr['abs_path']
                #print 'copio',packages_path,'in',self.getDestPath(packages_path)
                if os.path.isdir(elem_path):
                    shutil.copytree(elem_path,self.getDestPath(elem_path))
                else:
                    folder = os.path.dirname(self.getDestPath(elem_path))
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    shutil.copy(elem_path,self.getDestPath(elem_path))
        sites = prgcontent['sites'] or Bag()
        if 'instances' in prgcontent:
            for instanceNode in prgcontent['instances'].nodes:
                sourcepath = instanceNode.attr['abs_path']
                destInstancePath = self.getDestPath(sourcepath)
                destConfigPath = os.path.join(destInstancePath,'config')
                shutil.copytree(sourcepath,destConfigPath,symlinks=True)
                siteNode = sites.getNode(instanceNode.label)
                if siteNode:
                    destSitePath = os.path.join(destInstancePath,'site')
                    shutil.copytree(siteNode.attr['abs_path'],destSitePath,symlinks=True)
                    rootfile = os.path.join(destSitePath,'root.py')
                    if os.path.exists(rootfile):
                        shutil.move(rootfile,os.path.join(destInstancePath,'root.py'))
                    siteconfig = os.path.join(destSitePath,'siteconfig.xml')
                    if os.path.exists(siteconfig):
                        shutil.move(siteconfig,os.path.join(destConfigPath,'siteconfig.xml'))

if __name__ == '__main__':
    p = ProjectConverter()
    p.run()