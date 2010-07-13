#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.sql.gnrsql_exceptions import RecordNotExistingError

class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self, root, **kwargs):
        box = root.div('press me',connect_onclick='FIRE aux.showDialog')
        dlgBC = self.hiddenTooltipDialog(root, dlgId='dlgProdChar', 
                                        close_action='FIRE aux_job.charChanged',
                                        title="!!showDialog",
                                        width="27em",height="15ex",
                                        fired='^aux_job.showDialog')
        dlgPane = dlgBC.contentPane(region='center',_class='pbl_roundedGroup',margin='2px',padding='5px')                                     
        fb = dlgPane.formbuilder(border_spacing='6px',margin_left='1em',datapath='dlg.form')
        fb.textbox(value='^.a',lbl='Foo')
        fb.textbox(value='^.b',lbl='Spam')