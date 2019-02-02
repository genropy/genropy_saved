#!/usr/bin/env python
# encoding: utf-8

# --------------------------- GnrWebPage Standard header ---------------------------
from __future__ import print_function
from builtins import object
class GnrCustomWebPage(object):
    skip_connection = True
    def rootPage(self, *args, **kwargs):
        print('ECHO RPC:','\n args',args,'\n kwargs',kwargs)