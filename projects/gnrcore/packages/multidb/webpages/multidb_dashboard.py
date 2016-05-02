#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#  Created by Francesco Porcari
#
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires = 'public:Public,th/th:TableHandler,th/th_dynamic:DynamicTableHandler'
    authTags='superadmin'
    pageOptions={'openMenu':False,'enableZoom':False}


    def main(self, root,**kwargs):
        frame = root.rootContentPane(datapath='main',design='sidebar',title='!!Multidb dasboard')   
        frame = frame.center.framePane()      
        bc = frame.center.borderContainer()
        bar = frame.top.slotBar('2,fbselects,*')
        fb = bar.fbselects.formbuilder(cols=4,border_spacing='2px')
        fb.filteringSelect(value='^.dbstore',lbl='!!Db Store',values=','.join(sorted(self.db.stores_handler.dbstores.keys())))
        fb.remoteSelect(value='^.sync_table',lbl='!!Table',selected_multidb='.multidb_mode',
                        method=self.getSyncTables,
                        auxColumns='multidb',hasDownArrow=True)
        fb.dataRpc('dummy',self.setSyncInfoInStore,insync_table='^.sync_table',insync_store='^.dbstore',
                    _if='insync_table&&insync_store',_onResult="FIRE main.load_th")

        left = bc.contentPane(region='left',width='50%',margin='2px')
        center = bc.contentPane(region='center',margin='2px')
        frame.dataController("""if(_reason=='child' && _node.label!='_protectionStatus'){
                var mainstruct_copy = mainstruct.deepCopy();
                mainstruct_copy.popNode('#0.#0._protectionStatus');
                SET main.dbext.th.view.grid.struct = mainstruct_copy;
            }""",
            mainstruct='^main.dbroot.th.view.grid.struct',_delay=1)

        frame.dataController("""SET main.dbext.th.view.grid.sorted = sorted;""",
            sorted='^main.dbroot.th.view.grid.sorted',_delay=1,_userChanges=True)

        left.dynamicTableHandler(table='=main.sync_table',datapath='.dbroot',
                                 th_wdg='plain',
                                 th_view_store_applymethod='checksync_mainstore',
                                th_viewResource='View', 
                                th_configurable=True,
                                th_condition='==multidb_mode=="complete"?"":"@subscriptions.dbstore=:ext_dbstore"',
                                th_view_store_multidb_mode ='=main.multidb_mode',
                                th_condition_ext_dbstore='=main.dbstore',
                                nodeId='rootStore',_fired='^main.load_th')

        center.dynamicTableHandler(table='=main.sync_table',datapath='.dbext',
                                th_wdg='plain',
                                th_viewResource='View',
                                 th_view_store_applymethod='checksync_extstore',
                                th_view_store_currentDbstore='=main.dbstore',
                                th_view_store_forced_dbstore=True,
                                th_dbstore='=main.dbstore',
                                nodeId='syncStore',
                                #th_configurable=False,
                                _fired='^main.load_th')

    @public_method
    def checksync_mainstore(self,selection=None,**kwargs):
        self._checksync(selection)

    @public_method
    def checksync_extstore(self,selection=None,**kwargs):
        self._checksync(selection)


    def _checksync(self,selection):
        currentSync = self.pageStore().getItem('currentSync')
        def cb(row):
            sync_value = currentSync.get(row['pkey'])
            if not sync_value:
                sync_value = 'missing'
            if sync_value == 'equal':
                return
            return dict(_customClasses='sync_status_%s' %sync_value)
        selection.apply(cb)
        selection.sort('pkey')

    @public_method
    def getSyncTables(self,_querystring=None,_id=None,**kwargs):
        result = Bag()
        if _id:
            tableobj = self.db.table(_id)
            tblattr = tableobj.attributes
            caption = tableobj.fullname
            result.setItem(_id.replace('.','_'),None,caption=caption,
                        multidb='complete' if tblattr['multidb']=='*' else 'partial',
                        tablename=caption,
                        _pkey=caption)
            return result,dict(columns='tablename,multidb',headers='Table,Multidb')
        if _querystring:
            _querystring = _querystring.replace('*','')

        for pkgobj in self.db.packages.values():
            for tableobj in pkgobj.tables.values():
                tblattr = tableobj.attributes
                caption = tableobj.fullname
                if tblattr.get('multidb') and _querystring in caption:
                    result.setItem('%s_%s' %(pkgobj.id,tableobj.name),None,caption=caption,
                        multidb='complete' if tblattr['multidb']=='*' else 'partial',
                        tablename=caption,
                        _pkey=caption)
        return result,dict(columns='tablename,multidb',headers='Table,Multidb')

    @public_method
    def setSyncInfoInStore(self,insync_table=None,insync_store=None):
        tbl = self.db.table(insync_table)
        pkey = tbl.pkey
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False)
        if tbl.attributes.get('hierarchical'):
            queryargs.setdefault('order_by','$hierarchical_pkey')

        with self.db.tempEnv(storename=insync_store):
            store_f = tbl.query(**queryargs).fetch()

        where = '@subscriptions.dbstore=:insync_store' if tbl.attributes['multidb']!='*' else None
        main_f = tbl.query(where=where,insync_store=insync_store, **queryargs).fetchAsDict()
        result = dict()
        for r in store_f:
            r = dict(r)
            r.pop('__ins_ts',None)
            r.pop('__mod_ts',None)
            mr = main_f.pop(r[pkey],None)
            if mr:
                mr = dict(mr)
                mr.pop('__ins_ts',None)
                mr.pop('__mod_ts',None)
                if mr==r:
                    result[r[pkey]] = 'equal'
                else:
                    result[r[pkey]] = 'diff'
            else:
                result[r[pkey]] = 'onlystore'
        for k in main_f.keys():
            result[k] = 'onlymain'
        with self.pageStore() as store:
            store.setItem('currentSync',result)

