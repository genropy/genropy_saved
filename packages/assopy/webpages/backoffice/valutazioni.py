#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.talk'
    py_requires='basecomponent:Public'
    def pageAuthTags(self, method=None, **kwargs):
        pass

        
    def main(self, root, **kwargs):
        lc,top = self.publicRoot(root)
        top.div('!!Valutazione Talk')
        mainpage = lc.stackContainer(layoutAlign='client', selected='^selectedPage')
        sc=mainpage.splitContainer(height='100%',orientation='vertical')
        listpane=sc.contentPane(sizeShare=30,_class='talklist')
        self.listaTalk(listpane)
        client=sc.contentPane(sizeShare=70)
        self.formValutazione(client,datapath='form.record',disabled='^form.locked')
                
    def listaTalk(self, pane):
        struct = self.newGridStruct()
        r=struct.child('view').child('rows',classes='talklist',
                                      cellClasses='talklist_cells',
                                      headerClasses='talklist_headers')
        r.fields("""@oratore_id.@anagrafica_id.ragione_sociale/Oratore:12,
                    titolo/Titolo:35,durata/D:3,@track_id.codice/Track:3""")
        pane.data('grid.struct', struct)
        pane.dataFormula('columns', 
                'gnr.columnsFromStruct(struct);',
                         struct='^grid.struct',_init=True)
        method, kwargs = self.recordGetter()
        pane.dataScript('list.selectedId','return genro.wdgById("maingrid").rowIdByIndex(idx)' ,
                             idx='^list.selectedIndex',_if='idx>=0', _else="if (idx==-1){return '*newrecord*'}")
        pane.dataRecord('form.record',self.maintable,'^list.selectedId', reload='^form.reload', method = method,
                         _onResult='this.dataLoggerReset("form.record", "form.modified", "form.changes");FIRE recordLoaded=true;', **kwargs)
        pane.dataSelection('grid.data','assopy.talk',columns='^columns',_init=True)
        grid=pane.staticGrid(storepath='grid.data',structpath='grid.struct',nodeId='maingrid',
                             selectedIndex='list.selectedIndex',
                             autoWidth=True,elasticView=0)
        
    def formValutazione(self,pane,datapath,disabled):
        fb=pane.formbuilder(cols=3,datapath=datapath)
        fb.field('assopy.talk.titolo',lbl='Titolo')           

                                   

    

    
        
    def iframe(self,pane):
        pass

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
