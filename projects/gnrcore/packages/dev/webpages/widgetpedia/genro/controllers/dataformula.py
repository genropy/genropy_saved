#!/usr/bin/python

from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"
    def main(self,root,**kwargs):
        root.div("dataFormula")
