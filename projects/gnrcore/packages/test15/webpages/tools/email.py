# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

from gnr.core.gnrdecorator import public_method
import smtplib
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    def test_1_email(self, pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px', width='100%', fld_width='100%',
                                                tdl_width='10em')
        fb.div(lbl='Mail Settings', colspan=2, lbl_font_style='italic', lbl_margin_top='1em', margin_top='1em',
               lbl_color='#7e5849')
        fb.textbox(value='^.smtp_host', lbl='SMTP Host', dtype='T', colspan=1)
        fb.textbox(value='^.from_address', lbl='From address', dtype='T', colspan=1)
        fb.textbox(value='^.user', lbl='Username', dtype='T', colspan=1)
        fb.textbox(value='^.password', lbl='Password', dtype='T', colspan=1, type='password')
        fb.textbox(value='^.port', lbl='Port', dtype='T', colspan=1)
        fb.checkbox(value='^.tls', lbl='TLS', dtype='B', colspan=1)
        fb.checkbox(value='^.ssl', lbl='SSL', dtype='B', colspan=1)


        fb.simpleTextarea(value='^.sms_text',lbl='Text')
        fb.button('Run',fire='.run')
        fb.dataRpc('dummy',self.send_email,sms_text='=.sms_text',sms_from='=.sms_from',sms_to='=.sms_to',_fired='^.run')

    @public_method
    def send_email(self,message=None,sms_from=None,sms_to=None):
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            print "Successfully sent email"
        except Exception:
            print "Error: unable to send email"