#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='public:Public'
    subscribed_tables='website.page,website.index_article'
    pageOptions=dict(openMenu=False)

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return 'Homepage articles'
         
    def main(self, rootBC, **kwargs):
        bc = rootBC.rootBorderContainer(title='Pratiche',datapath='pratiche')
        self.framePages(bc.framePane(frameCode='pages',region='top',height='50%',datapath='.pages',splitter=True))
        self.frameArticles(bc.framePane(frameCode='articles',region='center',datapath='articles',splitter=True))

    def framePages(self,frame):
        def pageStruct(struct):
            r = struct.view().rows()
            r.cell('id', hidden=True)
            r.cell('@folder.child_code', name='!!Folder',width='30%')
            r.cell('permalink', name='!!Permalink',width='70%')
            return struct
        tb=frame.top.slotToolbar('*,searchOn')
        iv = frame.includedView(struct=pageStruct,_newGrid=True,
                            onDrag= 'dragValues["page"] = dragValues.gridrow.rowset;',
                            draggable_row=True)
        iv.selectionStore(table='website.page',autoSelect=True,_onStart=True,
                          externalChanges=False,
                          where='$id IS NOT NULL')
                          
    def frameArticles(self,frame):
        tb=frame.top.slotToolbar('*,searchOn')
        def articleStruct(struct):
            r = struct.view().rows()
            r.cell('id', hidden=True)
            r.cell('_row_counter', name='!!Pos',width='5%')
            r.cell('@page_id.@folder.child_code', name='!!Folder',width='30%')
            r.cell('@page_id.permalink', name='!!Permalink',width='70%')
            return struct
            
        iv = frame.includedView(struct=articleStruct,autoSelect=True,_newGrid=True,
                                selfDragRows=True,
                                onDrop_page='FIRE .dropped_page={"data":data,"page_id":this.widget.rowIdByIndex(dropInfo.row)};')
        iv.selectionStore(table='website.index_article',_onStart=True,externalChanges=True,order_by='$_row_counter',_fired='^.reload')        
        iv.dataController("""var pkeys = [];
                             var data=drop_dict.data;
                             dojo.forEach(data,function(n){pkeys.push(n._pkey);});
                             genro.publish('dragged_pages',{pkeys:pkeys});""",
                             drop_dict="^.dropped_page")
        iv.dataRpc('dummy','addArticle',subscribe_dragged_pages=True)
        iv.dataRpc('dummy','onViewCounterChange',subscribe_articles_grid_counterChanges=True)
        #frame.dataController("FIRE .reload;",subscribe_dbevent_studio_pr_riga=True)
        #
        

                                          
    def rpc_addArticle(self,pkeys=None,data=None,**kwargs):
        tblobj = self.db.table('website.index_article')
        for pkey in pkeys:
            tblobj.insertOrUpdate(dict(page_id=pkey))
        self.db.commit()

    def rpc_onViewCounterChange(self,table=None,changes=None,**kwargs):
        updaterDict = dict( [ (d['_pkey'],d['new']) for d in changes] )
        pkeys = updaterDict.keys()
        def cb(r):
            r['_row_counter'] = updaterDict[r['id']]
        self.db.table(table).batchUpdate(cb, where='$id IN:pkeys', pkeys=pkeys)
        self.db.commit()
