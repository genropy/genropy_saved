#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/source_viewer/source_viewer:SourceViewer,th/th:TableHandler"
    def main(self,root,**kwargs):
        #root.div('hello')
        bc = root.borderContainer(datapath='main',height='100%')
        bc.contentPane(region='top',height='40px',background='red')
        center = bc.contentPane(region='center')
        center.plainTableHandler(table='glbl.provincia',
                               datapath='main',
                               view_store__onBuilt=100)
        print 'aaa'
