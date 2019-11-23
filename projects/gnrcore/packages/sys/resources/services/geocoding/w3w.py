#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from __future__ import print_function
from gnrpkg.sys.services.geocoding import GeocodeService

from gnr.core.gnrlang import GnrException
import re
SAFETRANSLATE = re.compile(r"""(?:\[tr-off\])(.*?)(?:\[tr-on\])""",flags=re.DOTALL)

try:
    import what3words
except:
    what3words = False

class Main(GeocodeService):
    def __init__(self, parent=None,api_key=None):
        super(Main, self).__init__(parent=parent,api_key=api_key)
        if not what3words:
            raise GnrException('Missing what3words. hint: pip install what3words')
        self.geocoder = what3words.Geocoder(self.api_key)
        
    def get_coordinates(self,source):
        return self.geocoder.convert_to_coordinates(source)