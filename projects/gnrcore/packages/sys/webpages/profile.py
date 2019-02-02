#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from builtins import object
import pstats
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method



class GnrCustomWebPage(object):
    
    def windowTitle(self):
        return '!!Profile'

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main')
        left = bc.contentPane(region='left',width='250px',splitter=True,background='#f3f3f3')
        left.tree(storepath='.modules', inspect='shift',isTree=False,selectedPath='.selectedPath')
              
              
              
      #  left.quickTree(value='^.modules',border='1px solid silver',height='500px')
        left.dataRpc('.modules',self.getModules,_onStart=True)
        center=bc.contentPane(region='center')
       #center.quickGrid(value='^.calls',border='1px solid silver')
       #center.dataRpc('.calls',self.getCalls,selected_module='^.selected_module')
       #
    def convertModuleName(self,k):
        p=k[0].replace('.py','')
        p=p.replace('.','_')
        p=p.replace('/','.')
        p='%s.%s'%(p,k[2])
        return p
        
    @public_method
    def getModules(self):
        s=pstats.Stats(self.site.getStaticPath('site:','site_profiler.log'))
        result=Bag()
        for k,v in list(s.stats.items()):
            modulename=k[0]
            p=self.convertModuleName(k)
            c=v[4]
            cbag=Bag()
            for ck,cv in list(c.items()):
                cp=self.convertModuleName(ck)
                cp=cp.replace('.','_')
                cbag[cp]=Bag(dict(modulename=ck[0],methodName=ck[2],linenumber=ck[1],ncalls=cv[0],
                    nscalls=cv[1],tottime=cv[2],prtime=cv[3]))
            result.setItem(p,Bag(dict(modulename=k[0],methodName=k[2],linenumber=k[1],ncalls=v[0],
                    nscalls=v[1],tottime=v[2],prtime=v[3],callers=cbag)))
        for n in result: 
            while len(n.value)==1:
                childnode=n.value.getNode('#0')
                n.label=childnode.label
                n.value=childnode.value
        return result
        
    @public_method
    def getCalls(self,selected_module=None):
        s=pstats.Stats(self.site.getStaticPath('site:','site_profiler.log'))
        result=Bag()
        for k,v in list(s.stats.items()):
            module=k[0].replace('.py','')
            module=module.replace('.','_')
            if module != selected_module:
                continue
            result.setItem(k[2],Bag(dict(modulename=k[0],methodName=k[2],linenumber=k[1],ncalls=v[0],
                    nscalls=v[1],tottime=v[2],prtime=v[3],callers_count=len(v[4]))))
        return result


        
        

  