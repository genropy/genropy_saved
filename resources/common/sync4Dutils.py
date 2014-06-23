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
# 
import os.path
from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import BaseComponent

class Utils4D(BaseComponent):
    def bag4dTableToListDict(self, b):
        result = []
        if 'New' in b:
            b = b['New']
        if 'new' in b:
            b = b['new']
        if b:
            keys = b.keys()
            values = b.values()
            n = len(values[0])
            for v in values:
                if len(v) < n:
                    v.extend([None] * (n - len(v)))
            result = [dict([(k.lower(), values[i][x]) for i, k in enumerate(keys)]) for x in range(n)]
        return result

    def listDictTobag4dTable(self, listdict):
        result = Bag()
        for k in listdict[0].keys():
            result[k] = [d.get(k) for d in listdict]
        return result

class Pkg4D(BaseComponent):
    def _structFix4D(self, struct, path):
        cnv_file = '%s_conv%s' % os.path.splitext(path)
        if os.path.isfile(cnv_file):
            return cnv_file
        cls = struct.__class__
        b = Bag()
        b.fromXml(path, bagcls=cls, empty=cls)

        convdict = {'ci_relation': None,
                    'o_name': None,
                    'o_name_short': None,
                    'o_name_full': None,
                    'o_name_long': None,
                    'many_name_short': None,
                    'many_name_full': None,
                    'many_name_long': None,
                    'eager_relation': None,
                    'len_max': None,
                    'len_min': None,
                    'len_show': None,
                    'relation': None,
                    'comment': None
        }
        #relate_attrs = set(('ci_relation', 'o_name', 'o_name_short', 'o_name_full', 'o_name_long',
        #                    'many_name_short','many_name_full','many_name_long','eager_relation'))

        for pkg in b['packages']:
            for tbl in pkg.value['tables']:
                for col in tbl.value['columns']:
                    newattrs = {}
                    for k, v in col.attr.items():
                        if v is not None:
                            lbl = convdict.get(k, k)
                            if lbl:
                                newattrs[lbl] = v
                    name_long = newattrs.get('name_long')
                    if name_long:
                        if name_long[0] == name_long[0].lower():
                            newattrs['group'] = '_'
                        if name_long.endswith('_I'):
                            name_long = name_long[:-2]
                        elif not 'indexed' in newattrs:
                            newattrs['group'] = '*'
                        if len(name_long) > 2 and name_long[2] == '_':
                            name_long = name_long[3:]
                        newattrs['name_long'] = name_long.replace('_', ' ')

                    if 'len_max' in col.attr:
                        newattrs['size'] = '%s:%s' % (col.attr.get('len_min', '0'), col.attr['len_max'])
                    if 'relation' in col.attr:
                        mode = None
                        if col.attr.get('ci_relation'):
                            mode = 'insensitive'
                        col.value = Bag()
                        col.value.setItem('relation', None, related_column=col.attr['relation'], mode=mode)
                    col.attr = newattrs
        b.toXml(cnv_file,mode4d=True)
        return cnv_file

def gnr4dNetBag (host4D, method, params=None):
    """Call a 4D method via 4D WebService Server and GnrNetBag
    @param host4D: host (and port) of the 4D webserver
    @param method: name of the method to invoke on 4D in the form 4dMethod.$1:$2
    @param params: a Bag containing all needed params: 4D receive it as $3 (string: name of a GnrViVa BLOB)"""
    from SOAPpy import SOAPProxy

    server = SOAPProxy("http://" + host4D + "/4DSOAP",
                       namespace="http://www.4d.com/namespace/default",
                       soapaction="A_WebService#GNT_NetBags_Server",
                       encoding="iso-8859-1",
                       http_proxy="")

    params = params or Bag()
    params['NetBag.Method'] = method
    params['NetBag.Compression'] = 'N'
    params['NetBag.Session'] = ''
    params['NetBag.UserID'] = ''

    #xml = params.toXml(encoding='iso-8859-1')
    xml = unicode(params.toXml(encoding='iso-8859-1',mode4d=True), encoding='iso-8859-1')
    result = server.GNT_NetBags_Server(FourD_Arg1=xml)

    return Bag(result)

if __name__ == '__main__':
    print gnr4dNetBag('localhost:21021', 'CS_Com.Ping')