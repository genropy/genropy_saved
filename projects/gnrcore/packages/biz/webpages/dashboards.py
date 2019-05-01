# -*- coding: utf-8 -*-

# dashboards gallery.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import boolean
from gnr.core.gnrdict import dictExtract

class GnrCustomWebPage(object):
    py_requires="""public:Public,th/th:TableHandler,
                    dashboard_component/dashboard_component:DashboardGallery"""
    public_multidbSelector = True 

    def main(self,root,th_public=None,**kwargs):
        callArgs = self.getCallArgs('dash_pkg','dash_code')
        root.attributes['datapath'] = 'main'
        pkg = callArgs.get('dash_pkg')
        code = callArgs.get('dash_code')
        title = '!!Dashboards'
        dashboard_tbl = self.db.table('biz.dashboard')
        dashboard_record = None
        if pkg:
            if code:
                dashboard_record = dashboard_tbl.record(pkey='%s_%s' %(pkg,code)).output('dict')
                title = dashboard_record['description'] or 'Dashboard :%s'  %dashboard_record['code']  
            else:
                title = '%s Dashboards'  %self.db.package(pkg).name_long  

        public=boolean(th_public) if th_public else True
        if public:
            root = root.rootContentPane(title=title,**kwargs)
        frame = root.framePane(nodeId='lookup_root')
        if not (pkg and code):
            bar = frame.top.slotToolbar('2,fbfilters,*')
            fb = bar.fbfilters.formbuilder(cols=2,border_spacing='2px')
            if not pkg:
                packages =  [r['pkgid'] for r in dashboard_tbl.query(columns='$pkgid',distinct=True).fetch()]
                fb.filteringSelect(value='^main.selected_pkg',lbl='!!Package',values=','.join(packages))
            else:
                frame.data('main.selected_pkg',pkg)
            if not code:
                fb.dbSelect(value='^main.selected_dashboard',lbl='!!Dashboard',dbtable='biz.dashboard',
                            condition='$pkgid=:pk',condition_pk='=main.selected_pkg',
                            selected_code='main.selected_code',
                            disabled='^main.selected_pkg?=!#v',hasDownArrow=True)
            else:
                frame.data('main.selected_code',code)
        else:
            frame.data('main.selected_pkg',pkg)
            frame.data('main.selected_code',code)
        frame.dashboardGallery(nodeId='gallery',datapath='.gallery',pkg='^main.selected_pkg',code='^main.selected_code')

        