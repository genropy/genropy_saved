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
        fb.dataRpc(None,self.writeContentNoService,_fired='^.write',filepath='=.path',filecontent='=.content')

    @public_method
    def writeContentNoService(self,filepath=None,filecontent=None):
        realpath = self.site.getStaticPath(filepath)
        with open(realpath,'w') as f:
            f.write(filecontent)
        