#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.web.gnrwsgisite_proxy.gnrresourceloader import GnrMixinError
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = """public:Public"""

    def windowTitle(self):
        return '!!Monitor panel'

    def onIniting(self, url_parts, request_kwargs):
        for pkgname in self.db.packages.keys():
            try:
                cl = self.site.loadResource(pkgname, 'monitor:Monitor')
                self.mixin(cl)
            except GnrMixinError:
                pass

    def main(self, root, **kwargs):
        """MONITOR BUILDER"""
        tc = root.rootTabContainer(title='Monitor', datapath='monitor')
        for pkg in self.db.packages.values():
            auth = True
            permmissioncb = getattr(self, 'permission_%s' % pkg.name, None)
            if permmissioncb:
                auth = self.application.checkResourcePermission(permmissioncb(), self.userTags)
            if auth:
                cblist = sorted(
                        [func_name for func_name in dir(self) if func_name.startswith('monitor_%s_' % pkg.name)])
                if len(cblist) > 0:
                    pane = tc.contentPane(title=pkg.name_full, datapath='.%s' % pkg.name)
                    for cbname in cblist:
                        data_name = cbname[len('monitor_%s_' % pkg.name):]
                        getattr(self, cbname)(pane.titlePane(title=data_name.title(), datapath='.%s' % data_name))

        tc.dataRpc('monitor', 'monitorUpdate', _timing='5', _onStart=True)

    def rpc_monitorUpdate(self):
        result = Bag()
        for pkg in self.db.packages.values():
            cblist = sorted(
                    [func_name for func_name in dir(self) if func_name.startswith('rpc_monitor_%s_' % pkg.name)])
            if len(cblist) > 0:
                result[pkg.name] = Bag()
                for cbname in cblist:
                    data_name = cbname[len('rpc_monitor_%s_' % pkg.name):]
                    result[pkg.name][data_name] = Bag(getattr(self, cbname)())
        return result