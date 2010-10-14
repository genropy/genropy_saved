# -*- coding: UTF-8 -*-

# fileInput.py
# Created by Niso on 2010-10-14.
# Copyright (c) 2010 Softwell. All rights reserved.

"""file Input"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """An explanation of "genro.dlg.upload" """
        pane.div("""We show you the "genro.dlg.upload": its first parameter is the name of the dialogue window (you
                    can see this window by clicking the button "Upload"; in this example the name is "Upload something"),
                    the second parameter is the name of the Rpc method you're calling (#NISO: is there a standard Rpc or
                    the programmer have to use a Rpc created by himself?), the third parameter is the folder for the
                    data uploaded.""",
                    font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test1')
        fb.button('Upload',action='genro.dlg.upload("Upload something","importMethod","aux.resultPath")')
        fb.simpleTextarea(value='^aux.resultPath',width='30em',height='20em',colspan=2,lbl='text uploaded')
        
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