# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrlang : support funtions
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
from os import sep

def checklist(name=None, pkg=None, code=None, subcode=None,doc_url=None,**kwargs):
    code = '%03i' % (code or 0)
    subcode = '%02i' % (subcode or 0)
    def decore(func):
        modulepkg = func.__code__.co_filename.split('packages%s' %sep)[1].split(sep)[0]
        checklist_dict = dict(pkg=pkg or modulepkg, name=name, subcode=subcode, code=code, doc_url=doc_url)
        def newFunc(tbl):
            description = func.__doc__
            pars = dict(checklist_dict)
            pars['pkg'] = pars['pkg']
            pars['name'] = pars['name'] or func.__name__.replace('_',' ').capitalize()
            return tbl.newrecord(description=description,**pars)
       
        syscode = '_'.join([pkg or modulepkg, code, subcode])
        newFunc.instance_mixin_as = 'sysRecord_%s' % syscode
        newFunc.mandatory = True
        return newFunc
    return decore

