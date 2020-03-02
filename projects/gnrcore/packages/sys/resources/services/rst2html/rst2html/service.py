#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from builtins import str
from gnr.lib.services import GnrBaseService
import re
try:
    from docutils.core import publish_string as renderRst
except ImportError:
    def renderRst(*args,**kwargs):
        return '<h1 style="color:red;">Missing docutils</h1><h2>hint: pip install docutils</h2>'


class Main(GnrBaseService):
    def __init__(self, parent=None,theme=None,stylesheet=None,**kwargs):
        self.parent = parent
        self.docutils_kwargs = kwargs
        self.theme = theme
        self.stylesheet = stylesheet
        self.content_class = 'rst-content'

    def styleSheetFromTheme(self,theme):
        if not theme.endswith('.css'):
            theme = '%s.css' %theme
        return self.parent.dummyPage.getResourcePath('services/rst2html/themes/%s' %theme)


    def __call__(self,source_rst=None,theme=None,stylesheet=None,scripts=None,**kwargs):
        docutils_kwargs = dict(self.docutils_kwargs)
        docutils_kwargs.update(kwargs)
        #stylesheet = stylesheet or self.stylesheetFromTheme(theme) if theme else self.stylesheet
        if not stylesheet:
            if theme:
                stylesheet = self.styleSheetFromTheme(theme)
            elif self.stylesheet:
                stylesheet = self.stylesheet
            else:
                stylesheet = self.styleSheetFromTheme(self.theme or 'readthedocs')
        settings_overrides = {'stylesheet_path':stylesheet}
        settings_overrides.update(docutils_kwargs)
        if not source_rst:
            return
        try :
            source_rst = source_rst.replace('[tr-off]','').replace('[tr-on]','')
            result = renderRst(source_rst, writer_name='html',
                              settings_overrides=settings_overrides
                              ).decode()
            if result:
                if scripts:
                    l = []
                    for s in scripts:
                        l.append('<script type="text/javascript" src="%s"></script>' %s)
                    z = '\n'.join(l)
                    result = result.replace('</head>','%s\n</head>' %z)
                result = re.sub(r'<a(.*?)(href\=\"javascript:)(.*?)>(.*?)</a>',r'<span \1 onclick="\3>\4</span>',result)
                #result = result.replace('href="javascript:','onclick="')

            #result = result.replace('class="document"','class="rst-content"')
            return result
        except Exception as e:
           return str(e)