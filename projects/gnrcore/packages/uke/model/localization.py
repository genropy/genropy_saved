# encoding: utf-8
from builtins import object
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('localization',pkey='id',name_long='!!Localization',
                      name_plural='!!Localization')
        self.sysFields(tbl)
        tbl.column('package_identifier' ,group='_',name_long='!!Package identifier').relation('package.package_identifier',mode='foreignkey',onDelete='raise')
        tbl.column('localization_key',name_long='!!Key')
        tbl.column('localization_values',dtype='X',name_long='!!Localization Values')


    def importLocalizationFile(self,package_identifier=None,filepath=None):
        localization_bag = Bag(filepath)
        self.deleteSelection(where='$package_identifier=:package_identifier',package_identifier=package_identifier)
        for localization_key,attributes in localization_bag.digest('#a._key,#a'):
            locrecord = dict(localization_key=localization_key or attributes.get('en'),package_identifier=package_identifier)
            localization_values = Bag()
            if attributes.get('it'):
                localization_values['it'] = attributes.get('it')
                localization_values['en'] = attributes.get('en') or localization_key
            locrecord['localization_values'] = localization_values
            self.insert(locrecord)



    def getProjectLocalizations(self,project_code=None):
        result = Bag()
        rows = self.query(where='@package_identifier.project_code=:project_code',project_code=project_code,
                                columns='$localization_key,$localization_values,$package_identifier',order_by='$package_identifier,$localization_key').fetch()

        for r in rows:
            localization_values = Bag(r['localization_values'])
            localization_values['_package_identifier'] = r['package_identifier']
            localization_values['_key'] = r['localization_key']
            result[r['pkey']] = localization_values
        return result


    @public_method
    def savePackageLocalizationBag(self,package_identifier=None,localizationBag=None):
        pass