#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  public.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" public multidb """

from gnr.web.gnrbaseclasses import BaseComponent

class TableHandlerMain(BaseComponent):
    css_requires='multidb_public'
    def onMain_multidb_addOn(self):
        th = self.root_tablehandler
        self.__viewCustomization(th.view)
        self.__formCustomization(th.form)
    
    def __formCustomization(self,form):
        if self.dbstore:
            form.attributes.update(form_readOnly=True)
    
    def __viewCustomization(self,view): #poi ci passo il th direttamente
        table = view.getInheritedAttributes()['table']
        dragCode = 'multidb_%s' %table.replace('.','_')
        
        if self.dbstore:
            bar = view.top.bar
            bar.replaceSlots('delrow','unsubscriberow')
            bar.replaceSlots('addrow','subscribepalette')
            bar.unsubscriberow.slotButton('!!Unsubscribe',iconClass='iconbox delete_row',
                            action="""genro.serverCall('_table.multidb.subscription.delRowsSubscription',{table:tbl,pkeys:grid.getSelectedPkeys(),dbstore:dbstore,_dbstore:false});
                                        """,dbstore=self.dbstore,tbl=self.maintable,grid=view.grid.js_widget)
            palette = bar.subscribepalette.palettePane(paletteCode='mainstore',title='!!Mainstore',
                                        dockButton_iconClass='iconbox add_row',width='850px',
                                        height='400px',_lazyBuild=True,overflow='hidden')
            urlist = self.site.get_path_list(self.request.path_info)
            urlist.pop(0)
            palette.iframe(src='/%s' %'/'.join(urlist),height='100%',width='100%',border=0,
                          main_th_public=False,main_fromdbstore=self.dbstore)
            gridattr = view.grid.attributes
            gridattr.update(dropTags=dragCode,dropTypes='dbrecords',
                                        onDrop_dbrecords="""function(dropInfo,data){
                                            genro.serverCall('_table.multidb.subscription.addRowsSubscription',{table:data['table'],pkeys:data.pkeys,dbstore:'%s',_dbstore:false});
                                        }""" %self.dbstore)
            currCodes = gridattr.get('dropTarget_grid')
            currCodes = currCodes.split(',') if currCodes else []
            if not 'dbrecords' in currCodes:
                currCodes.append('dbrecords')
            gridattr['dropTarget_grid'] = ','.join(currCodes)
            
            view.onDbChanges(action="""
            if(dojo.some(dbChanges,function(c){return (c['tablename']==tablename) && (c['dbstore']==dbstore);})){
                store.fireNode();
            };
        
        """,table='multidb.subscription',tablename=self.maintable,dbstore=self.dbstore,store=view.store)
            
        else:
            fromdbstore = self._call_kwargs['fromdbstore']
            gridattr = view.grid.attributes
            gridattr['dragTags'] = dragCode
            hiddencolumns = gridattr.get('hiddencolumns')
            hiddencolumns = hiddencolumns.split(',') if hiddencolumns else []
            hiddencolumns.append(' @subscriptions.dbstore AS _dbstorename ')
            gridattr['hiddencolumns'] = ','.join(hiddencolumns)
            gridattr['rowCustomClassesCb']="""function(row){
                                                  return row['_dbstorename']=='%s'?'multidb_imported':null;
                                              }""" %fromdbstore
            view.onDbChanges(action="""
            console.log('xxx',dbChanges)
            if(dojo.some(dbChanges,function(c){return (c['tablename']==tablename) && (c['dbstore']==dbstore);})){
                console.log('ffff',grid);
                grid.updateRowCount(0);
                grid.updateRowCount();
            };
        
            """,table='multidb.subscription',tablename=self.maintable,dbstore=fromdbstore,grid=view.grid.js_widget)
        