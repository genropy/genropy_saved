# -*- coding: UTF-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag 

class ChartManager(BaseComponent):
    js_requires = 'gnrcomponents/chartmanager/chartmanager'

    @struct_method
    def crt_slotbar_charts(self,pane,_class='iconbox chart_bar',mode='bar',enable=None,rawData=True,parameters=None,**kwargs):
        gridattr = pane.frame.grid.attributes
        gridId = gridattr['nodeId']
        storepath = '#%s.chartsMenu' %gridId
        pane.menudiv(iconClass=_class,storepath=storepath,tip='!!Charts',
                    action="genro.publish({topic:'openChart',nodeId:'%(nodeId)s'},$1);" %gridattr)
        gridattr['selfsubscribe_openChart'] = """
            genro.charts.openChart({data:this.widget.storebag(),
                                    code:this.attr.nodeId+'_chart_'+($1.pkey || '_newchart') +'_'+ genro.getCounter(),
                                    title:$1.caption,
                                    pkeys:this.widget.getSelectedPkeys(),
                                    struct:this.widget.structbag().deepCopy(),
                                    datamode:this.widget.datamode});
        """
        pane.dataRemote(storepath,self.crt_menuCharts,table=gridattr.get('table'),
                        gridId=gridId)

    @public_method
    def crt_menuCharts(self,table=None,pyviews=None,favoriteViewPath=None,gridId=None,**kwargs):
        result = Bag()
        if pyviews:
            for k,caption in pyviews:
                result.setItem(k.replace('_','.'),None,description=caption,caption=caption,viewkey=k,gridId=gridId)
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype='chart',flags='%s_%s' % (self.pagename, gridId) if gridId else None,table=table)
        if len(userobjects)>0:
            result.update(userobjects)
            result.setItem('r_sep',None,caption='-')
        result.setItem('__newchart__',None,caption='!!New Chart')
        return result
    