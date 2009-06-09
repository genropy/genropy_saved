from gnr.core.gnrbag import Bag
import shutil
import os



def structToPy(tables,path):
    shutil.rmtree(path,True)
    os.makedirs(path)
    header = """# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('%s',  pkey='%s',name_long='%s')
"""
    for tablename,columns,attributes in tables.digest('#k,#v.columns,#a'):
        f = file(os.path.join(path,'%s.py' %tablename),'w')
        pkey = attributes.get('pkey')
        f.write(header %(tablename,pkey,tablename))
        for colName,colAttr in columns.digest('#k,#a'):
            dflt=colAttr.pop('default',None)
            colAttr['name_long']='!!%s'% colName.title()
            x=colAttr.pop('tag',None)
            atlst=[]
            for k,v in colAttr.items():
                atlst.append("%s ='%s'" %(k,v))
            f.write("        tbl.column('%s', %s)  \n" %(colName,', '.join(atlst)))
        f.close()


if __name__=='__main__':
    xmlPath = '/Users/michele/svnrepos/progetti/writers/packages/writers/model/config_db.xml'
    destPath = '/Users/michele/svnrepos/progetti/writers/packages/writers/model'
    struct = Bag(xmlPath)
    structToPy(struct['packages.writers.tables'],destPath)