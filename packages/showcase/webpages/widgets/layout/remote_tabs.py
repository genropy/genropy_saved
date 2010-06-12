#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(height="100%", width="100%", margin="10px")
        fb = bc.contentPane(region="top", height="3em").formbuilder(cols=2, border_spacing='4px')
        bc.data("numtabs",0)
        fb.numberspinner(value="^numtabs", lbl="Number of tabs", width="10ex")
        fb.div('Move focus out of the textbox to update tabs. There is a bug when you set the number of tabs to one.')
        
        tc = bc.tabContainer(region="center")
        tc.remote('tabs', numtabs="^numtabs")
    
    def remote_tabs(self, tc, numtabs=None):
        if numtabs:
            for i in xrange(numtabs):
                tab = tc.contentPane(title="Tab #%d" % i, margin="40px")
                tab.div('This is tab #%d' % i)