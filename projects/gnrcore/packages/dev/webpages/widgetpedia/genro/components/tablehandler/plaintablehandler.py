#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer,th/th:TableHandler"
    def main(self,root,**kwargs):
        root.plainTableHandler(table='glbl.provincia')
