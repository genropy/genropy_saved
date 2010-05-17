# encoding: utf-8

class Table(object):
    """ """
    def config_db(self, pkg):
        """Funzioni"""
        tbl =  pkg.table('function',  pkey='id',name_plural = '!!Functions',
                         name_long=u'!!Functions', rowcaption='name')
        self.sysFields(tbl)
        tbl.column('path', size=':100',name_long = '!!Name',unique=True)#function/widget path
        tbl.column('name', size=':40',name_long = '!!Name')#function/widget name
        tbl.column('doc', name_long = '!!Documentation')