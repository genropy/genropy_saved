# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import splitAndStrip, fromJson
from gnr.core.gnrbag import DirectoryResolver

class ExplorerManager(BaseComponent):
    py_requires = 'gnrcomponents/htablehandler:HTableHandlerBase,gnrcomponents/palette_manager:PaletteManager'

    def onMain_explorer_manager(self):
        explorers = getattr(self, 'explorers', None)
        if explorers:
            self.expmng_main(explorers)

    def expmng_main(self, explorers):
        explorer_to_create = splitAndStrip(explorers, ',')
        pane = self.pageSource()
        pg = pane.paletteGroup('gnr_explorer', title='!!Explorers', dockTo='pbl_dock')
        for explorer in explorer_to_create:
            explorer_pars = None
            if ' AS ' in explorer:
                explorer, explorer_code = splitAndStrip(explorer, ' AS ')
            elif ' as ' in explorer:
                explorer, explorer_code = splitAndStrip(explorer, ' as ')
            else:
                explorer_code = None
            if ':' in explorer:
                explorer, explorer_pars = explorer.split(':', 1)
            if not explorer_code:
                explorer_code = explorer.replace('.', '_').replace('@', '_')
            handler = getattr(self, 'explorer_' + explorer, None)
            if handler:
                data, metadata = handler(explorer_pars, explorer_code=explorer_code)
            else:
                if explorer_pars:
                    explorer_pars = fromJson(explorer_pars.replace("'", '"'))
                    kw = dict()
                    for k, v in explorer_pars.items():
                        kw[str(k)] = v
                else:
                    kw = dict()
                data, metadata = self.expmng_htableExplorer(explorer_table=explorer, **kw)
            pg.paletteTree(explorer_code, title=metadata.pop('title', explorer), data=data, **metadata)


    def expmng_htableExplorer(self, explorer_table=None, **kwargs):
        tblobj = self.db.table(explorer_table)
        related_field = None
        related_table = None
        if '@' in explorer_table:
            pkg, related_table, related_field = explorer_table.split('.')
            related_table = '%s.%s' % (pkg, related_table)
            related_table_obj = self.db.table(related_table)
            explorer_table = related_table_obj.column(related_field).parent.fullname
        return self.ht_treeDataStore(table=explorer_table,
                                     related_table=related_table,
                                     relation_path=related_field,
                                     rootcaption=tblobj.name_plural, **kwargs), dict(title=tblobj.name_long)


    def explorer_directory(self, path=None):
        return DirectoryResolver(path or '/')(), dict(title='Directory: %s' % path)

    def tableTreeResolver(self, table=None, where=None, group_by=None, **kwargs):
        tblobj = self.db.table(table)
        columns = [x for x in group_by if not callable(x)]
        selection = tblobj.query(where=where, columns=','.join(columns), **kwargs).selection()
        explorer_id = self.getUuid()
        freeze_path = self.site.getStaticPath('page:explorers', explorer_id)
        totalizeBag = selection.totalize(group_by=group_by, collectIdx=False)
        return self.lazyBag(totalizeBag, name=explorer_id, location='page:explorer')

    def tableTreeExplorer(self, pane, table=None, where=None, group_by=None, explorer_code=None, **kwargs):
        data = self.tableTreeResolver(table=table, where=where, group_by=group_by, **kwargs)()
        explorer_code = explorer_code or table.replace('.', '_')
        pane.paletteTree(explorer_code, data=data)
        