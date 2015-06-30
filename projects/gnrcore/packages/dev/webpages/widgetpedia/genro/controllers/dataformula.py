#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"
    def main(self,root,**kwargs):
        root.div("dataFormula")
