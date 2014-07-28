#!/usr/bin/env python
# encoding: utf-8

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    skip_connection = True
    def rootPage(self, *args, **kwargs):
        print 'ECHO RPC:','\n args',args,'\n kwargs',kwargs