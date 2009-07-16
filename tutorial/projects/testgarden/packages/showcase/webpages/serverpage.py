#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrwsgipage import GnrHtmlPage

page_factory = GnrHtmlPage

class GnrCustomWebPage(object):

    def main(self, name='World'):
        self.defineStyles()
        self.content(name)
        
    def defineStyles(self):
        self.body.style(""".caption{background-color:lightgray;
                                 text-align:center;
                                 color:white;
                                 font-size:8pt;
                                 height:4mm;
                                 line-height:4mm;
                                 font-weight: normal;
                                 }
                        .smallCaption{font-size:7pt;
                                  text-align:left;
                                  color:gray;
                                  text-indent:1mm;
                                  width:auto;
                                  font-weight: normal;
                                  line-height:auto;
                                  line-height:3mm;
                                  height:3mm;""")
                     
        self.body.style(""".fs_xs {font-size:7.5pt;}
                        .fs_s {font-size:11pt;}
                        .fs_m {font-size:13pt;}
                        .fs_l {font-size:18pt;}
                        .fw_b {font-weight:bold}
                        .ta_l {text-align:left;}
                        .ta_c {text-align:center;}
                        .ta_r {text-align:right;margin-right:2mm;}
                        .lh_12 {line-height:12mm;}
                        .lh_3 {line-height:3mm;}
                         """)
    def content(self,name):
        self.body.div('Hello,')
        self.body.div('%s!'%name, style='color:red;')
       
