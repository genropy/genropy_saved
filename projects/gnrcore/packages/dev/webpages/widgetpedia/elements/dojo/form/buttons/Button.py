#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"
    def main(self,root,**kwargs):
        fb = root.formbuilder(cols=1,datapath='main',margin='10px')
        fb.button('CIAO', action='alert("ciao")', hidden='^.hidden')
        fb.button('Hide CIAO',
                  action='SET .hidden=true')
        fb.button('SHOW CIAO',
                  action='SET .hidden=false')
