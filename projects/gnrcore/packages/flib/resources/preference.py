# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------

from builtins import object
class AppPref(object):
    def prefpane_flib(self, tc, **kwargs):
        pane = tc.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1, border_spacing='5px')
        fb.textbox(value='^.basefolder', lbl='!!Base url')


class UserPref(object):
    def prefpane_flib(self, tc, **kwargs):
        pane = tc.contentPane(**kwargs)



