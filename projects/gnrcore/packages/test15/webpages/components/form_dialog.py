# -*- coding: UTF-8 -*-

# form_dialog.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""FormDialog"""

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull,foundation/dialogs'
    
    def test_0_formDialog(self, pane):
        self.askAuthcodeDlg(pane)
        pane.button('test_0', action='FIRE #askAuthcode_dlg.open;')
        
    def askAuthcodeDlg(self, bc, onConfirmed='', request_txt=''):
        def cb_center(parentBC, **kwargs):
            dlg_body = parentBC.contentPane(margin='8px', **kwargs)
            dlg_body.div(request_txt)
            fb = dlg_body.formbuilder(cols=1)
            fb.textbox(lbl='Insert your authorization code',
                       value='^.authcode', width='8em',
                       validate_notnull=True,
                       validate_notnull_error='Insert code',
                       validate_remote='validateAuthCode',
                       validate_remote_error='Wrong or already used auth code.'
                       )
                       
        dlg = self.formDialog(bc,
                              formId='askAuthcode',
                              title='Authorization required',
                              height='150px', width='350px',
                              datapath='aux.auth_dlg',
                              cb_center=cb_center, loadsync=True)
        dlg.dataController("""SET form.record.$authcode = GET .data.authcode;
                              FIRE .saved;
                              %s""" % onConfirmed,
                           nodeId='askAuthcode_saver')
                           
        dlg.dataController("""SET .data.authcode = null;""",
                           nodeId='askAuthcode_loader')
                           
    def rpc_validateAuthCode(self, value=None, **kwargs):
        if value != 'pippo':
            return False
        else:
            return True