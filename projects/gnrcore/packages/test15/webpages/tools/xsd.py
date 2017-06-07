#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  index.py


""" index.py """
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import DirectoryResolver
import os

PATH = '/Users/fporcari/sviluppo/xbrl2016/2016-11-14/2016-11-14'
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires = """public:Public"""

    def main(self, root,**kwargs):
        bc = root.rootBorderContainer(datapath='main',design='sidebar',title='!!XML and XSD') 
        left = bc.tabContainer(margin='2px',splitter=True,region='center')
        self.fileTreeTab(left,'xsd')
        self.fileTreeTab(left,'xml')

    def fileTreeTab(self,tc,mode):
        pane = tc.contentPane(title=mode,datapath='.tree_%s' %mode)
        resolver= DirectoryResolver(PATH,include='*.%s' %mode,ext=mode)
        pane.data('.data', resolver())
        pane.bagEditor(storepath='.data' ,hideValues=True, 
                  font_family='courier',
                  selectedLabelClass='selectedTreeNode',
                  selected_abs_path='.abs_path',
                  labelAttribute='name',
                  searchOn=True,
                  export=True,
                  autoCollapse=True)

        #
        #left.dataRpc('.content',self.getContent, 
        #               filepath='^.abs_path',
        #               _delay=200)
        #
        #center=bc.contentPane(region='center')
        #center.pre(value='^.content',font_size='.8em')
        
    @public_method    
    def getContent(self,filepath=None,**kwargs):
        filepath=os.path.join(PATH,filepath)
        with open(filepath,'r') as f:
            data=f.read()
        return data