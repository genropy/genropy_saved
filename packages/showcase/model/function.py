# encoding: utf-8

class Table(object):
    """ """
    def config_db(self, pkg):
        """invc.customer"""
        tbl =  pkg.table('function',  pkey='id',name_plural = '!!Functions',
                         name_long=u'!!Functions', rowcaption='name')
        self.sysFields(tbl)
        tbl.column('name', size=':40',name_long = '!!Name')
        tbl.column('doc', name_long = '!!Documentation')