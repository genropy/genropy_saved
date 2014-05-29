# -*- coding: UTF-8 -*-
            
class GnrCustomWebPage(object):
    py_requires = 'source_viewer'
    def main(self,root,**kwargs):
        root.div('Hello world')    
