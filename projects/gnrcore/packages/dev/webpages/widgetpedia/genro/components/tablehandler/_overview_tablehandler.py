#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer,th/th:TableHandler"
    def main(self,root,**kwargs):
        #root.div('hello')
        bc = root.borderContainer(datapath='main',height='100%')
        bc.contentPane(region='top',height='40px',background='gray')
        center = bc.contentPane(region='center')
        center.inlineTableHandler(table='glbl.regione',
                                 viewResource='ViewEditable',
                               datapath='main',
                               view_store__onBuilt=1000)
