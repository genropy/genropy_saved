#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import hashlib
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
import time

class GnrWebLocalizer(GnrBaseProxy):
    def init(self, **kwargs):
        self.locale = self.page.locale
        if '-' in self.locale:
            self.locale = self.locale.split('-')[0]
        self.localizer_dict = {}
        self.missingLoc = False

    def event_onEnd(self):
        with self.page.pageStore() as store:
            localization = {}
            localization.update(store.getItem('localization') or {})
            localization.update(self.localizer_dict)
            store.setItem('localization', localization)

    def translateText(self, txt):
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
        else:
            self._translateMissing(txt)
            application.localization[key] = {}
        if self.page.isLocalizer():
            self.localizer_dict[key] = application.localization[key]
            self.missingLoc = self.missingLoc or missingLoc
        return txt


    def _translateMissing(self, txt):
        if not self.page.packageId: return
        missingpath = os.path.join(self.page.siteFolder, 'data', '_missingloc', self.page.packageId)
        if isinstance(txt, unicode):
            txtmd5 = txt.encode('utf8', 'ignore')
        else:
            txtmd5 = txt
        fname = os.path.join(missingpath, '%s.xml' % hashlib.md5(txtmd5).hexdigest())

        if not os.path.isfile(fname):
            b = Bag()
            b['txt'] = txt
            b['pkg'] = self.page.packageId
            old_umask = os.umask(2)
            b.toXml(fname, autocreate=True)
            os.umask(old_umask)

    def _get_status(self):
        if self.missingLoc:
            return 'missingLoc'
        else:
            return 'ok'

    status = property(_get_status)

    #### BEGIN: RPC Section ##########

    def rpc_pageLocalizationSave(self, data, **kwargs):
        self.page.application.updateLocalization(self.page.packageId, data, self.locale)
        self.page.siteStatus['resetLocalizationTime'] = time.time()
        self.page.siteStatusSave()

    def rpc_pageLocalizationLoad(self):
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
        #### BEGIN: RPC Section ##########