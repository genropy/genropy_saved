# -*- coding: utf-8 -*-
from builtins import str
from builtins import object
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag
from gnr.lib.services.storage import StorageResolver

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/storagetree:StorageTree"


    def test_1_write(self,root,**kwargs):
        fb = root.formbuilder()
        fb.textbox(value='^.path',lbl='Path',width='40em')
        fb.simpleTextArea(value='^.content',lbl='Content')
        fb.button('Write',fire='.write')
        fb.dataRpc(None,self.writeContent,_fired='^.write',filepath='=.path',filecontent='=.content')

        fb.textbox(value='^.url',lbl='Url',width='40em', readOnly=True)
        fb.dataRpc('.url',self.url,filepath='^.path')
        root.data('.store',StorageResolver(self.site.storageNode('pkg:test15'),cacheTime=10,
                            include='*.txt', exclude='_*,.*',dropext=True,readOnly=False,_page=self)()
                            )
        root.tree(storepath='.store', hideValues=True, inspect='shift', draggable=True, dragClass='draggedItem')

        
    @public_method
    def writeContent(self,filepath=None,filecontent=None):
        storageNode = self.site.storage(filepath)
        with storageNode.open(mode='wb') as f:
            f.write(str(filecontent))

    @public_method
    def url(self,filepath=None,filecontent=None, **kwargs):
        storageNode = self.site.storage(filepath)
        return storageNode.url(**kwargs)
        

    def test_2_copy(self,root,**kwargs):
        bc = root.borderContainer(_anchor=True,height='400px')
        bc.storageTreeFrame(frameCode='localStorage',storagepath='pkg:test15/lib',
                                border='1px solid silver',margin='2px',rounded=4,
                                region='center',preview_region='right',
                                store__onBuilt=True,
                                store__reloadstore='^.reloadstore',
                                tree_selected_abs_path='#ANCHOR.sourcepath',
                                preview_border_left='1px solid silver',preview_width='50%')

        fb = bc.contentPane(region='bottom').formbuilder()

        fb.textbox(value='^#ANCHOR.sourcepath',lbl='Source')
        fb.textbox(value='^#ANCHOR.destpath',lbl='Dest')
        fb.button('Copy',fire='.copy')
        fb.dataRpc(None,self.copyFileTest,sourcepath='=#ANCHOR.sourcepath',
                        destpath='=#ANCHOR.destpath',_fired='^.copy',_onResult='FIRE .reloadstore',
                        _lockScreen=True)
    
    @public_method
    def copyFileTest(self,sourcepath=None,destpath=None,**kwargs):
        if not destpath:
            return
        source = self.site.storageNode(sourcepath)
        source.copy(self.site.storageNode(destpath))
