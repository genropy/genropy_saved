#-*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
import shutil
import os
from gnr.app.gnrdeploy import PackageMaker

def structToPyFull(sourcepath, destpath):
    if not os.path.isdir(destpath):
        os.mkdir(destpath)
    fullstruct = Bag(sourcepath)
    packages = fullstruct['packages']
    for k,v in packages.items():
        if not v: continue
        package_dir_path = os.path.join(destpath,k)
        package_maker = PackageMaker(k, base_path=destpath)
        package_maker.do()
        model_path = os.path.join(package_dir_path,'model')
        structToPy(v['tables'],model_path,pkg=k)

def structToPy(tables, path,pkg=None):
    #shutil.rmtree(path,True)
    #os.makedirs(path)
    header = """# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('%s', pkey='%s', name_long='%s')
"""
    for tablename, columns, attributes in tables.digest('#k,#v.columns,#a'):
        if pkg and tablename.startswith('%s_' %pkg):
            tablename = tablename[len(pkg)+1:]
        f = file(os.path.join(path, '%s.py' % tablename), 'w')
        pkey = attributes.get('pkey')
        f.write(header % (tablename, pkey, tablename))
        for colName, colAttr in columns.digest('#k,#a'):
            dflt = colAttr.pop('default', None)
            colAttr['name_long'] = '!!%s' % colName.title()
            x = colAttr.pop('tag', None)
            atlst = []
            for k, v in colAttr.items():
                atlst.append("%s ='%s'" % (k, v))
            f.write("        tbl.column('%s', %s)  \n" % (colName, ', '.join(atlst)))
        f.close()
        
if __name__ == '__main__':
    xmlPath = '/Users/fporcari/Desktop/rossetti.xml'
    destPath = '/Users/fporcari/Desktop/rossetti_packages'
    structToPyFull(xmlPath, destPath)