# -*- coding: utf-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def pageAuthTags(self, **kwargs):
        return 'user'

    def windowTitle(self):
        return '!!Test pref'

    def test_01_single_value(self, pane, **kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.prefpkg',lbl='Pref pkg')
        fb.textbox(value='^.prefpath',lbl='Pref path')
        fb.button('Search',fire='.search')
        fb.div('^.result',lbl='Result')
        fb.dataRpc('.result',self.getAppPreference,pkg='=.prefpkg',prefpath='=.prefpath',_fired='^.search')