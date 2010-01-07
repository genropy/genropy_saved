#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        lc=root.LayoutContainer(height='100%',gnrId='piero')
        topbar=lc.contentPane(layoutAlign='top',background_color='gray',height='1.3em').span('topbar')
        bottombar=lc.contentPane(layoutAlign='bottom',background_color='pink',height='1.3em').span('topbar')
        leftcolumn=lc.contentPane(layoutAlign='left',background_color='silver',width='6em')
        client=lc.contentPane(layoutAlign='client')
        tabcontainer=client.TabContainer(height='100%')
        one=tabcontainer.contentPane(title='Dojo book')
        one.iframe(src="http://dojotoolkit.org/book/dojo-book-0-9-0",border='0px',height='100%',width='100%')
        two=tabcontainer.contentPane(title='Dojo Forum',background_color='yellow')
        two.iframe(src="http://dojotoolkit.org/forum",border='0px',height='100%',width='100%')
        three=tabcontainer.contentPane(title='Three')
        accinner=three.accordionContainer(height='100%')
        oneAcc=accinner.accordionPane(title="One Accordion")
        twoAcc=accinner.accordionPane(title="Two Accordion")
        tb2=oneAcc.TabContainer(height='100%')
        tb2.contentPane(title='One kkkk',background_color='pink').iframe(src="http://www.apple.com",border='0px',height='100%',width='100%')
        tb2.contentPane(title='Wtr kkkk',background_color='lime').iframe(src="http://python.org",border='0px',height='100%',width='100%')
        spl=twoAcc.splitContainer(height='100%')
        spl.contentPane(sizeShare=30,background_color='yellow')
        tt=spl.contentPane(sizeShare=70,background_color='smoke')
        az=tt.accordionContainer()
        az.accordionPane(title="Ginger").button('I am ginger')
        az.accordionPane(title="Fred").button('I am fred')
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
