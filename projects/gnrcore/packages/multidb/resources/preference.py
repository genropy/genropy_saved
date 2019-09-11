#!/usr/bin/env python
# -*- coding: utf-8 -*-


from gnr.web.gnrbaseclasses import BaseComponent

class AppPref(BaseComponent):
    def permission_multidb(self, **kwargs):
        return 'admin'

    def prefpane_multidb(self, parent, **kwargs):
        pane = parent.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.checkbox(value='^.multidb_switch',html_label=True,lbl='!!Multidb switch')
        fb.textbox(value='^.multidb_switch_tag',lbl='!!Multidb switch tag',hidden='^.multidb_switch?=!#v')
