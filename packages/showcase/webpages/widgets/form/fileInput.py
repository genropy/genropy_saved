#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(datapath='form',cols=2)
        fb.button(label='Upload',
                    action='genro.dlg.upload("Upload something","importMethod","aux.resultPath")')
        fb.span('--- upload a text file (.txt) ---')
        fb.simpleTextarea(label='text uploaded',value='^aux.resultPath',width='30em',height='40em',colspan=2)
        
    def rpc_importMethod(self,**kwargs):
        """What I do with my file on server"""
        try:
            f = kwargs['fileHandle'].file
            text = f.read()
            result = """Content-Type: text/html
                <html>
                    <head>
                    </head>
                    <body>
                        <textarea>%s</textarea>
                    </body>
                </html>
                """ % text
        except Exception, e:
            result = """Content-Type: text/html
                <html>
                    <head>
                    </head>
                    <body>
                        <textarea>It doesn't work</textarea>
                    </body>
                </html>
            """
        return result