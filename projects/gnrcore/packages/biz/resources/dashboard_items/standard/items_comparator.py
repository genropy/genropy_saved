# -*- coding: utf-8 -*-
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
objtype = 'dash_items_comparator'

item_parameters = [dict(value='^.item_1',lbl='Sheet 1',tag='callBackSelect',validate_notnull=True,
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
            }""",hasDownArrow=True),
            dict(value='^.compare_mode',lbl='Op',values='diff:-,perc_change:Perc.Change',tag='filteringSelect'),
            dict(value='^.item_2',lbl='Sheet 2',tag='callBackSelect',validate_notnull=True,
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
            }""",hasDownArrow=True)]


class Main(BaseDashboardItem):
    title_template = '$title'
    def content(self,pane,item_1=None,item_2=None,compare_mode=None,**kwargs):
        frame = pane.bagGrid(frameCode=self.itemIdentifier,
                            structpath='%s.struct' %self.workpath,datamode='attr',
                            storepath='%s.store' %self.workpath,
                            datapath=self.workpath,
                            addrow=False,delrow=False)
        pane.dataController("""
            var cmp_store = new gnr.GnrBag();
            var structrow = basestruct.getItem('view_0.rows_0');
            var cmp_struct = new gnr.GnrBag();
            var cmp_struct_row = new gnr.GnrBag();
            cmp_struct.setItem('view_0.rows_0',cmp_struct_row);
            compare_mode = compare_mode || 'diff';

            store_1.forEach(function(n){
                var row1 = n.attr;
                var row = objectUpdate({},row1);
                var row2 = store_2.getNodeByAttr('_thgroup_pkey',row1._thgroup_pkey);
                row2 = row2?row2.attr:{}
                structrow.forEach(function(sn){
                    var cmp_struct_node = cmp_struct_row.setItem(sn.label,null,sn.attr);
                    objectPop(cmp_struct_node.attr,'totalize');
                    if('NLIRF'.indexOf(sn.attr.dtype)>=0 && !sn.attr.group_nobreak){
                        var kf = sn.attr.field+'_sum';
                        if(compare_mode=='diff'){
                            row[kf] = (row1[kf] || 0) - (row2[kf] || 0)
                        }else{
                            console.log('changing format',cmp_struct_node.attr)
                            cmp_struct_node.attr.format = '#,###.00;-;<span style="color:red">-#,###.00</span>'
                            if(row2[kf]){
                                row[kf] = (((row1[kf] || 0) - (row2[kf] || 0))/row2[kf]) *100;
                            }else{
                                row[kf] = null;
                            }
                        }
                        
                    }
                })
                cmp_store.setItem(n.label,null,row);
            });
            SET %s.struct = cmp_struct;
            SET %s.store = cmp_store;

        """ %(self.workpath,self.workpath),
        store_1='^#%s.store' %item_1,
            store_2='^#%s.store' %item_2,
            basestruct='=#%s_grid.struct' %item_1,
            _fired='^%s.runItem' %self.workpath,
            _delay=100,
            compare_mode='^.conf.compare_mode',_if='store_1 && store_2',
            _else="SET %s.store = new gnr.GnrBag()" %self.workpath)

    def configuration(self,pane,item_1=None,item_2=None,compare_mode=None,**kwargs):
        fb = pane.formbuilder()
        fb.filteringSelect(value='^.compare_mode',lbl='!!Compare mode',
                        default_value=compare_mode,values='diff:-,perc_change:Perc.Change')
        
