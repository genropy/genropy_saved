#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
try:
    from docutils.core import publish_string as renderRst
except ImportError:
    def renderRst(*args,**kwargs):
        return '<h1 style="color:red;">Missing docutils</h1><h2>hint: pip install docutils</h2>'


class Main(GnrBaseService):
    def __init__(self, parent=None,theme=None,stylesheet=None,**kwargs):
        self.parent = parent
        self.docutils_kwargs = kwargs
        self.stylesheet = stylesheet or self.stylesheetFromTheme(theme or 'standard')

    def stylesheetFromTheme(self,theme):
        return 'common/services/rst2html/themes/%s.css' %theme

    def __call__(self,source_rst=None,theme=None,stylesheet=None,**kwargs):
        docutils_kwargs = dict(self.docutils_kwargs)
        docutils_kwargs.update(kwargs)
        stylesheet = stylesheet or self.stylesheetFromTheme(theme) if theme else self.stylesheet
        stylesheet = self.parent.getStaticPath('rsrc:%s' %stylesheet)
        settings_overrides = {'stylesheet_path':stylesheet}
        settings_overrides.update(docutils_kwargs)
        try :
            return renderRst(source_rst, writer_name='html',
                              settings_overrides=settings_overrides)
        except Exception,e:
            return str(e)
