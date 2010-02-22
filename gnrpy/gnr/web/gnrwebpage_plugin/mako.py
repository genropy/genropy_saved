#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage_plugin.gnrbaseplugin import GnrBasePlugin
from mako.lookup import TemplateLookup
import itertools
import os
AUTH_OK=0
AUTH_NOT_LOGGED=1
AUTH_FORBIDDEN=-1

class Plugin(GnrBasePlugin):
    
    def __call__(self, path=None, dojo_theme=None, striped='odd_row,even_row', pdf=False, **kwargs):
        page = self.page
        dojo_theme = dojo_theme or getattr(self.page, 'dojo_theme', None) or 'tundra'
        auth = page._checkAuth()
        if auth != AUTH_OK:
            page.raiseUnauthorized()
        if striped:
            kwargs['striped']=itertools.cycle(striped.split(','))
        tpldirectories=[os.path.dirname(path), page.parentdirpath]+page.resourceDirs+[page.site.gnr_static_path(page.gnrjsversion,'tpl')]
        lookup=TemplateLookup(directories=tpldirectories,
                              output_encoding='utf-8', encoding_errors='replace')                      
        template = lookup.get_template(os.path.basename(path))
        css_dojo = getattr(page, '_css_dojo_d%s' % page.dojoversion)()
        
        _resources = page.site.resources.keys()
        _resources.reverse()
        dojolib = page.site.dojo_static_url(page.dojoversion,'dojo','dojo','dojo.js')
        gnrModulePath = page.site.gnr_static_url(page.gnrjsversion)
        page.js_requires.append(page.pagename)
        js_requires = [x for x in [page.getResourceUri(r,'js') for r in page.js_requires] if x]
        if os.path.isfile(page.resolvePath('%s.js' % page.pagename)):
            js_requires.append('%s.js' % page.pagename)
        css_requires, css_media_requires = page.get_css_path()
        output = template.render(mainpage=page,
                               css_genro = page.get_css_genro(),
                               css_requires = css_requires , js_requires=page.js_requires,
                               css_media_requires = css_media_requires,
                               css_dojo = [page.site.dojo_static_url(page.dojoversion,'dojo',f) for f in css_dojo],
                               dojolib=dojolib,
                               djConfig="parseOnLoad: false, isDebug: %s, locale: '%s'" % (page.isDeveloper() and 'true' or 'false',page.locale),
                               gnrModulePath=gnrModulePath, **kwargs)
        if not pdf:
            page.response.content_type = 'text/html'
            return output
        else:
            from gnr.pdf.wk2pdf import WK2pdf
            page.response.content_type = 'application/pdf'
            tmp_name = page.temporaryDocument('tmp.pdf')
            if page.request.query_string:
                query_string = '&'.join([q for q in page.query_string.split('&') if not 'pdf' in q.lower()])
                url = '%s?%s'%(page.path_url,query_string)
            else:
                url = page.path_url
            wkprinter = WK2pdf(url,tmp_name)
            wkprinter.run()
            wkprinter.exec_()
            page.response.add_header("Content-Disposition",str("%s; filename=%s.pdf"%('inline',page.path_url.split('/')[-1]+'.pdf')))
            tmp_file = open(tmp_name)
            tmp_content = tmp_file.read()
            tmp_file.close()
            return tmp_content
