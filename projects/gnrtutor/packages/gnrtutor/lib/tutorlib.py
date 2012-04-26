# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy gnrtutor - see LICENSE for details
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


def example(code,height=None,description=None,**kwargs):
    def decore(func):
        kw=dict(kwargs)
        kw['height']=height or 200
        kw['description']=description or '...not description...'
        kw['code']=code or 99
        for k, v in kw.items():
            setattr(func, 'example_%s' %k, v)
        setattr(func,'isExample',True)
        return func 
    return decore