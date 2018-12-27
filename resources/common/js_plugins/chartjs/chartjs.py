# -*- coding: utf-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag 

class ChartManager(BaseComponent):
    @struct_method
    def crt_slotbar_chartjs(self,pane,_class='iconbox chart_bar',mode='bar',gridId=None,
                            enable=None,rawData=True,parameters=None,**kwargs):
        if gridId:
            gridNode = self.pageSource().nodeById(gridId)
            gridattr = gridNode.attr
        else:
            gridattr = pane.frame.grid.attributes
            gridId = gridattr['nodeId']
        storepath = '#%s.chartsMenu' %gridId
        pane.slotButton(iconClass=_class,menupath=storepath,label='!!Charts',
                    action="genro.publish({topic:'openChart',nodeId:'%(nodeId)s'},$1);" %gridattr)
        gridattr['selfsubscribe_openChart'] = """this.publish('pluginCommand',
                                                                {plugin:'chartjs',
                                                                command:'openGridChart',
                                                                pkey:$1.pkey,caption:$1.caption});"""

        pane.dataRemote(storepath,self.crt_menuCharts,table=gridattr.get('table'),
                        gridId=gridId)

    @public_method
    def crt_menuCharts(self,table=None,pyviews=None,favoriteViewPath=None,gridId=None,**kwargs):
        result = Bag()
        userobjects = self.db.table('adm.userobject').userObjectMenu(objtype='chartjs',flags='%s_%s' % (self.pagename, gridId) if gridId else None,table=table)
        if len(userobjects)>0:
            result.update(userobjects)
            result.setItem('r_sep',None,caption='-')
        result.setItem('__newchart__',None,caption='!!New Chart')
        return result

class ChartPane(BaseComponent):
    js_requires='js_plugins/chartjs/chartjs,/_rsrc/js_libs/chroma.min,/_rsrc/js_libs/distinct-colors.min'
    css_requires='js_plugins/chartjs/chartjs'

    
