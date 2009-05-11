#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Examples & Tutorials """

#from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag, DirectoryResolver
import os

# ----- GnrWebPage subclass -----

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('currentUrl', self.package.attributes.get('startpage'))
        root.dataScript('dummy',"""var timerFunc=function(){
                                      genro.rpc.remoteCall('getUrl', {},
                                       null, 'GET', true,
                                       function(r){
                                          var newUrl=r.getValue();
                                          if(newUrl!=genro.lastUrl){
                                             genro.myframe.src = newUrl;
                                             genro.lastUrl=newUrl;
                                          }}
                                       );}
                                  setInterval(timerFunc,3000)""",_init=True)        
        root.iframe(border='0px', width='100%', height='100%',src='=currentUrl',gnrId='myframe')
        
    def rpc_getUrl(self,**kwargs):
        start=self.package.attributes.get('startpage')        
        filepath=os.path.join(self.siteFolder, 'data', 'common','selectedURL.txt')
        f = file(filepath)
        relpath = f.read()
        f.close()
        return relpath

#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
