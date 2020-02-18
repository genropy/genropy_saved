# encoding: utf-8
from gnr.core.gnrdecorator import metadata


class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('data_type',pkey='code',name_long='Data type', name_plural='Data types',caption_field='code',lookup=True)
        tbl.column('code', size=':10',name_long='Code')
        tbl.column('description', name_long='Description')


    @metadata(mandatory=True)
    def sysRecord_N(self):
        return self.newrecord(code='N',description='Number')

    @metadata(mandatory=True)
    def sysRecord_P(self):
        return self.newrecord(code='I',description='Interger')

    @metadata(mandatory=True)
    def sysRecord_L(self):
        return self.newrecord(code='L',description='Long integer')

    @metadata(mandatory=True)
    def sysRecord_T(self):
        return self.newrecord(code='T',description='Text')

    @metadata(mandatory=True)
    def sysRecord_V(self):
        return self.newrecord(code='X',description='Bag')
