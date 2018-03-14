#!/usr/bin/env python
# encoding: utf-8

# --------------------------- GnrWebPage Standard header ---------------------------
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import NetBag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'

    @public_method
    def makeapp(self,name=None,**kwargs):
        platform = {'windows':'windows','linux':'linux','mac':'osx'}.get(self.connection.user_device.split(':')[0])
        if not platform:
            return
        service_url = 'http://services.genropy.net/electron/electron'
        electron_pars = self.site.config.getAttr('electron') or {}
        name = electron_pars.get('name') or self.site.site_name
        url = self.request.host_url
        result = NetBag(service_url,'make_electron' , name=name, platform=platform,app_url=url)
        dlurl = 'http://services.genropy.net%s' %result()['result']
        self.forced_mimetype='text/html'
        return self.plain_redirect(dlurl)
        #self.setInClientData('gnr.downloadurl',dlurl)

    def plain_redirect(self,url):
        return """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
        <html lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <script>
                    window.open('%s');
            </script>
            </head>
            <body>
            </body>
            </html>""" %url