#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package            : GenroPy web - see LICENSE for details
# module gnrhtmlpage : Genro Web structures implementation
# Copyright (c)      : 2004 - 2009 Softwell sas - Milano 
# Written by         : Giovanni Porcari, Michele Bertoldi
#                      Saverio Porcari, Francesco Porcari
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

from gnr.web.gnrwebpage import GnrWebPage
from time import time
from gnr.core.gnrstring import boolean

class GnrSimplePage(GnrWebPage):
    
    def __init__(self, site=None, page_id=None, request_kwargs=None, request_args=None,
                 filepath=None, packageId=None, pluginId=None, basename=None):
        self._inited = False
        self._start_time = time()
        self.workspace = dict()
        self.sql_count = 0
        self.sql_time = 0
        self.site = site
        #dbstore = request_kwargs.pop('temp_dbstore',None) or None
        #self.dbstore = dbstore if dbstore != self.application.db.rootstore else None
        self.dbstore=None  # find a way to handle it based on call/thread
        self._locale='en'  # find a way to handle it based on call/thread
        self._event_subscribers = {}
        self.filepath = filepath
        self.packageId = packageId
        self.pluginId = pluginId
        self.basename = basename
        self.siteFolder = self.site.site_path
        self.folders = self._get_folders()
        self.pagepath = self.filepath.replace(self.folders['pages'], '')
        self._dbconnection = None
        self.application.db.clearCurrentEnv() # ?? dump and restore?
        self.debug_sql = boolean(request_kwargs.pop('debug_sql', None))
        debug_py = request_kwargs.pop('debug_py', None)
        self.debug_py = False if boolean(debug_py) is not True else debug_py
        self.callcounter = request_kwargs.pop('callcounter', None) or 'begin'
        self.root_page_id = None
        self.parent_page_id = None
        self.sourcepage_id = request_kwargs.pop('sourcepage_id', None)
        self.instantiateProxies()
        self.onPreIniting(request_args, request_kwargs)
        self.onIniting(request_args, request_kwargs)
        self._call_args = request_args or tuple()
        self._call_kwargs = dict(request_kwargs)
        self.page_item = self._check_page_id(page_id, kwargs=request_kwargs)
        self._workdate = self.page_item['data']['rootenv.workdate'] #or datetime.date.today()
        self._language = self.page_item['data']['rootenv.language']
        self._inited = True
    
    def _check_page_id(self, page_id=None, kwargs=None):
        page_item = self.site.register.page(page_id,include_data='lazy')
        if not page_item:
            raise self.site.client_exception('The referenced page_id is cannot be found in site register',
                                             self._environ)
        self.page_id = page_id
        self.root_page_id = page_item['data'].getItem('root_page_id')
        self.parent_page_id = page_item['data'].getItem('parent_page_id')
        return page_item   


    def replayComponentMixins(self):
    	with self.pageStore() as store:
    		mixin_set = store.get('mixin_set') or []
    		for (path,kwargs_list) in mixin_set:
    			print path, kwargs_list
    			kwargs = dict(kwargs_list)
    			self.site.resource_loader.mixinPageComponent(self, *path,**kwargs)