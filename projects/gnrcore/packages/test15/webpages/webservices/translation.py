# -*- coding: utf-8 -*-
# 

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_ftplist(self, pane):
        fb = pane.formbuilder()
        fb.textbox(value='^.it',lbl='Italiano')
        fb.textbox(value='^.lang',lbl='Language')
        fb.div('^.translation',lbl='Translation')
        pane.button('Translate',fire='.run')
        pane.dataRpc('.translation',self.doTranslation,_fired='^.run',it='=.it',lang='=.lang')

    @public_method
    def doTranslation(self,it=None,lang=None):
        return self.getService('translation').translate(what=it,from_language='it',to_language=lang)
