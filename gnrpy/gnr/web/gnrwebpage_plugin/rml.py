#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  rml.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage_plugin.gnrbaseplugin import GnrBasePlugin
from mako.lookup import TemplateLookup


class Plugin(GnrBasePlugin):
    def __call__(self, path, inline=False, **kwargs):
        auth = self._checkAuth()
        if auth != AUTH_OK:
            self.raiseUnauthorized()
        tpldirectories = [os.path.dirname(path), self.parentdirpath] + self.resourceDirs + [
                self.resolvePath('gnrjs', 'gnr_d%s' % self.dojo_version, 'tpl', folder='*lib')]
        lookup = TemplateLookup(directories=tpldirectories,
                                output_encoding='utf-8', encoding_errors='replace')
        template = lookup.get_template(os.path.basename(path))
        self.response.content_type = 'application/pdf'
        filename = os.path.split(path)[-1].split('.')[0]
        inline_attr = (inline and 'inline') or 'attachment'
        self.response.add_header("Content-Disposition", str("%s; filename=%s.pdf" % (inline_attr, filename)))
        import cStringIO
        from lxml import etree
        from z3c.rml import document

        tmp = template.render(mainpage=self, **kwargs)
        tmp = tmp.replace('&', '&amp;')
        root = etree.fromstring(tmp)
        doc = document.Document(root)
        output = cStringIO.StringIO()
        doc.process(output)
        output.seek(0)
        return output.read()