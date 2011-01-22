#!/usr/bin/python
# -*- coding: UTF-8 -*-
import codecs
import logging
import os
import yaml

from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag
from gnr.core.gnrlog import enable_colored_logging
from gnr.devel.commands import command, argument
from gnr.sql.gnrsql_exceptions import GnrSqlMissingTable

DEFAULT_FILENAME = 'pkg_table.yaml'

@command('yaml', 'Load/Save records from/to YAML files')
@argument('instance', metavar="INSTANCE", type=GnrApp, help="Genro instance")
@argument('operation', choices=['i', 'e', 'import', 'export'])
@argument('pkg_table', metavar='PKG.TABLE', help="package and table to operate on")
@argument('where', '-q', '--where', metavar='GNRSQL', help="Genro SQL query, used only when exporting records")
@argument('filename', '-f', '--filename', metavar="FILENAME.YAML", default=DEFAULT_FILENAME, help="Filename, defaults to pkg_table.yaml")
@argument('replace', '-r', '--replace', default=False, help="on import, INSERT or UPDATE records instead of just INSERT records")
def main(instance, operation, pkg_table, where=None, filename=None, replace=False, verbose=False):
    logging_level = logging.INFO if verbose else logging.WARNING
    enable_colored_logging(level=logging_level)
    try:
        tbl = instance.db.table(pkg_table)
    except GnrSqlMissingTable, e:
        logging.error(e)
        return

    if filename is DEFAULT_FILENAME or filename is None:
        filename = pkg_table.replace('.','_',1) + '.yaml'

    if os.path.exists(filename):
        data = Bag(yaml.load(codecs.open(filename,'rt','utf-8')))
    else:
        data = Bag()

    if operation in ('i','import'):
        import_record = tbl.insertOrUpdate if replace else tbl.insert
        try:
            for rec in data[pkg_table].values():
                import_record(rec)
            instance.db.dbcommit()
        except Exception, e:
            instance.db.rollback()
            logging.exception(e)

    if operation in ('e','export'):
        qry = tbl.query(where=where)
        logging.info('%d records found', qry.count())

        records = data.get(pkg_table) or Bag()
        for n, rec in enumerate(qry.fetch()):
            r = dict([(k,v) for k,v in rec.items() if not k.startswith('__')])
            records.addItem('r_%d' % n, Bag(r))

        data.setItem(pkg_table, records)

        yaml.dump(data.asDictDeeply(), codecs.open(filename, 'wt','utf-8'))

if __name__ == '__main__':
    main.run()