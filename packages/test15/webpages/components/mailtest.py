# -*- coding: UTF-8 -*-

# testcomponent.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""IncludedView test page"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/testhandler:TestHandlerFull,foundation/includedview:IncludedView'
    js_requires='ckeditor/ckeditor'
    
    def test_1_mailtest(self,pane):
        fb=pane.formbuilder(cols=3)
        fb.data('mail.from','michele@vico10.com')
        fb.data('mail.to','michele@vico10.com')
        fb.data('mail.async',False)
        fb.data('mail.content','Prova')
        fb.data('mail.subject','Prova')
        fb.textBox(value='^mail.content', lbl='Content:')
        fb.textBox(value='^mail.from', lbl='From:')
        fb.textBox(value='^mail.to', lbl='To:')
        fb.textBox(value='^mail.subject', lbl='Subject:')
        fb.checkBox(value='^mail.async', lbl='Async:')
        fb.button('Send', action='FIRE mail.send')
        fb.dataRpc('dummy','sendMail', to_address='=mail.to', from_address='=mail.from',async='=mail.async', subject='=mail.subject', body='=mail.content', _fired='^mail.send')

    def rpc_sendMail(self, to_address=None, from_address=None, subject=None, body=None, async=False):
        import time
        t=time.time()
        self.site.mail_handler.sendmail(to_address, subject, body,from_address=from_address,attachments=[__file__],
                            host='smtp.gmail.com',tls=True, user='michele.bertoldi@gmail.com', password='rotring', async=async)
        print time.time()-t
    



