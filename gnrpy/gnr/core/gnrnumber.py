# -*- coding: utf-8 -*-
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


def calculateMultiPerc(multiperc):
    if not multiperc:
        return
    multiperc = multiperc.split('+')
    t = 100
    while multiperc:
        s = Decimal(multiperc.pop(0))
        t -= t*s/100
    return decimalRound(100-t)

def partitionTotals(totals,quotes,places=2,rounding=None):
    if not isinstance(totals,list):
        totals = [totals]
    totals = map(Decimal,totals)
    quotes = map(Decimal,quotes)
    residues = list(totals)
    tot_quotes = sum(quotes)
    n_quotes = len(quotes)
    for idx,q in enumerate(quotes):
        if idx+1==n_quotes:
            yield (decimalRound(r,places=places,rounding=rounding) for r in residues)
            return
        result = []
        for j,tot in enumerate(totals):
            tot = decimalRound(tot*q/tot_quotes)
            result.append(tot)
            residues[j] = residues[j]-tot
        yield result
