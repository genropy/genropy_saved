#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool

class DbStructure(BaseWebtool):
    def __call__(self, *args, **kwargs):
        args = list(args)
        struct = self.site.db.packages
        packages = self.site.db.packages
        self.content_type = 'text'
        if args:
            pkg = args.pop(0)
            struct = struct['%s.tables' % pkg]
            if args:
                table = args.pop(0)
                struct = struct['%s.relations' % table]
                if args:
                    struct = struct['.'.join(args)]
        if struct:
            return ','.join(struct.keys())

