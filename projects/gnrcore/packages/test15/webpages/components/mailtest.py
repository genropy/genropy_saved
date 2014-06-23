# -*- coding: UTF-8 -*-

# mailtest.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Mail test page"""

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/testhandler:TestHandlerFull,foundation/includedview:IncludedView'
    js_requires='ckeditor/ckeditor'
    
    def test_1_mailtest(self,pane):
        fb=pane.formbuilder(cols=3)
        fb.data('mail.from','test@genropy.net')
        fb.data('mail.to','test@genropy.net')
        fb.data('mail.async',False)
        fb.data('mail.content','Prova')
        fb.data('mail.subject','Prova')
        fb.textBox(value='^mail.content', lbl='Content:')
        fb.textBox(value='^mail.from', lbl='From:')
        fb.textBox(value='^mail.to', lbl='To:')
        fb.textBox(value='^mail.subject', lbl='Subject:')
        
        fb.textBox(value='^mail.host', lbl='Smtp Host:')
        fb.textBox(value='^mail.user', lbl='User:')
        fb.textBox(value='^mail.password', lbl='Password:')
        fb.checkBox(value='^mail.tls', lbl='Tls:')
        fb.checkBox(value='^mail.async', lbl='Async:')
        
        fb.button('Send', action='FIRE mail.send')
        fb.dataRpc('dummy','sendMail',to_address='=mail.to',from_address='=mail.from',async='=mail.async',
                    subject='=mail.subject', body='=mail.content', _fired='^mail.send', user='=mail.user',
                    password='=mail.password', host='=mail.host', tls='=mail.tls')
    
    def cb(self):
        print 'callback'

    def rpc_sendMail(self,to_address=None,from_address=None,subject=None,body=None,async=False,host=None,user=None, password=None, tls=None):
        import time
        t=time.time()
        print host, user, password, async, tls
        self.site.mail_handler.sendmail(to_address,subject,body,from_address=from_address,attachments=[__file__],
                                        smtp_host=host,tls=tls,user=user, port=587,
                                        password=password,async=async, cb=self.cb)
        print 'rpc end'
        print time.time()-t