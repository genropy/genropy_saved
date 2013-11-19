#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  localizer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
import hashlib
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
import time

class GnrWebLocalizer(GnrBaseProxy):
    """A class for handle the site localization and the translation for :ref:`languages`"""
    def init(self, **kwargs):
        """TODO"""
        self.locale = self.page.locale
        if '-' in self.locale:
            self.locale = self.locale.split('-')[0]
        self.localizer_dict = {}
        self.missingLoc = False

    def event_onEnd(self):
        """TODO"""
        if self.localizer_dict:
            self.page.site.register.updateLocalization(page_id=self.page.page_id,localizer_dict=self.localizer_dict,register_name='page')

    def localize(self,txt):
        """Localize a string beginning with the :ref:`\!\! <exclamation_point>` character"""
        if txt.startswith('!!'):
            return self.translateText(txt[2:])
        return txt
        
    def translateText(self, txt):
        """Translate the *txt* string following the browser's locale
        
        :param txt: the text to be translated"""
        application = self.page.application
        key = '%s|%s' % (self.page.packageId, txt.lower())
        localelang = self.locale
        loc = application.localization.get(key)
        missingLoc = True
        if not loc:
            key = txt
            loc = application.localization.get(txt)
        if loc:
            loctxt = loc.get(localelang)
            if loctxt:
                missingLoc = False
                txt = loctxt
        elif loc is None:
            self._translateMissing(txt)
            application.localization[key] = {}
        if self.page.isLocalizer():
            self.localizer_dict[key] = application.localization[key]
            self.missingLoc = self.missingLoc or missingLoc
        return txt
        
    def _translateMissing(self, txt):
        return
        ### DISABLED WAITING FOR FURTHER INVESTIGATIONS ###
        #if not self.page.packageId: return
        #missingpath = os.path.join(self.page.siteFolder, 'data', '_missingloc', self.page.packageId)
        #if isinstance(txt, unicode):
        #    txtmd5 = txt.encode('utf8', 'ignore')
        #else:
        #    txtmd5 = txt
        #fname = os.path.join(missingpath, '%s.xml' % hashlib.md5(txtmd5).hexdigest())
        #if not os.path.isfile(fname):
        #    b = Bag()
        #    b['txt'] = txt
        #    b['pkg'] = self.page.packageId
        #    old_umask = os.umask(2)
        #    b.toXml(fname, autocreate=True)
        #    os.umask(old_umask)

    def _get_status(self):
        if self.missingLoc:
            return 'missingLoc'
        else:
            return 'ok'

    status = property(_get_status)

    #### BEGIN: RPC Section ##########

    def rpc_pageLocalizationSave(self, data, **kwargs):
        """TODO
        
        :param data: TODO"""
        self.page.application.updateLocalization(self.page.packageId, data, self.locale)
        self.page.siteStatus['resetLocalizationTime'] = time.time()
        self.page.siteStatusSave()

    def rpc_pageLocalizationLoad(self):
        """TODO"""
        loc = self.page.pageStore().getItem('localization')
        b = Bag()
        loc_items = loc.items()
        loc_items.sort()
        for j, kv in enumerate(loc_items):
            k, v = kv
            if '|' in k:
                k = k.split('|')[1]
            b['r_%i.key' % j] = k
            b['r_%i.txt' % j] = v.get(self.locale)
        return b
