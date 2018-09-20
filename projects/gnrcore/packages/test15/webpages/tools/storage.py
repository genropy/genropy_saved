# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_1_write(self,root,**kwargs):
        fb = root.formbuilder()
        fb.textbox(value='^.path',lbl='Path',width='40em')
        fb.simpleTextArea(value='^.content',lbl='Content')
        fb.button('Write no service',fire='.write_noservice')
        fb.dataRpc(None,self.writeContentNoService,_fired='^.write_noservice',filepath='=.path',filecontent='=.content')

        fb.button('Write with service',fire='.write_service')
        fb.dataRpc(None,self.writeContentWithService,_fired='^.write_service',filepath='=.path',filecontent='=.content')

    @public_method
    def writeContentNoService(self,filepath=None,filecontent=None):
        realpath = self.site.getStaticPath(filepath)
        with open(realpath,'w') as f:
            f.write(filecontent)
        

    @public_method
    def writeContentWithService(self,filepath=None,filecontent=None):
        storage = self.site.storage('vol:pippo') 
        """
        site:data
        vol:documenti_locali
        vol:
        storage:mybucket
        """
        with storage.open('mario','antonio.txt') as f:
            f.write(filecontent)

        @public_method
    def writeContentWithService2(self,filepath=None,filecontent=None):
        with self.site.openFile(path) as f: # path = '_site:pippo' o '_vol:mario'
            f.write(filecontent)