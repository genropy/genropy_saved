#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Standard table showcase """

from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import RecordNotExistingError


class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self, root, **kwargs):
        box = root.div('press me',connect_onclick='FIRE aux.showTooltipDialog')
        box = root.div('press me now',connect_onclick='genro.wdgById("myDialog").show()')

        dlgBC = self.hiddenTooltipDialog(root, dlgId='dlgProdChar', 
                                        close_action='FIRE aux_job.charChanged',
                                        title="!!showDialog",
                                        width="27em",height="15ex",
                                        fired='^aux.showTooltipDialog')
        dlgPane = dlgBC.contentPane(region='center',_class='pbl_roundedGroup',margin='2px',padding='5px')                                     
        fb = dlgPane.formbuilder(cols=1,border_spacing='6px',margin_left='1em',datapath='dlg.form')
        fb.textbox(value='^.a',lbl='Foo')
        fb.textbox(value='^.b',lbl='Spam')
        
        dialog = root.dialog(nodeId='myDialog')
        dialogBc = dialog.borderContainer(height='300px',width='500px')
        dialogPane = dialogBc.contentPane(region='center')
        dialogPane.div('press me again',connect_onclick='FIRE aux.showTooltipDialog2')
        dialogPane.div('press me and see this',connect_onclick='genro.wdgById("myDialog2").show()')


        dialog2 = root.dialog(nodeId='myDialog2')
        dialogBc2 = dialog2.borderContainer(height='300px',width='500px')
        dialogPane2 = dialogBc2.contentPane(region='center')
        fb3 = dialogPane2.formbuilder(cols=1,border_spacing='6px',margin_left='1em',datapath='dlg.form')
        fb3.textbox(value='^.a',lbl='Foo',_autoselect=False)
        fb3.textbox(value='^.b',lbl='Spam')
        
        dlgBC2 = self.hiddenTooltipDialog(root, dlgId='dlgProdChar', 
                                        close_action='FIRE aux_job.charChanged',
                                        title="!!showDialog",
                                        width="27em",height="15ex",
                                        fired='^aux.showTooltipDialog2')
        dlgPane2 = dlgBC2.contentPane(region='center',_class='pbl_roundedGroup',margin='2px',padding='5px')                                     
        fb2 = dlgPane2.formbuilder(cols=1,border_spacing='6px',margin_left='1em',datapath='dlg.form')
        fb2.textbox(value='^.a',lbl='Foo',_autoselect=False)
        fb2.textbox(value='^.b',lbl='Spam')
        

