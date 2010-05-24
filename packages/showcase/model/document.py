# encoding: utf-8

class Table(object):
    """ """
    def config_db(self, pkg):
        """document"""
        tbl =  pkg.table('document',  pkey='id',name_plural = '!!Documents',
                         name_long=u'!!Documents', rowcaption='name')
        self.sysFields(tbl)
        tbl.column('path', size=':100',name_long = '!!Name',unique=True)#function/widget path
        tbl.column('name', size=':40',name_long = '!!Name')#function/widget name
        tbl.column('data', name_long = '!!Documentation')