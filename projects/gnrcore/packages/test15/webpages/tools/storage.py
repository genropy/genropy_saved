# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_1_write(self,root,**kwargs):
        fb = root.formbuilder()
        fb.textbox(value='^.path',lbl='Path',width='40em')
        fb.simpleTextArea(value='^.content',lbl='Content')
        fb.button('Write',fire='.write')
        fb.dataRpc(None,self.writeContent,_fired='^.write',filepath='=.path',filecontent='=.content')

        fb.textbox(value='^.url',lbl='Url',width='40em', readOnly=True)
        fb.dataRpc('.url',self.url,filepath='^.path')

    @public_method
    def writeContent(self,filepath=None,filecontent=None):
        storageNode = self.site.storage(filepath)
        with storageNode.open(mode='wb') as f:
            f.write(str(filecontent))

    @public_method
    def url(self,filepath=None,filecontent=None):
        storageNode = self.site.storage(filepath)
        print storageNode
        return storageNode.url
        