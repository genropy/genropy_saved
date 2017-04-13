# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrstring : gnr date implementation
# Copyright (c) : 2004 - 2015 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari 
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


from decimal import Decimal,ROUND_HALF_UP

def decimalRound(value=None,places=2,rounding=None):
    value = value or 0
    if not isinstance(value,Decimal):
        value = floatToDecimal(value)
    return value.quantize(Decimal(str(10**-places)),rounding=rounding or ROUND_HALF_UP)
    
def floatToDecimal(f,places=None,rounding=None):
    if f is None:
        return None
    result = Decimal(str(f))
    if places:
        return decimalRound(result,places=places,rounding=rounding)
    return result