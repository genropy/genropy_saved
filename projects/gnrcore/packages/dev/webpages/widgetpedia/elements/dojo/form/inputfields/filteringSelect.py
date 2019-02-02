#!/usr/bin/python

from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer"
    def main(self,root,**kwargs):
        fb = root.formbuilder(cols=1,datapath='main',margin='10px')
        fb.filteringselect(value='^.classifica',lbl='Classifica', values='1:Primo,2:Secondo,3:Terzo,4:Quarto')
        fb.filteringselect(value='^.voto',lbl='Voto', values='A,B,C,D,E')