#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        ac = root.accordionContainer(height='100%')
        #ac= lc.tabContainer(height='100%')
        #
        packages=self.db.packages
        #
        for pname,pobj in packages.items():
            tables=pobj.tables
            pane=ac.accordionPane(title=pname)
        
            if tables:
                for tname,tobj in tables.items():
                    t=pane.table()
                    t.caption(tname, background_color='gray')
                    head=t.thead(background_color='whitesmoke').tr()
                    head.th('name')
                    head.th('type')
                    head.th('size')
                    head.th('long name')
                    head.th('related col')
                    head.td('mode')
                    for cobj in tobj.columns.values():
                        row=t.tr()
                        row.td(cobj.name)
                        row.td(cobj.attributes.get('dtype',''))
                        row.td(cobj.attributes.get('size',''))
                        row.td(cobj.name_long)
                        rc=cobj.relatedColumn()
                        if rc:
                            row.td(cobj.relatedColumn().fullname)
                        else:
                            row.td('a')
                        #row.td(cobj.column_relation.attributes.get('mode',''))
                        
                    
            
        
        
