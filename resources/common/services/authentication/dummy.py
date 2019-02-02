#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#

# Required:
#
#    pip install python-ntlm
#

from __future__ import print_function
from gnr.lib.services import GnrBaseService

class Main(GnrBaseService):
    """
    ntlm authentication service 
    inside siteconfig.xml

        <services>
            ... other services

            <dummyauth service_type='authentication' resource='dummy' url='www.dummy.com/foo' template='FOO\\%s' case='l' /> 
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
        print('user', user)
        print('url',self.url)
        print('password',password)
        return password=='password'

