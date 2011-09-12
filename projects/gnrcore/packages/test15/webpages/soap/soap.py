#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrsoappage import GnrSoapPage as page_factory

from soaplib.core.service import soap

from soaplib.core.model.primitive import String, Integer

class GnrCustomWebPage(object):
    
    @soap(String,String,_returns=String)
    def test(self, pippo, pluto):
        print pippo
        print x
        print pluto
        return pluto
