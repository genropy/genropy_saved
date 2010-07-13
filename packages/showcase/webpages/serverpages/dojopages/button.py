#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory

class GnrCustomWebPage(object):
    dojoversion='13'
    theme='soria'

    def main_(self, body, name='World'):
        body.script("""dojo.addOnLoad(function(){alert("PPPP")};)""")
        bc=body.borderContainer(height='500px',width='600px',margin='10px',background_color='red')
        bc.contentPane(region='top',height='5ex',splitter='true',background_color='lime')
        bc.contentPane(region='left',width='15em',splitter='true',background_color='gray')
        tc=bc.tabContainer(region='center')
        c1=tc.contentPane(title='abcd')
        c2=tc.contentPane(title='uuuu')
        c3=tc.contentPane(title='kkkk')
        c1.div('Hello,')
        c1.div('%s!'%name, style='color:red;')
        c1.button(label='I am a button: please click me!',onClick='alert("I was clicked")')
        c2.div('buoooo,')
        c2.div('%s!'%name, style='color:red;')
        c2.button(label='I am a button: you cannot click me!',onClick='alert("I cannot be clicked")')
        c3.div('treeeee,')
        c3.div('%s!'%name, style='color:red;')
        c3.button(label='I am a button: please NOT click me!',onClick='alert("YOU dare")')