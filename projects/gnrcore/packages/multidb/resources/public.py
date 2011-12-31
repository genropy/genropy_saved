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
        th = self.root_tablehandler
        self.__viewCustomization(th.view)

    def __viewCustomization(self,view): #poi ci passo il th direttamente
        table = view.getInheritedAttributes()['table']
        dragCode = 'multidb_%s' %table.replace('.','_')
        if self.dbstore:
            bar = view.top.bar
            bar.replaceSlots('delrow','unsubscriberow')
            bar.replaceSlots('addrow','subscribepalette')
            bar.unsubscriberow.slotButton('"!!Unsubscribe',iconClass='iconbox delete_row')
            palette = bar.subscribepalette.palettePane(paletteCode='mainstore',title='!!Mainstore',
                                        dockButton_iconClass='iconbox add_row',width='850px',
                                        height='400px',_lazyBuild=True,overflow='hidden')
            urlist = self.site.get_path_list(self.request.path_info)
            urlist.pop(0)
            palette.iframe(src='/%s' %'/'.join(urlist),height='100%',width='100%',border=0,
                          main_th_public=False)
            view.grid.attributes.update(dropTags=dragCode,dropTypes='dbrecords',
                                        onDrop_dbrecords="""function(dropInfo,data){
                                            genro.serverCall('_table.multidb.subscription.addRowsSubscription',{table:data['table'],pkeys:data.pkeys,dbstore:'%s'});
                                        }""" %self.dbstore)
        else:
            gridattr = view.grid.attributes
            gridattr['dragTags'] = dragCode

        