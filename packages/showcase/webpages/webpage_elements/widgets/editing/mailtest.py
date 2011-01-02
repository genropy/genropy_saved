#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

"""Mail demo"""

class GnrCustomWebPage(object):
    js_requires = 'ckeditor/ckeditor'

    def main(self, root, **kwargs):
        toolbar = """[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   '/',
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""
        bc = root.borderContainer()
        top = bc.contentPane(height='50%', region='top', splitter=True)
        top.ckeditor(value='^mail.body', nodeId='cked1', config_toolbar='Basic',
                     config_uiColor='#9AB8F3', toolbar=toolbar)

        center = bc.borderContainer(region='center')
        fb = center.formbuilder(cols=3)
        fb.data('mail.from', 'michele@vico10.com')
        fb.data('mail.async', False)
        fb.textBox(value='^mail.from', lbl='From:')
        fb.textBox(value='^mail.to', lbl='To:')
        fb.textBox(value='^mail.subject', lbl='Subject:')
        fb.checkBox(value='^mail.async', lbl='Async:')
        fb.button('Send', action='FIRE mail.send')
        center.dataRpc('dummy', 'sendMail', to_address='=mail.to', from_address='=mail.from', async='=mail.async',
                       subject='=mail.subject', body='=mail.body', _fired='^mail.send')

    def rpc_sendMail(self, to_address=None, from_address=None, subject=None, body=None, async=False):
        import time

        t = time.time()
        self.site.mail_handler.sendmail(to_address, subject, body, from_address=from_address,
                                        host='smtp.gmail.com', tls=True, user='michele.bertoldi@gmail.com',
                                        password='rotring', html=True, async=async)
        print time.time() - t
        