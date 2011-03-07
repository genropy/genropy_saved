#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  pluginhandler.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrlang import gnrImport

class GnrWebPluginHandler(GnrBaseProxy):
    def init(self, **kwargs):
        self.plugin_dict = {}

    def get_plugin(self, plugin_name, **kwargs):
        plugin = self.plugin_dict.get(plugin_name)
        if not plugin:
            plugin_class = self.load_plugin(plugin_name)
            if plugin_class:
                plugin = plugin_class(self.page, **kwargs)
                self.plugin_dict[plugin_name] = plugin
                return plugin
            else:
                raise

    def load_plugin(self, plugin_name):
        if self.page.packageId:
            plugin_folder = os.path.join(self.page.pkgapp.libPath, 'plugins')
            plugin_module_name = "%s.py" % plugin_name
            plugin_module = gnrImport(os.path.join(os.path.join(plugin_folder, plugin_module_name)), avoidDup=True)
        if not plugin_module:
            plugin_module = gnrImport('gnr.web.gnrwebpage_plugin.%s' % plugin_name)
            plugin_class = getattr(plugin_module, 'Plugin')
        return plugin_class
                    