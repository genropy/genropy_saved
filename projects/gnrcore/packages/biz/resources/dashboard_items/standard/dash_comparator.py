# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from gnrpkg.biz.dashboard import BaseDashboardItem
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method


caption = 'Compare items'
description = 'Item comparator'
objtype = 'dash_comparator'

item_parameters = [dict(value='^.item_1',lbl='Item 1',tag='callBackSelect',validate_notnull=True,
                        selected_caption='.item_1_caption',
                        callback="""function(kw){
                var _id = kw._id;
                var _querystring = kw._querystring;
                var data = genro.getData(genro.dashboards[this.sourceNode.attr.dashboardIdentifier].itemspath);
                data = data.getNodes().map(function(n){
                    return {_pkey:n.label,caption:n.getValue().getItem('title')};
                })
                var cbfilter = function(n){return true};
                if(_querystring){
                    _querystring = _querystring.slice(0,-1).toLowerCase();
                    cbfilter = function(n){return n.caption.toLowerCase().indexOf(_querystring)>=0;};
                }else if(_id){
                    cbfilter = function(n){return n._pkey==_id;}
                }
                data = data.filter(cbfilter);
                return {headers:'',data:data}
            }""",hasDownArrow=True),dict(value='^.item_2',lbl='Item 2',tag='callBackSelect',validate_notnull=True,
                        selected_caption='.item_2_caption',
                        callback="""function(kw){
                var _id = kw._id;
                var _querystring = kw._querystring;
                var data = genro.getData(genro.dashboards[this.sourceNode.attr.dashboardIdentifier].itemspath);
                data = data.getNodes().map(function(n){
                    return {_pkey:n.label,caption:n.getValue().getItem('title')};
                })
                var cbfilter = function(n){return true};
                if(_querystring){
                    _querystring = _querystring.slice(0,-1).toLowerCase();
                    cbfilter = function(n){return n.caption.toLowerCase().indexOf(_querystring)>=0;};
                }else if(_id){
                    cbfilter = function(n){return n._pkey==_id;}
                }
                data = data.filter(cbfilter);
                return {headers:'',data:data}
            }""",hasDownArrow=True),
            dict(value='^.compare_mode',lbl='Mode',values='diff,perc',tag='filteringSelect')]


class Main(BaseDashboardItem):
    title_template = '$title'
    def content(self,pane,table=None,userobject_id=None,item_1=None,item_2=None,compare_mode=None,**kwargs):
        frame = pane.bagGrid(frameCode=self.itemIdentifier,structpath='#%s_grid.struct' %item_1,datamode='attr',
                            storepath='%s.store' %self.workpath,datapath=self.workpath,addrow=False,delrow=False)
        frame.dataController("""
            var cmp_store = new gnr.GnrBag();
            store_1.forEach(function(n){
                var row = objectUpdate({},n.attr);
                var row2 = store_2.getNodeByAttr('_thgroup_pkey',row._thgroup_pkey);
                row2 = row2?row2.attr:{}
                structrow.forEach(function(sn){
                    if(sn.attr.group_aggr=='sum'){
                        row[sn.attr.field+'_sum'] -= (row2[sn.attr.field+'_sum'] || 0)
                    }
                })
                cmp_store.setItem(n.label,null,row);
            });
            SET .store = cmp_store;

        """,store_1='^#%s.store' %item_1,
            store_2='^#%s.store' %item_2,
            structrow='=#%s_grid.struct.view_0.rows_0' %item_1,
            _fired='^.runItem',datapath=self.workpath,
            compare_mode=compare_mode,_if='store_1&&store_2',
            _else="SET .store = new gnr.GnrBag()")

