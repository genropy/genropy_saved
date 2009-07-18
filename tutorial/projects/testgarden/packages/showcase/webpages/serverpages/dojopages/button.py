#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory


class GnrCustomWebPage(object):
    dojoversion='13'
    theme='soria'
    def main(self, body, name='World'):
        body.script("""dojo.require("dijit.form.Button");""")
        body.div('Hello,')
        body.div('%s!'%name, style='color:red;')
        body.button(label='I am a button: please click me!',dojoType='dijit.form.Button',
                   id="mybutton",onClick='alert("I was clicked")')
