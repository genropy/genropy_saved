#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo Hello World """

import datetime, subprocess
from gnr.core.gnrbag import Bag, DirectoryResolver

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root,padding='2px')
        self.menubar.data('Commands',self.commandsMenu())
        sp = root.splitContainer(height='100%')
        left = sp.contentPane(sizeShare=30)     
        client = sp.contentPane(sizeShare=70, gnrId='client').accordionContainer(height='100%')
  
        s=client.contentPane(label='Python Source',height='100%')
        s.button(caption='edit', action="genro.serverCall('mate',{path:'@trees.currentPath'})")
        
        source=s.contentPane(gnrId='srccont',height='100%',_class='linecode',overflow='auto')
        source.subscribe('genro.gnrjstree', event='onSelect', func = "*loadpane")
        source.subscribe('genro.gnrpytree', event='onSelect', func = "*loadpane")
        source.func('loadpane','treenode',"""
                                genro.setData('trees.currentPath', genro.getDataAttr(treenode, 'abs_path'))
                                genro.setUrlRemote(genro.srccont, 'getSourceFile', 
                                                                {'mode': 'text', 
                                                                 'linenumbers': 1, 
                                                                 'path': '@trees.currentPath'
                                                                });""")
        
                                                                
        ac = left.accordionContainer(height='100%', datasource='trees')
        tc = ac.contentPane(label='usr/local/genro').tabContainer(height='100%')
        tc.contentPane(label='instances').tree(datasource=':instances').data('',self.directoryTree('/usr/local/genro/data/instances'))
        tc.contentPane(label='sites').tree(datasource=':sites').data('', self.directoryTree('/usr/local/genro/data/sites'))
        tc.contentPane(label='packages').tree(datasource=':sites').data('', self.directoryTree('/usr/local/genro/data/sites'))
        
        
        pkg = ac.contentPane(label='Packages').tabContainer(height='100%')
        pkg.contentPane(label='Genro').tree(datasource=':packages').data('', self.directoryTree('/usr/local/genro/packages'))
        for p,v in self.package.attributes.items():
            if p.startswith('pkgLoc'):
                pkg.contentPane(label=p[7:]).tree(datasource=':%s'%p[7:]).data('', self.directoryTree(v))
        libpy = ac.contentPane(label='Genropy').tree(datasource=':libpy',gnrId='gnrpytree').data('', self.directoryTree('/sviluppo/genro/gnrpy/gnr'))
        libjs = ac.contentPane(label='Genrojs').tree(datasource=':libjs',gnrId='gnrjstree').data('', self.directoryTree('/sviluppo/genro/gnrjs/gnr'))
    
        
        
        help = ac.contentPane(label='Help').tree(datasource=':help').data('', self.directoryTree('/usr/local/genro/packages'))
    
    def commandsMenu(self):
        b=Bag()
        b.setItem('Make Package','', action="genro.serverCall('makepackage')")
        return b
    
    def directoryTree(self, path=''):
        return  DirectoryResolver(path,exclude='*.pyc')
        
    def rpc_mate(self, path=''):
        self.gnotify('fff',path)
        subprocess.call(['mate',path])
        
    def rpc_makepackage(self, path=''):
        self.gnotify('xxx','aaa')   
               
    def rpc_test(self, path=''):
        self.gnotify('xxx','aaa')
            
    def rpc_getSourceFile(self,path='',linenumbers=0):
        result=self.utils.readFile(path)
    
        if not linenumbers:
            return result
        lines=result.split('\n')
        result="<table border='0' cellspacing='0' cellpadding='0' >%s</table>"
        rows=[]
        for j,line in enumerate (lines):
            rows.append("<tr><td class='linenum'>%i</td><td class='linecode r%i'>%s</td></tr>" % (j+1,j%2,line))
        result = result  % '\n'.join(rows)
        return result

