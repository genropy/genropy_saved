# -*- coding: UTF-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:ChunkEditor"

    def test_1_embed(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='left').tree(storepath='.store',selected_rel_path='.rel_path').directoryStore(rootpath='/Users/fporcari/sviluppo/softwell/progetti/genromed/sites/moscati_test/data/attatchment')
        
        bc.dataController('SET .url = base_path+"/"+rel_path',rel_path='^.rel_path',base_path=self.site.getStaticUrl('site:data/attatchment'),_if='rel_path')
        bc.contentPane(region='center').embed(src='/_site/data/attatchment/P1030352.jpg',height='100%',width='100%')

    def test_2_embed(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='left').tree(storepath='.store',selected_rel_path='.rel_path').directoryStore(rootpath='/Users/fporcari/sviluppo/softwell/progetti/genromed/sites/moscati_test/data/attatchment')
        
        bc.dataController('SET .url = base_path+"/"+rel_path',rel_path='^.rel_path',base_path=self.site.getStaticUrl('site:data/attatchment'),_if='rel_path')
        bc.contentPane(region='center').embed(src='/_site/data/attatchment/fatt.pdf',height='100%',width='100%')
