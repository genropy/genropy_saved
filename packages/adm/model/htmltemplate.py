# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('htmltemplate',  pkey='id',name_long='!!Html Template',
                      name_plural='!!Html Template')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name',validate_nodup=True,
                    validate_notnull=True,validate_notnull_error='!!Name is mandatory',
                    validate_nodup_error='!!This name is already taken')
        tbl.column('username',name_long='!!Username')
        tbl.column('version',name_long='!!Version')
        tbl.column('data',dtype='X',name_long='!!Data',_sendback=True)
    
    def getTemplate(self,name):
        templatelist = name.split(',')
        f = self.query(where='$name IN :names',names=templatelist,columns='name,version,data').fetchAsDict(key='name')
        templatebase = Bag(f[templatelist[0]]['data'])
        if len(templatelist)>1:
            pass
        return templatebase            
    