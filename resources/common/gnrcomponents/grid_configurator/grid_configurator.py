# -*- coding: UTF-8 -*-

# grid_configurator.py
# Created by Francesco Porcari on 2010-10-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

class GridConfigurator(BaseComponent):
    js_requires='gnrcomponents/grid_configurator/grid_configurator'
    css_requires='gnrcomponents/grid_configurator/grid_configurator'


    def rpc_gridConfigurationMenu(self,gridId=None,table=None,selectedViewPkey=None):
        result = Bag()
        if not hasattr(self.package,'listUserObject'):
            return
        objtype ='iv_%s_%s' %(self.pagename,gridId)
        objectsel = self.package.listUserObject(objtype=objtype,userid=self.user,authtags=self.userTags)
        selectedViewPkey = selectedViewPkey or None
        result.setItem('baseview',None,
                        action="genro.grid_configurator.loadGridBaseView(this.attr.gridId)",
                        label='Base View',checked=selectedViewPkey is None,
                        gridId=gridId)
        if objectsel:
            for i,r in enumerate(objectsel.data):
                attrs = dict([(str(k), v) for k,v in r.items()])
                result.setItem(r['code'] or 'r_%i' % i, None, label = attrs.get('description'),pkey=attrs['pkey'],checked=selectedViewPkey==attrs['pkey']);
        result.setItem('_spacer_',None,label='-')
        if table:
            result.setItem('fieldstree',None,label='!!Show Fields Tree',floating_title='!! Fields',
                       action="""genro.dev.relationExplorer(this.attr.table,this.attr.floating_title,{'left':$3.pageX+'px','top':$3.pageY+'px','height':'270px','width':'180px'})""",table=table)
        result.setItem('save',None,label='!!Save',action='genro.grid_configurator.saveGridView(this.attr.gridId);',gridId=gridId)
        result.setItem('delete',None,label='!!Delete',action='genro.grid_configurator.deleteGridView(this.attr.gridId);',gridId=gridId,disabled='==_selectedViewPkey==null;',_selectedViewPkey='=.selectedViewPkey')
        return result
        
    def rpc_deleteViewGrid(self,pkey=None):
        self.package.deleteUserObject(pkey)
        self.db.commit()

    def rpc_saveGridCustomView(self,gridId=None,save_info=None,data=None):
        description = save_info['description']
        code = description.replace('.','_').lower()
        objtype ='iv_%s_%s' %(self.pagename,gridId)
        pkey = save_info.get('id')
        record = self.package.loadUserObject(id=pkey)[1]
        if record:
            if record['code'] != code:
                pkey = None
        record = self.package.saveUserObject(data, code=code, 
                                    description=description,
                                    id=pkey,
                                    private=bool(save_info['private']),
                                    objtype=objtype)
        self.db.commit()
        return self.package.loadUserObject(id=record.getItem('id'))
        
    def rpc_loadGridCustomView(self,pkey=None):
        data, metadata = self.package.loadUserObject(id=pkey)
        return (data, metadata)
    