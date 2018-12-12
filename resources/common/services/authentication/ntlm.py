#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#

# Required:
#
#    pip install python-ntlm
#

from gnr.lib.services import GnrBaseService
import urllib2
from ntlm import HTTPNtlmAuthHandler

class Main(GnrBaseService):
    """
    ntlm authentication service 
    inside siteconfig.xml

        <services>
            ... other services

            <ntml service_type='authentication' resource='ntlm' url='http://www.url_di_dominio_NTLM.it/' template='FOO\\%s' case='l' /> 
        </services>

    """
    def __init__(self, parent=None,url=None,template=None,case=None):
        self.url = url 
        self.parent = parent
        self.template = template or '%s'
        self.case = case

    def __call__(self, user=None,password=None,**kwargs):
        if self.case=='l':
            user = user.lower()
        elif self.case=='u':
            user = user.upper()
        user = self.template %user
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.url, user, password)
        # create the NTLM authentication handler
        auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)

        # create and install the opener
        opener = urllib2.build_opener(auth_NTLM)
        urllib2.install_opener(opener)

        # retrieve the result
        response = urllib2.urlopen(self.url)

        if response.read():
            return True
        else:
            return False


