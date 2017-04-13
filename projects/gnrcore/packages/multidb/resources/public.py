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
    def onMain_multidb_addOn(self):
        if not self.tblobj.multidb:
            return
        th = getattr(self,'root_tablehandler',None)
        if th:
            self.__viewCustomization(th.view)
            if hasattr(th,'form'):
                self.__formCustomization(th.form)

    def __formCustomization(self,form):
        multidb = self.tblobj.multidb
        if not self.dbstore:
            if multidb is True:
                bar = form.top.bar.replaceSlots(',*,',',*,cb_default_sub,10,')
                bar.cb_default_sub.checkbox(value='^#FORM.record.__multidb_default_subscribed',
                                        label='!!Subscribed by default',margin_top='1px',
                                        label_color='#666',label_font_size='.9em',
                                        label_font_weight='bold') 
            return

        readOnly = self.tblobj.attributes.get('multidb_onLocalWrite') != 'merge'
        if readOnly:
            form.attributes.update(form_readOnly=True)
        else:
            bar = form.top.bar.replaceSlots(',*,',',*,merge_tool,10,')
            box = bar.merge_tool.div(width='20px')
            merge_tool = box.div(_class='iconbox warning',hidden='^#FORM.record?_multidb_diff?=!#v')
            tpane = merge_tool.tooltipPane(onOpening="""

                """)
            fpane = tpane.roundedGroupFrame(title='Localstore differences',height='200px',width='550px')
            grid = fpane.quickgrid(value='^#FORM.localstore_changes')
            grid.column('fname',name='Field',width='10em')
            grid.column('mvalue',name='Main value',width='15em')
            grid.column('lvalue',name='local value',width='15em')


    def __viewCustomization(self,view): #poi ci passo il th direttamente
        table = view.getInheritedAttributes()['table']
        
        
        if self.dbstore:
            dragCode = 'multidb_%s_%s' %(table.replace('.','_'),self.dbstore)
            bar = view.top.bar
            if 'delrow' in bar.keys():
                bar.replaceSlots('delrow','unsubscriberow')
                bar.unsubscriberow.slotButton('!!Unsubscribe',iconClass='iconbox delete_row',
                            action="""genro.serverCall('_table.multidb.subscription.delRowsSubscription',{table:tbl,pkeys:grid.getSelectedPkeys(),dbstore:dbstore,temp_dbstore:false});
                                        """,dbstore=self.dbstore,tbl=self.maintable,grid=view.grid.js_widget,disabled='^.disabledButton')
            if 'addrow' in bar.keys():
                bar.replaceSlots('addrow','subscribepalette')
                palette = bar.subscribepalette.palettePane(paletteCode='mainstore',title='!!Mainstore',
                                            dockButton_iconClass='iconbox add_row',width='900px',
                                            height='400px',_lazyBuild=True,overflow='hidden',dockButton_disabled='^.disabledButton')
                urlist = self.site.get_path_list(self.request.path_info)
                urlist.pop(0)
                palette.iframe(src='/%s' %'/'.join(urlist),height='100%',width='100%',border=0,
                              main_th_public=False,main_env_target_store=self.dbstore,
                              nodeId='subscriber_palette')
                gridattr = view.grid.attributes
                gridattr.update({'onDrop_%s' %dragCode:"""function(dropInfo,data){
                                                if(data.table!='%s'){
                                                    return false;
                                                }
                                                genro.serverCall('_table.multidb.subscription.addRowsSubscription',
                                                                {table:data['table'],pkeys:data.pkeys,dbstore:'%s',temp_dbstore:false},
                                                                function(){
                                                                    genro.publish({topic:'ping',iframe:'subscriber_palette'});
                                                                });
                                            }""" %(self.maintable,self.dbstore)})
                currCodes = gridattr.get('dropTarget_grid')
                currCodes = currCodes.split(',') if currCodes else []
                currCodes.append(dragCode)
                gridattr['dropTarget_grid'] = ','.join(currCodes)                
                view.onDbChanges(action="""
                if(dojo.some(dbChanges,function(c){return (c['tablename']==tablename) && (c['dbstore']==dbstore);})){
                    store.fireNode();
                };
            
            """,table='multidb.subscription',tablename=self.maintable,dbstore=self.dbstore,store=view.store)
            
        elif 'env_target_store' in self._call_kwargs:
            dragCode = 'multidb_%s_%s' %(table.replace('.','_'),self._call_kwargs['env_target_store'])
            target_store = self._call_kwargs.get('env_target_store')
            gridattr = view.grid.attributes
            
            hiddencolumns = gridattr.pop('hiddencolumns',None)
            hiddencolumns = '%s,$__multidb_subscribed' if hiddencolumns else '$__multidb_subscribed'
            gridattr['hiddencolumns'] = hiddencolumns
            gridattr['rowCustomClassesCb']="""function(row){
                                                return row['__multidb_subscribed']?'dimmed':'';
                                            }"""
            gridattr['onDrag_%s' %dragCode] = "dragValues['%s']=dragValues['dbrecords'];" %dragCode
            store = view.store 
           #storeattr = store.attributes
           #condition = storeattr.pop('condition',None)
            #condition = '%s AND $__multidb_subscribed IS NOT TRUE' %condition if condition else '$__multidb_subscribed IS NOT TRUE'
            #storeattr['condition'] = condition
            view.onDbChanges(action="""
            if(dojo.some(dbChanges,function(c){return (c['tablename']==tablename) && (c['dbstore']==dbstore);})){
                store.fireNode();
            };
            """,table='multidb.subscription',tablename=self.maintable,dbstore=target_store,store=store)
