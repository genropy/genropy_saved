# -*- coding: UTF-8 -*-
from gnr.core.gnrbag import DirectoryResolver
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/framegrid:FrameGrid'
    auth_main = '_DEV_'

    def main(self,root,**kwargs):
        frame = root.framePane(datapath='main')
        bc = frame.center.borderContainer()
        bc.contentPane(region='left',width='300px')
        left = bc.contentPane(overflow='auto',region='left',width='300px') 
        left.tree(storepath='.efs')
        left.data('.efs.root',DirectoryResolver(self.site.getStaticPath('vol:efs'),name='EFS')())


    @public_method
    def efsResolver(self,pod=None,**kwargs):
        return 
