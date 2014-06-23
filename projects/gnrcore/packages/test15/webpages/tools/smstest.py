# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    def test_1_smstest(self, pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.sms_from',lbl='From',placeholder=self.site.config['services.smsmobyt?sender'])
        fb.textbox(value='^.sms_to',lbl='To')

        fb.simpleTextarea(value='^.sms_text',lbl='Text')
        fb.button('Run',fire='.run')
        fb.dataRpc('dummy',self.sendsms,sms_text='=.sms_text',sms_from='=.sms_from',sms_to='=.sms_to',_fired='^.run')

    @public_method
    def sendsms(self,sms_text=None,sms_from=None,sms_to=None):
        smsservice = self.site.getService('sms')
        assert smsservice,'set in siteconfig the service smsmobyt'
        result = smsservice.sendsms(receiver=sms_to,sender=sms_from,data=sms_text)
        print result